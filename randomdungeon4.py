import random
import os

# ダンジョンサイズとタイル定義
WIDTH = random.randint(24, 100)
HEIGHT = random.randint(24, 100)
TILES = {
    "wall": "＃",
    "floor": "　",
    "room": "　",
    "enemy": "敵",
    "treasure": "宝",
    "trap": "罠",
    "start": "始",
    "goal": "終"
}

dungeon = [[TILES["wall"] for _ in range(WIDTH)] for _ in range(HEIGHT)]
directions = [(1,0), (-1,0), (0,1), (0,-1)]

def dig_corridor(x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon[y1][x] = TILES["floor"]
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon[y][x2] = TILES["floor"]

# メイン通路生成
sx, sy = 2, 2
gx, gy = WIDTH - 3, HEIGHT - 3
dig_corridor(sx, sy, gx, sy)
dig_corridor(gx, sy, gx, gy)

main_path = [(sy, x) for x in range(sx, gx + 1)] + [(y, gx) for y in range(sy + 1, gy + 1)]
branches = []

# 枝道生成
for _ in range(200):
    y, x = random.choice(main_path)
    dx, dy = random.choice(directions)
    length = random.randint(5, 12)
    for i in range(1, length + 1):
        nx, ny = x + dx*i, y + dy*i
        if 1 <= nx < WIDTH - 1 and 1 <= ny < HEIGHT - 1:
            dungeon[ny][nx] = TILES["floor"]
            branches.append((ny, nx))

floor_tiles = set(main_path + branches)

def is_overlapping(rx, ry, w, h, existing_rooms):
    for erx, ery, ew, eh in existing_rooms:
        if (rx < erx + ew and rx + w > erx and ry < ery + eh and ry + h > ery):
            return True
    return False

def connect_room_to_nearest_floor(cx, cy):
    min_dist = float('inf')
    target = None
    for fy, fx in floor_tiles:
        dist = abs(cx - fx) + abs(cy - fy)
        if dist < min_dist:
            min_dist = dist
            target = (fx, fy)
    if target:
        tx, ty = target
        for x in range(min(cx, tx), max(cx, tx) + 1):
            dungeon[cy][x] = TILES["floor"]
            floor_tiles.add((cy, x))
        for y in range(min(cy, ty), max(cy, ty) + 1):
            dungeon[y][tx] = TILES["floor"]
            floor_tiles.add((y, tx))
        return True
    return False

# 部屋生成
rooms = []
connected_rooms = []

for _ in range(60):
    x = random.randint(5, WIDTH - 6)
    y = random.randint(5, HEIGHT - 6)
    w, h = random.randint(3, 5), random.randint(3, 5)
    rx, ry = x - w // 2, y - h // 2
    if 1 <= rx < WIDTH - w and 1 <= ry < HEIGHT - h:
        if not is_overlapping(rx, ry, w, h, rooms):
            valid = True
            for i in range(h):
                for j in range(w):
                    if dungeon[ry + i][rx + j] != TILES["wall"]:
                        valid = False
                        break
            if valid:
                for i in range(h):
                    for j in range(w):
                        dungeon[ry + i][rx + j] = TILES["room"]
                cx, cy = rx + w // 2, ry + h // 2
                if connect_room_to_nearest_floor(cx, cy):
                    rooms.append((rx, ry, w, h))
                    connected_rooms.append((rx, ry, w, h))
                else:
                    for i in range(h):
                        for j in range(w):
                            dungeon[ry + i][rx + j] = TILES["wall"]

# スタートとゴール設定
start_room = random.choice(connected_rooms)
goal_room = random.choice(connected_rooms)
while goal_room == start_room:
    goal_room = random.choice(connected_rooms)

rx, ry, w, h = start_room
sx = rx + random.randint(0, w - 1)
sy = ry + random.randint(0, h - 1)

rx, ry, w, h = goal_room
gx = rx + random.randint(0, w - 1)
gy = ry + random.randint(0, h - 1)

def connect_start_to_goal(sx, sy, gx, gy):
    for x in range(min(sx, gx), max(sx, gx) + 1):
        if dungeon[sy][x] == TILES["wall"]:
            dungeon[sy][x] = TILES["floor"]
        floor_tiles.add((sy, x))
    for y in range(min(sy, gy), max(sy, gy) + 1):
        if dungeon[y][gx] == TILES["wall"]:
            dungeon[y][gx] = TILES["floor"]
        floor_tiles.add((y, gx))

connect_start_to_goal(sx, sy, gx, gy)

# 特別部屋の生成
for rx, ry, w, h in rooms:
    roll = random.random()
    if roll < 0.03:
        for i in range(h):
            for j in range(w):
                if dungeon[ry + i][rx + j] == TILES["room"]:
                    dungeon[ry + i][rx + j] = TILES["enemy"]
    elif roll < 0.06:
        for i in range(h):
            for j in range(w):
                if dungeon[ry + i][rx + j] == TILES["room"]:
                    dungeon[ry + i][rx + j] = TILES["treasure"]
    elif roll < 0.09:
        for i in range(h):
            for j in range(w):
                if dungeon[ry + i][rx + j] == TILES["room"]:
                    dungeon[ry + i][rx + j] = TILES["trap"]
    else:
        for _ in range(random.randint(1, 5)):
            x = rx + random.randint(0, w - 1)
            y = ry + random.randint(0, h - 1)
            if dungeon[y][x] == TILES["room"]:
                dungeon[y][x] = random.choice([TILES["enemy"], TILES["trap"], TILES["treasure"]])

# デッドエンド除去
def prune_dead_ends_protected():
    important = {(sy, sx), (gy, gx)}
    for rx, ry, w, h in rooms:
        cx, cy = rx + w // 2, ry + h // 2
        important.add((cy, cx))

    changed = True
    while changed:
        changed = False
        for y in range(1, HEIGHT - 1):
            for x in range(1, WIDTH - 1):
                if (y, x) in important or dungeon[y][x] != TILES["floor"]:
                    continue
                count = sum(
                    dungeon[y + dy][x + dx] in [TILES["floor"], TILES["room"], TILES["start"], TILES["goal"]]
                    for dy, dx in directions
                    if 0 <= y + dy < HEIGHT and 0 <= x + dx < WIDTH
                )
                if count <= 1:
                    dungeon[y][x] = TILES["wall"]
                    changed = True

prune_dead_ends_protected()

# 外周壁
for x in range(WIDTH):
    dungeon[0][x] = dungeon[HEIGHT - 1][x] = TILES["wall"]
for y in range(HEIGHT):
    dungeon[y][0] = dungeon[y][WIDTH - 1] = TILES["wall"]

dungeon[sy][sx] = TILES["start"]
dungeon[gy][gx] = TILES["goal"]

# プレイヤー初期位置と宝カウント
player_x, player_y = sx, sy
treasure_count = 0

def render_dungeon():
    os.system('cls' if os.name == 'nt' else 'clear')
    for y in range(HEIGHT):
        row = ""
        for x in range(WIDTH):
            row += "自" if (x, y) == (player_x, player_y) else dungeon[y][x]
        print(row)

def can_move_to(x, y):
    return (
        0 <= x < WIDTH and
        0 <= y < HEIGHT and
        dungeon[y][x] in [TILES["floor"], TILES["room"], TILES["start"], TILES["goal"], TILES["treasure"]]
    )

# ゲーム開始
render_dungeon()
print("WASDで移動、Qで終了")

while True:
    move = input("移動: ").lower()
    if move == "q":
        print("ゲーム終了")
        break

    dx, dy = 0, 0
    if move == "w":
        dy = -1
    elif move == "s":
        dy = 1
    elif move == "a":
        dx = -1
    elif move == "d":
        dx = 1
    else:
        print("無効な入力")
        continue

    new_x = player_x + dx
    new_y = player_y + dy

    if can_move_to(new_x, new_y):
        tile = dungeon[new_y][new_x]

        # 宝を拾う処理
        if tile == TILES["treasure"]:
            treasure_count += 1
            print(f"✨ 宝を拾った！現在の宝数: {treasure_count}")
            dungeon[new_y][new_x] = TILES["floor"]

        # ゴールに到達
        if tile == TILES["goal"]:
            render_dungeon()
            print("🎉 ゴールに到達！ダンジョンをクリアしました！")
            print(f"💎 拾った宝の数: {treasure_count}")
            break

        player_x, player_y = new_x, new_y
    else:
        print("その方向には進めません")

    render_dungeon()