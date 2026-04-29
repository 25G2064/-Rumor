import base64
import json
from tkinter import filedialog, Tk, Text, Button, END
from lzstring import LZString

lz = LZString()

def load_save():
    path = filedialog.askopenfilename(
        filetypes=[("RPG Maker MV Save", "*.rpgsave")]
    )
    if not path:
        return

    with open(path, "rb") as f:
        data = f.read()

    # Base64 → LZString → JSON
    decoded = base64.b64decode(data).decode("utf-8")
    decompressed = lz.decompress(decoded)
    save_json = json.loads(decompressed)

    text.delete("1.0", END)
    text.insert(END, json.dumps(save_json, indent=2, ensure_ascii=False))

def save_file():
    # JSON → LZString → Base64
    edited_json = text.get("1.0", END)
    try:
        obj = json.loads(edited_json)
    except:
        print("JSON が不正です")
        return

    compressed = lz.compress(json.dumps(obj))
    encoded = base64.b64encode(compressed.encode("utf-8"))

    path = filedialog.asksaveasfilename(
        defaultextension=".rpgsave",
        filetypes=[("RPG Maker MV Save", "*.rpgsave")]
    )
    if not path:
        return

    with open(path, "wb") as f:
        f.write(encoded)

root = Tk()
root.title("RPGツクールMV セーブエディタ（簡易版）")

Button(root, text="セーブを読み込む", command=load_save).pack()
Button(root, text="保存する", command=save_file).pack()

text = Text(root, width=80, height=30)
text.pack()

root.mainloop()