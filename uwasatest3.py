# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ★ 日本語フォント設定
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# SimulationConfig（実験条件を1か所に集約）
# ============================================
class SimulationConfig:
    WIDTH = 75
    HEIGHT = 75
    AGENTS_NUMBER = 675

    INITIAL_FALSE_SPREADER = 66
    INITIAL_TRUE_SPREADER = 6

    TRUE_RUMOR_START = 144

    RUMOR_RADIUS = 2.0
    BASE_SPREAD_PROBABILITY = 1.0
    BASE_FORGET_TIME = 672
    SIMULATION_TIME = 672
    AGENT_SPEED = 1.0

    HIGH_INFLUENCE_RATIO = 0.1
    HIGH_TRUST_RATIO = 0.1

    # ★ 真実を広める人になる確率（0〜1）
    TRUE_SPREADER_PROB = 0.1

# ============================================
# AgentConfig（個人差）
# ============================================
class AgentConfig:
    INTEREST_MIN = 1.0
    INTEREST_MAX = 1.0

    INFLUENCE_MIN = 1.0
    INFLUENCE_MAX = 1.0

    TRUST_MIN = 0.7
    TRUST_MAX = 0.9

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
# 初期化（★最初の真実スプレッダーIDを返す）
# ============================================
def initialize_simulation():
    agents = []
    for _ in range(SimulationConfig.AGENTS_NUMBER):
        x = np.random.rand() * SimulationConfig.WIDTH
        y = np.random.rand() * SimulationConfig.HEIGHT
        agents.append(Agent(x, y))

    high_inf_count = int(SimulationConfig.AGENTS_NUMBER * SimulationConfig.HIGH_INFLUENCE_RATIO)
    idx_inf = np.random.choice(SimulationConfig.AGENTS_NUMBER, high_inf_count, replace=False)
    for i in idx_inf:
        agents[i].influence *= 2.0

    high_trust_count = int(SimulationConfig.AGENTS_NUMBER * SimulationConfig.HIGH_TRUST_RATIO)
    idx_trust = np.random.choice(SimulationConfig.AGENTS_NUMBER, high_trust_count, replace=False)
    for i in idx_trust:
        agents[i].trust = 1.0

    idx = np.random.choice(SimulationConfig.AGENTS_NUMBER, SimulationConfig.INITIAL_FALSE_SPREADER, replace=False)
    for i in idx:
        agents[i].state = FALSE_SPREADER
        agents[i].rumor_time = 0

    # ★ 最初の真実スプレッダーIDを保存するリスト
    initial_true_ids = []

    return agents, initial_true_ids

# ============================================
# デマの伝播
# ============================================
def spread_false(a1, a2, frame):
    if a1.state == FALSE_SPREADER and a2.state == IGNORANT:

        effective_radius = SimulationConfig.RUMOR_RADIUS * a1.influence
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)

        prob = SimulationConfig.BASE_SPREAD_PROBABILITY * a1.interest * a1.influence * a2.trust

        if dist < effective_radius and np.random.rand() < prob:
            if a2.interest >= 1.0:
                a2.state = FALSE_SPREADER
            else:
                a2.state = FALSE_BELIEVER
            a2.rumor_time = frame

# ============================================
# 真実の伝播（確率で TRUE_SPREADER になる）
# ============================================
def spread_true(a1, a2, frame):
    if a1.state == TRUE_SPREADER and a2.state in (IGNORANT, FALSE_BELIEVER, FALSE_SPREADER):

        effective_radius = SimulationConfig.RUMOR_RADIUS * a1.influence
        dist = np.hypot(a1.x - a2.x, a1.y - a2.y)

        prob = SimulationConfig.BASE_SPREAD_PROBABILITY * a1.interest * a1.influence * 1.2 * a2.trust

        if dist < effective_radius and np.random.rand() < prob:

            # ★ 確率で TRUE_SPREADER になる
            if np.random.rand() < SimulationConfig.TRUE_SPREADER_PROB:
                a2.state = TRUE_SPREADER
            else:
                a2.state = TRUE_BELIEVER

            a2.rumor_time = frame

# ============================================
# 忘却（★最初の2人は忘却しない）
# ============================================
def update_state(agent, frame, initial_true_ids):

    if id(agent) in initial_true_ids:
        return

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
    agents, initial_true_ids = initialize_simulation()
    history = []

    count_I, count_FS, count_FB, count_TS, count_TB = [], [], [], [], []

    false_end_time = None
    effort = 0

    for frame in range(SimulationConfig.SIMULATION_TIME):

        # ★ 真実を流す（最初の2人を登録）
        if frame == SimulationConfig.TRUE_RUMOR_START:
            idx = np.random.choice(SimulationConfig.AGENTS_NUMBER, SimulationConfig.INITIAL_TRUE_SPREADER, replace=False)
            for i in idx:
                agents[i].state = TRUE_SPREADER
                agents[i].rumor_time = frame
                initial_true_ids.append(id(agents[i]))

        for a in agents:
            a.move()

        for i, a1 in enumerate(agents):
            for j, a2 in enumerate(agents):
                if i == j: continue

                before = a2.state
                spread_false(a1, a2, frame)
                spread_true(a1, a2, frame)

                if a2.state != before and a1.state == TRUE_SPREADER:
                    effort += 1

        for a in agents:
            update_state(a, frame, initial_true_ids)

        count_I.append(sum(a.state == IGNORANT for a in agents))
        count_FS.append(sum(a.state == FALSE_SPREADER for a in agents))
        count_FB.append(sum(a.state == FALSE_BELIEVER for a in agents))
        count_TS.append(sum(a.state == TRUE_SPREADER for a in agents))
        count_TB.append(sum(a.state == TRUE_BELIEVER for a in agents))

        if false_end_time is None:
            if count_FS[-1] == 0 and count_FB[-1] == 0:
                false_end_time = frame
                break

        history.append([Agent(a.x, a.y) for a in agents])
        for h, a in zip(history[-1], agents):
            h.state = a.state

    remaining_false = count_FS[-1] + count_FB[-1]
    remaining_true = count_TS[-1] + count_TB[-1]
    remaining_ignorant = count_I[-1]

    return (
        history,
        (count_I, count_FS, count_FB, count_TS, count_TB),
        false_end_time,
        effort,
        remaining_false,
        remaining_true,
        remaining_ignorant
    )

# ============================================
# 描画 & 出力
# ============================================
(history, counts, false_end_time, effort,
 remaining_false, remaining_true, remaining_ignorant) = run_simulation()

count_I, count_FS, count_FB, count_TS, count_TB = counts

print("デマが消えるまでの時間:", false_end_time)
print("デマを消すための労力（真実の接触回数）:", effort)

if false_end_time is None:
    print("指定時間までにデマは消えませんでした。")
    print("残ったデマ人数:", remaining_false)
    print("残った真実側:", remaining_true)
    print("未接触:", remaining_ignorant)
else:
    print("デマは途中で消滅しました。")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.set_xlim(0, SimulationConfig.WIDTH)
ax1.set_ylim(0, SimulationConfig.HEIGHT)
ax1.set_aspect('equal')

# ★ 横軸を「日」表示に変更（48フレーム＝1日）
frames_per_day = 48
max_days = SimulationConfig.SIMULATION_TIME // frames_per_day

ax2.set_xticks([d * frames_per_day for d in range(max_days + 1)])
ax2.set_xticklabels([f"{d}日" for d in range(max_days + 1)])

ax2.set_xlim(0, SimulationConfig.SIMULATION_TIME)
ax2.set_ylim(0, SimulationConfig.AGENTS_NUMBER)
ax2.set_title("Rumor Spread Over Time")
ax2.set_xlabel("経過日数")
ax2.set_ylabel("人数")
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
