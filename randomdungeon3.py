import random

WIDTH = 100
HEIGHT = 100
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

def is_overlapping(x, y, w, h, rooms):
    for r in rooms:
        rx, ry, rw, rh = r["x"], r["y"], r["w"], r["h"]
        if (x < rx + rw and x + w > rx and y < ry + rh and y + h > ry):
            return True
    return False

def dig_line(x1, y1, x2, y2):
    if x1 == x2:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            dungeon[y][x1] = TILES["floor"]
    elif y1 == y2:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            dungeon[y1][x] = TILES["floor"]

def carve_circle(cx, cy, r):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if 0 < x < WIDTH - 1 and 0 < y < HEIGHT - 1:
                if (x - cx)**2 + (y - cy)**2 <= r**2:
                    dungeon[y][x] = TILES["room"]

def connect_rooms_limited(room_a, room_b, max_connections=4):
    if room_a["connections"] >= max_connections or room_b["connections"] >= max_connections:
        return False
    ax, ay = room_a["center"]
    bx, by = room_b["center"]
    if random.random() < 0.5:
        dig_line(ax, ay, bx, ay)
        dig_line(bx, ay, bx, by)
    else:
        dig_line(ax, ay, ax, by)
        dig_line(ax, by, bx, by)
    room_a["connections"] += 1
    room_b["connections"] += 1
    return True

# 部屋生成（四角＋丸型）
rooms = []
for _ in range(60):
    shape = "circle" if random.random() < 0.15 else "rect"
    if shape == "circle":
        r = random.randint(4, 6)
        cx = random.randint(r + 1, WIDTH - r - 2)
        cy = random.randint(r + 1, HEIGHT - r - 2)
        if not is_overlapping(cx - r, cy - r, r * 2 + 1, r * 2 + 1, rooms):
            carve_circle(cx, cy, r)
            room = {
                "shape": "circle",
                "x": cx - r,
                "y": cy - r,
                "w": r * 2 + 1,
                "h": r * 2 + 1,
                "center": (cx, cy),
                "connections": 0
            }
            rooms.append(room)
    else:
        w, h = random.randint(3, 6), random.randint(3, 6)
        x = random.randint(1, WIDTH - w - 2)
        y = random.randint(1, HEIGHT - h - 2)
        if not is_overlapping(x, y, w, h, rooms):
            for i in range(h):
                for j in range(w):
                    dungeon[y + i][x + j] = TILES["room"]
            room = {
                "shape": "rect",
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "center": (x + w // 2, y + h // 2),
                "connections": 0
            }
            rooms.append(room)

# 部屋接続（ランダム探索）
connected = set()
unconnected = set(range(len(rooms)))
current = random.choice(list(unconnected))
connected.add(current)
unconnected.remove(current)

while unconnected:
    target = random.choice(list(unconnected))
    nearest = min(connected, key=lambda i: (
        abs(rooms[i]["center"][0] - rooms[target]["center"][0]) +
        abs(rooms[i]["center"][1] - rooms[target]["center"][1])
    ))
    if connect_rooms_limited(rooms[nearest], rooms[target]):
        connected.add(target)
        unconnected.remove(target)

# スタート・ゴールを接続済みの部屋から選ぶ
start_room = random.choice([r for r in rooms if r["connections"] > 0])
goal_room = random.choice([r for r in rooms if r["connections"] > 0])
while goal_room == start_room:
    goal_room = random.choice([r for r in rooms if r["connections"] > 0])

sx, sy = start_room["center"]
gx, gy = goal_room["center"]

# スタートとゴールを通路で接続
dig_line(sx, sy, gx, sy)
dig_line(gx, sy, gx, gy)

# 特別部屋の生成
for room in rooms:
    rx, ry, w, h = room["x"], room["y"], room["w"], room["h"]
    roll = random.random()
    if roll < 0.03:
        for i in range(h):
            for j in range(w):
                dungeon[ry + i][rx + j] = TILES["enemy"]
    elif roll < 0.06:
        for i in range(h):
            for j in range(w):
                dungeon[ry + i][rx + j] = TILES["treasure"]
    elif roll < 0.09:
        for i in range(h):
            for j in range(w):
                dungeon[ry + i][rx + j] = TILES["trap"]
    else:
        for _ in range(random.randint(1, 5)):
            x = rx + random.randint(0, w - 1)
            y = ry + random.randint(0, h - 1)
            if dungeon[y][x] == TILES["room"]:
                dungeon[y][x] = random.choice([TILES["enemy"], TILES["trap"], TILES["treasure"]])

# 外周を壁にする
for x in range(WIDTH):
    dungeon[0][x] = TILES["wall"]
    dungeon[HEIGHT - 1][x] = TILES["wall"]
for y in range(HEIGHT):
    dungeon[y][0] = TILES["wall"]
    dungeon[y][WIDTH - 1] = TILES["wall"]

# スタート・ゴールを配置
dungeon[sy][sx] = TILES["start"]
dungeon[gy][gx] = TILES["goal"]

# 表示
for row in dungeon:
    print("".join(row))