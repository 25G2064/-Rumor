import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.rcParams['font.family'] = 'Meiryo'
import matplotlib.pyplot as plt
import re
import random

def evaluate_word(word):
    score = 0

    # ① 文字種の多様性
    types = [
        bool(re.search(r'[ぁ-ん]', word)),
        bool(re.search(r'[ァ-ヶ]', word)),
        bool(re.search(r'[一-龠]', word)),
        bool(re.search(r'[0-9０-９]', word)),
        bool(re.search(r'[!-/:-@[-`{-~]', word)),
        bool(re.search(r'[A-Za-zＡ-Ｚａ-ｚ]', word))
    ]
    diversity = sum(types)
    score += diversity * 10 + random.randint(-3, 3)

    # ② 象徴性
    symbolic_words = ['神', '闇', '光', '虚無', '運命', '記憶', '夢']
    if any(s in word for s in symbolic_words):
        score += 30 + random.randint(-5, 5)

    # ③ 響きの強度（濁音）
    strong_sounds = 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ'
    sound_score = sum(1 for c in word if c in strong_sounds) * (10 + random.randint(-2, 2))
    score += sound_score

    # ④ 意味の重層性
    concrete_words = ['猫', 'カレー', '剣', '花', '机']
    has_abstract = any(s in word for s in symbolic_words)
    has_concrete = any(c in word for c in concrete_words)
    if has_abstract and has_concrete:
        score += 20 + random.randint(-3, 3)

    # ⑤ 文字数ペナルティ
    length = len(word)
    if length > 5:
        penalty = (length - 5) * 2
        score -= penalty

    # ⑥ 気まぐれ係数（全体補正）
    score += random.randint(-10, 10)

    return score

def plot_bar(word1, word2, score1, score2):
    words = [word1, word2]
    scores = [score1, score2]
    colors = ['blue', 'red']

    plt.figure(figsize=(6, 4))
    bars = plt.bar(words, scores, color=colors)
    plt.title("言葉の強さ比較", fontsize=16)
    plt.ylabel("強さスコア", fontsize=12)
    plt.ylim(min(0, min(scores) - 10), max(scores) + 30)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}', ha='center', fontsize=12)

    winner = word1 if score1 > score2 else word2 if score2 > score1 else "引き分け"
    plt.text(0.5, -0.15, f"🏆 勝者: {winner}", ha='center', fontsize=14, transform=plt.gca().transAxes)
    plt.tight_layout()
    plt.show()

def compare():
    word1 = entry1.get()
    word2 = entry2.get()
    score1 = evaluate_word(word1)
    score2 = evaluate_word(word2)
    plot_bar(word1, word2, score1, score2)

# GUI構築
root = tk.Tk()
root.title("言葉の強さ比較")

ttk.Label(root, text="言葉1").grid(row=0, column=0, padx=5, pady=5)
entry1 = ttk.Entry(root, width=30)
entry1.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="言葉2").grid(row=1, column=0, padx=5, pady=5)
entry2 = ttk.Entry(root, width=30)
entry2.grid(row=1, column=1, padx=5, pady=5)

ttk.Button(root, text="比較する", command=compare).grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()