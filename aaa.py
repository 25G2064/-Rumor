import base64
import lzstring
import json

input_file = "file1.rpgsave"
output_file = "save.json"

# 1. .rpgsave を「テキストとして」読み込む（ここが重要）
with open(input_file, "r", encoding="ascii") as f:
    base64_text = f.read()

# 2. LZString の Base64 展開を使う
lz = lzstring.LZString()
json_text = lz.decompressFromBase64(base64_text)

# 3. JSON に変換
save_data = json.loads(json_text)

# 4. 保存
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(save_data, f, ensure_ascii=False, indent=2)

print("展開完了:", output_file)