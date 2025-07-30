cliptext

**Smart sentence-based text clipper for Python.**  
Cuts long text without breaking sentences. Great for YouTube descriptions, SEO titles, social posts, and more.

---

✨ Features

- Clips text at punctuation (".", "!", "?")
- Keeps sentences whole — no awkward mid-cut phrases
- Adds `...` if text is trimmed
- Simple, lightweight — no dependencies

---

📦 Installation

```bash
pip install cliptext
````

🧠 Usage

```python
from cliptext import clip_text

text = "This is a long description. It has many sentences! But not all will fit?"

short = clip_text(text, limit=50)
print(short)  # Output: "This is a long description..."
```

 `clip_text(text: str, limit: int) -> str`

| Parameter | Type  | Description                      |
| --------- | ----- | -------------------------------- |
| `text`    | `str` | The text you want to clip        |
| `limit`   | `int` | Max number of characters allowed |

---

🆕 What's New in 0.1.1

- ✅ Now supports partial word clipping if sentence is too long
- ✅ Won’t break words unless absolutely needed (e.g., if first word is too long)


👨‍💻 Author

Made with ❤️ by [Vivek Appu](https://github.com/VivekMalayarasan)

---

📝 License

MIT License – free to use, modify, and share.


