import lzstring

# 入出力ファイル
input_file = "save.json"      # 展開した JSON（文字列のまま）
output_file = "file1.rpgsave" # ゲームに戻す用

# JSON文字列をそのまま読み込む
with open(input_file, "r", encoding="utf-8") as f:
    json_text = f.read()

# ★ ここで文字列置換（例：所持金を999999にする）
json_text = json_text.replace('" _gold": 12345', '"_gold": 999999')

# LZString Base64 圧縮
lz = lzstring.LZString()
compressed = lz.compressToBase64(json_text)

# .rpgsave として保存
with open(output_file, "w", encoding="ascii") as f:
    f.write(compressed)

print("非破壊型で再圧縮完了")