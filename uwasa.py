# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ================================
# パラメータ設定
# ================================
WIDTH = 50
HEIGHT = 50
AGENTS_NUMBER = 300

# 噂A（正しい情報）
INITIAL_SPREADER_A = 0
RUMOR_A_START = 50

# 噂B（デマ）
INITIAL_SPREADER_B = 3

RUMOR_RADIUS = 3.0
BASE_SPREAD_PROBABILITY = 0.1
BASE_FORGET_TIME = 30
SIMULATION_TIME = 200
AGENT_SPEED = 1.0

# 状態
IGNORANT = 0
SPREADER = 1
STIFLER = 2

# ================================
# エージェント定義
# ================================
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # 噂A（正しい情報）
        self.state_A = IGNORANT
        self.rumor_time_A = -1
        self.interest_A = np.random.uniform(0.0, 2.0)

        # 噂B（デマ）
        self.state_B = IGNORANT
        self.rumor_time_B = -1
        self.interest_B = np.random.uniform(0.0, 2.0)

    def move(self):
        angle = np.random.rand() * 2 * np.pi
        self.x += AGENT_SPEED * np.cos(angle)
        self.y += AGENT_SPEED * np.sin(angle)
        self.x = max(0, min(self.x, WIDTH))
        self.y = max(0, min(self.y, HEIGHT))

# ================================
# 初期化
# ================================
def initialize_simulation():
    agents = []
    for _ in range(AGENTS_NUMBER):
        x = np.random.rand() * WIDTH
        y = np.random.rand() * HEIGHT
        agents.append(Agent(x, y))

    # デマ（噂B）だけ最初に流す
    idx_B = np.random.choice(AGENTS_NUMBER, INITIAL_SPREADER_B, replace=False)
    for i in idx_B:
        agents[i].state_B = SPREADER
        agents[i].rumor_time_B = 0

    return agents

# ================================
# 噂伝播
# ================================
def spread_rumor_A(a1, a2, frame):
    if a2.state_A == IGNORANT:
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)
        prob = BASE_SPREAD_PROBABILITY * a1.interest_A
        if dist < RUMOR_RADIUS and np.random.rand() < prob:
            a2.state_A = SPREADER
            a2.rumor_time_A = frame

def spread_rumor_B(a1, a2, frame):
    if a2.state_B == IGNORANT:
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)
        prob = BASE_SPREAD_PROBABILITY * a1.interest_B
        if dist < RUMOR_RADIUS and np.random.rand() < prob:
            a2.state_B = SPREADER
            a2.rumor_time_B = frame

# ================================
# 忘却（Stifler化）
# ================================
def check_stifler_A(agent, frame):
    if agent.state_A == SPREADER:
        forget = BASE_FORGET_TIME * (0.5 + agent.interest_A)
        if frame - agent.rumor_time_A > forget:
            agent.state_A = STIFLER

def check_stifler_B(agent, frame):
    if agent.state_B == SPREADER:
        forget = BASE_FORGET_TIME * (0.5 + agent.interest_B)
        if frame - agent.rumor_time_B > forget:
            agent.state_B = STIFLER

# ================================
# 色決定（白背景で見やすい配色）
# ================================
def get_color(agent):
    # 両方広めている → 濃い紫
    if agent.state_A == SPREADER and agent.state_B == SPREADER:
        return "#800080"

    # 正しい噂A → 鮮やかな赤
    if agent.state_A == SPREADER:
        return "#E60026"

    # デマB → 濃い青
    if agent.state_B == SPREADER:
        return "#0072B2"

    # どちらも知らない → グレー
    if agent.state_A == IGNORANT and agent.state_B == IGNORANT:
        return "#999999"

    # Stifler → 緑
    return "#009E73"

# ================================
# シミュレーション本体
# ================================
def run_simulation():
    agents = initialize_simulation()
    history = []

    # 人数推移記録
    count_A_I, count_A_S, count_A_T = [], [], []
    count_B_I, count_B_S, count_B_T = [], [], []

    for frame in range(SIMULATION_TIME):

        # 正しい噂Aを遅れて流す
        if frame == RUMOR_A_START:
            idx_A = np.random.choice(AGENTS_NUMBER, INITIAL_SPREADER_A, replace=False)
            for i in idx_A:
                agents[i].state_A = SPREADER
                agents[i].rumor_time_A = frame

        # 移動
        for a in agents:
            a.move()

        # 伝播
        for i, a1 in enumerate(agents):
            for j, a2 in enumerate(agents):
                if i == j:
                    continue
                if a1.state_A == SPREADER:
                    spread_rumor_A(a1, a2, frame)
                if a1.state_B == SPREADER:
                    spread_rumor_B(a1, a2, frame)

        # 忘却
        for a in agents:
            check_stifler_A(a, frame)
            check_stifler_B(a, frame)

        # 正しい噂Aを信じたらデマBを非活性化
        for a in agents:
            if a.state_A in (SPREADER, STIFLER) and a.state_B == SPREADER:
                a.state_B = STIFLER

        # 人数カウント
        count_A_I.append(sum(a.state_A == IGNORANT for a in agents))
        count_A_S.append(sum(a.state_A == SPREADER for a in agents))
        count_A_T.append(sum(a.state_A == STIFLER for a in agents))

        count_B_I.append(sum(a.state_B == IGNORANT for a in agents))
        count_B_S.append(sum(a.state_B == SPREADER for a in agents))
        count_B_T.append(sum(a.state_B == STIFLER for a in agents))

        # 履歴保存
        history.append([Agent(a.x, a.y) for a in agents])
        for h, a in zip(history[-1], agents):
            h.state_A = a.state_A
            h.state_B = a.state_B

    return history, (count_A_I, count_A_S, count_A_T, count_B_I, count_B_S, count_B_T)

# ================================
# 描画
# ================================
history, counts = run_simulation()
count_A_I, count_A_S, count_A_T, count_B_I, count_B_S, count_B_T = counts

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.set_xlim(0, WIDTH)
ax1.set_ylim(0, HEIGHT)
ax1.set_aspect('equal')

ax2.set_xlim(0, SIMULATION_TIME)
ax2.set_ylim(0, AGENTS_NUMBER)
ax2.set_title("Rumor Spread Over Time")
ax2.set_xlabel("Time")
ax2.set_ylabel("Number of Agents")
ax2.grid(True)

# グラフの線色も見やすい色に統一
line_A_S, = ax2.plot([], [], color="#E60026", label="A Spreader")
line_B_S, = ax2.plot([], [], color="#0072B2", label="B Spreader")
line_A_T, = ax2.plot([], [], color="#B00020", label="A Stifler")
line_B_T, = ax2.plot([], [], color="#005082", label="B Stifler")
line_A_I, = ax2.plot([], [], color="#FF99A0", label="A Ignorant")
line_B_I, = ax2.plot([], [], color="#99C2FF", label="B Ignorant")

ax2.legend()

def animate(frame):
    agents = history[frame]

    x = [a.x for a in agents]
    y = [a.y for a in agents]
    colors = [get_color(a) for a in agents]

    ax1.clear()
    ax1.set_xlim(0, WIDTH)
    ax1.set_ylim(0, HEIGHT)
    ax1.set_title(f"Frame: {frame}")
    ax1.scatter(x, y, c=colors, s=30)

    # グラフ更新
    line_A_S.set_data(range(frame), count_A_S[:frame])
    line_B_S.set_data(range(frame), count_B_S[:frame])
    line_A_T.set_data(range(frame), count_A_T[:frame])
    line_B_T.set_data(range(frame), count_B_T[:frame])
    line_A_I.set_data(range(frame), count_A_I[:frame])
    line_B_I.set_data(range(frame), count_B_I[:frame])

ani = animation.FuncAnimation(fig, animate, frames=SIMULATION_TIME, interval=50)
plt.show()
