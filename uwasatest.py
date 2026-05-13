# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ============================================
# SimulationConfig（実験条件を1か所に集約）
# ============================================
class SimulationConfig:
    WIDTH = 50
    HEIGHT = 50
    AGENTS_NUMBER = 300

    INITIAL_FALSE_SPREADER = 33
    INITIAL_TRUE_SPREADER = 3

    TRUE_RUMOR_START = 50

    RUMOR_RADIUS = 1.0
    BASE_SPREAD_PROBABILITY = 1.0
    BASE_FORGET_TIME = 30
    SIMULATION_TIME = 200
    AGENT_SPEED = 1.0

    # 影響力の高い人の割合
    HIGH_INFLUENCE_RATIO = 0.1
    # 信頼度の高い人の割合
    HIGH_TRUST_RATIO = 0.1

# ============================================
# AgentConfig（個人差）
# ============================================
class AgentConfig:
    INTEREST_MIN = 1.0
    INTEREST_MAX = 2.0

    INFLUENCE_MIN = 0.5
    INFLUENCE_MAX = 2.0

    TRUST_MIN = 1.0
    TRUST_MAX = 1.0

# ============================================
# 状態（5種類）
# ============================================
IGNORANT = 0
FALSE_SPREADER = 1
FALSE_BELIEVER = 2
TRUE_SPREADER = 3
TRUE_BELIEVER = 4

# ============================================
# Agent 定義
# ============================================
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.state = IGNORANT
        self.rumor_time = -1

        # 個人差
        self.interest = np.random.uniform(AgentConfig.INTEREST_MIN, AgentConfig.INTEREST_MAX)
        self.influence = np.random.uniform(AgentConfig.INFLUENCE_MIN, AgentConfig.INFLUENCE_MAX)
        self.trust = np.random.uniform(AgentConfig.TRUST_MIN, AgentConfig.TRUST_MAX)

    def move(self):
        angle = np.random.rand() * 2 * np.pi
        self.x += SimulationConfig.AGENT_SPEED * np.cos(angle)
        self.y += SimulationConfig.AGENT_SPEED * np.sin(angle)
        self.x = max(0, min(self.x, SimulationConfig.WIDTH))
        self.y = max(0, min(self.y, SimulationConfig.HEIGHT))

# ============================================
# 初期化
# ============================================
def initialize_simulation():
    agents = []
    for _ in range(SimulationConfig.AGENTS_NUMBER):
        x = np.random.rand() * SimulationConfig.WIDTH
        y = np.random.rand() * SimulationConfig.HEIGHT
        agents.append(Agent(x, y))

    # 影響力の高い人を設定
    high_inf_count = int(SimulationConfig.AGENTS_NUMBER * SimulationConfig.HIGH_INFLUENCE_RATIO)
    idx_inf = np.random.choice(SimulationConfig.AGENTS_NUMBER, high_inf_count, replace=False)
    for i in idx_inf:
        agents[i].influence *= 2.0

    # 信頼度の高い人を設定
    high_trust_count = int(SimulationConfig.AGENTS_NUMBER * SimulationConfig.HIGH_TRUST_RATIO)
    idx_trust = np.random.choice(SimulationConfig.AGENTS_NUMBER, high_trust_count, replace=False)
    for i in idx_trust:
        agents[i].trust = 1.0

    # デマを最初に流す（33人）
    idx = np.random.choice(SimulationConfig.AGENTS_NUMBER, SimulationConfig.INITIAL_FALSE_SPREADER, replace=False)
    for i in idx:
        agents[i].state = FALSE_SPREADER
        agents[i].rumor_time = 0

    return agents

# ============================================
# デマの伝播
# ============================================
def spread_false(a1, a2, frame):
    if a1.state == FALSE_SPREADER and a2.state == IGNORANT:

        effective_radius = SimulationConfig.RUMOR_RADIUS * a1.influence
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)

        prob = SimulationConfig.BASE_SPREAD_PROBABILITY * a1.interest * a1.influence * a2.trust

        if dist < effective_radius and np.random.rand() < prob:
            if a2.interest > 1.0:
                a2.state = FALSE_SPREADER
            else:
                a2.state = FALSE_BELIEVER
            a2.rumor_time = frame

# ============================================
# 真実の伝播
# ============================================
def spread_true(a1, a2, frame):
    if a1.state == TRUE_SPREADER and a2.state in (IGNORANT, FALSE_BELIEVER):

        effective_radius = SimulationConfig.RUMOR_RADIUS * a1.influence
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)

        prob = SimulationConfig.BASE_SPREAD_PROBABILITY * a1.interest * a1.influence * 1.2 * a2.trust

        if dist < effective_radius and np.random.rand() < prob:
            if a2.interest > 1.0:
                a2.state = TRUE_SPREADER
            else:
                a2.state = TRUE_BELIEVER
            a2.rumor_time = frame

# ============================================
# デマの否定（真実を知ったら上書き）
# ============================================
def correct_false(agent):
    if agent.state in (TRUE_SPREADER, TRUE_BELIEVER):
        if agent.state == FALSE_SPREADER or agent.state == FALSE_BELIEVER:
            agent.state = TRUE_BELIEVER

# ============================================
# 忘却
# ============================================
def update_state(agent, frame):
    if agent.state == FALSE_SPREADER:
        if frame - agent.rumor_time > SimulationConfig.BASE_FORGET_TIME * (0.5 + agent.interest):
            agent.state = FALSE_BELIEVER

    if agent.state == TRUE_SPREADER:
        if frame - agent.rumor_time > SimulationConfig.BASE_FORGET_TIME * (0.5 + agent.interest):
            agent.state = TRUE_BELIEVER

# ============================================
# 色
# ============================================
def get_color(agent):
    if agent.state == IGNORANT: return "#999999"
    if agent.state == FALSE_SPREADER: return "#0072B2"
    if agent.state == FALSE_BELIEVER: return "#99C2FF"
    if agent.state == TRUE_SPREADER: return "#E60026"
    if agent.state == TRUE_BELIEVER: return "#FF99A0"

# ============================================
# シミュレーション本体
# ============================================
def run_simulation():
    agents = initialize_simulation()
    history = []

    count_I, count_FS, count_FB, count_TS, count_TB = [], [], [], [], []

    false_end_time = None
    effort = 0  # 真実が接触した回数

    for frame in range(SimulationConfig.SIMULATION_TIME):

        # 真実を流す
        if frame == SimulationConfig.TRUE_RUMOR_START:
            idx = np.random.choice(SimulationConfig.AGENTS_NUMBER, SimulationConfig.INITIAL_TRUE_SPREADER, replace=False)
            for i in idx:
                agents[i].state = TRUE_SPREADER
                agents[i].rumor_time = frame

        # 移動
        for a in agents:
            a.move()

        # 伝播
        for i, a1 in enumerate(agents):
            for j, a2 in enumerate(agents):
                if i == j: continue

                before = a2.state
                spread_false(a1, a2, frame)
                spread_true(a1, a2, frame)
                if a2.state != before and a1.state == TRUE_SPREADER:
                    effort += 1

        # 状態更新
        for a in agents:
            update_state(a, frame)
            correct_false(a)

        # カウント
        count_I.append(sum(a.state == IGNORANT for a in agents))
        count_FS.append(sum(a.state == FALSE_SPREADER for a in agents))
        count_FB.append(sum(a.state == FALSE_BELIEVER for a in agents))
        count_TS.append(sum(a.state == TRUE_SPREADER for a in agents))
        count_TB.append(sum(a.state == TRUE_BELIEVER for a in agents))

        # 停止条件：デマ完全消滅
        if false_end_time is None:
            if count_FS[-1] == 0 and count_FB[-1] == 0:
                false_end_time = frame
                break

        # 履歴保存
        history.append([Agent(a.x, a.y) for a in agents])
        for h, a in zip(history[-1], agents):
            h.state = a.state

    return history, (count_I, count_FS, count_FB, count_TS, count_TB), false_end_time, effort

# ============================================
# 描画
# ============================================
history, counts, false_end_time, effort = run_simulation()
count_I, count_FS, count_FB, count_TS, count_TB = counts

print("デマが消えるまでの時間:", false_end_time)
print("デマを消すための労力（真実の接触回数）:", effort)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.set_xlim(0, SimulationConfig.WIDTH)
ax1.set_ylim(0, SimulationConfig.HEIGHT)
ax1.set_aspect('equal')

ax2.set_xlim(0, SimulationConfig.SIMULATION_TIME)
ax2.set_ylim(0, SimulationConfig.AGENTS_NUMBER)
ax2.set_title("Rumor Spread Over Time")
ax2.set_xlabel("Time")
ax2.set_ylabel("Number of Agents")
ax2.grid(True)

line_I,  = ax2.plot([], [], color="#999999", label="Ignorant")
line_FS, = ax2.plot([], [], color="#0072B2", label="False Spreader")
line_FB, = ax2.plot([], [], color="#99C2FF", label="False Believer")
line_TS, = ax2.plot([], [], color="#E60026", label="True Spreader")
line_TB, = ax2.plot([], [], color="#FF99A0", label="True Believer")

ax2.legend()

def animate(frame):
    agents = history[frame]

    x = [a.x for a in agents]
    y = [a.y for a in agents]
    colors = [get_color(a) for a in agents]

    ax1.clear()
    ax1.set_xlim(0, SimulationConfig.WIDTH)
    ax1.set_ylim(0, SimulationConfig.HEIGHT)
    ax1.set_title(f"Frame: {frame}")
    ax1.scatter(x, y, c=colors, s=30)

    line_I.set_data(range(frame), count_I[:frame])
    line_FS.set_data(range(frame), count_FS[:frame])
    line_FB.set_data(range(frame), count_FB[:frame])
    line_TS.set_data(range(frame), count_TS[:frame])
    line_TB.set_data(range(frame), count_TB[:frame])

ani = animation.FuncAnimation(fig, animate, frames=len(history), interval=50)
plt.show()
