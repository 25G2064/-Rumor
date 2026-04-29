import random

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

# 通路を掘る（L字）
def dig_corridor(x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon[y1][x] = TILES["floor"]
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon[y][x2] = TILES["floor"]

# メイン通路
sx, sy = 2, 2
gx, gy = WIDTH - 3, HEIGHT - 3
dig_corridor(sx, sy, gx, sy)
dig_corridor(gx, sy, gx, gy)

main_path = [(sy, x) for x in range(sx, gx + 1)] + [(y, gx) for y in range(sy + 1, gy + 1)]
branches = []

# 枝分かれ通路
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

# 部屋の重なりチェック
def is_overlapping(rx, ry, w, h, existing_rooms):
    for erx, ery, ew, eh in existing_rooms:
        if (rx < erx + ew and rx + w > erx and ry < ery + eh and ry + h > ery):
            return True
    return False

# 部屋を通路に接続（成功判定付き）
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

# 部屋生成（接続できた部屋のみ記録）
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

# スタート・ゴールを接続済みの部屋に配置
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

# スタートとゴールを通路で接続（壁を上書きしてでも）
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

# 部屋に敵・罠・宝物を配置
for rx, ry, w, h in rooms:
    for _ in range(random.randint(1, 5)):
        x = rx + random.randint(0, w - 1)
        y = ry + random.randint(0, h - 1)
        if dungeon[y][x] == TILES["room"]:
            dungeon[y][x] = random.choice([TILES["enemy"], TILES["trap"], TILES["treasure"]])

# 孤立通路の削除（重要地点保護）
def prune_dead_ends_protected():
    important = set()
    important.add((sy, sx))
    important.add((gy, gx))
    for rx, ry, w, h in rooms:
        cx, cy = rx + w // 2, ry + h // 2
        important.add((cy, cx))

    changed = True
    while changed:
        changed = False
        for y in range(1, HEIGHT - 1):
            for x in range(1, WIDTH - 1):
                if (y, x) in important:
                    continue
                if dungeon[y][x] != TILES["floor"]:
                    continue
                count = 0
                for dy, dx in directions:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                        if dungeon[ny][nx] in [TILES["floor"], TILES["room"], TILES["start"], TILES["goal"]]:
                            count += 1
                if count <= 1:
                    dungeon[y][x] = TILES["wall"]
                    changed = True

prune_dead_ends_protected()

# 外枠を壁にする
for x in range(WIDTH):
    dungeon[0][x] = TILES["wall"]
    dungeon[HEIGHT - 1][x] = TILES["wall"]
for y in range(HEIGHT):
    dungeon[y][0] = TILES["wall"]
    dungeon[y][WIDTH - 1] = TILES["wall"]

# スタート・ゴールを配置（最後に）
dungeon[sy][sx] = TILES["start"]
dungeon[gy][gx] = TILES["goal"]

# 表示
for row in dungeon:
    print("".join(row))