# 🦤 dodo

**dodo** is a minimal, fast and interactive domain availability checker for the terminal.  
It checks if a domain name is available across multiple TLDs and supports CSV/JSON export directly to your Desktop.

---

## ✨ Features

- 🌐 Check availability across popular TLDs (`.com`, `.io`, `.dev`, etc.)
- 📤 Export results as CSV or JSON
- 🖥️ Automatically saves exports to your Desktop
- 🎨 Colorful, clean output with progress bar
- ⚡ Parallelized WHOIS checks (fast)
- 🧠 Interactive shell mode with commands (`quit`, `export`, `help`)

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/dodo.git
cd dodo
pip install .
```

---

## 🧑‍💻 Usage

### Launch interactive mode:
```bash
dodo
```

### Inside the shell:

| Command                         | Description                             |
|----------------------------------|-----------------------------------------|
| `example`                        | Check availability of `example.*`       |
| `export csv domains.csv`         | Export last results to Desktop as CSV   |
| `export json domains.json`       | Export last results to Desktop as JSON  |
| `help`                           | Show help text                          |
| `quit` / `exit`                  | Exit dodo                               |

---

## 🧪 Example

```bash
> example
🔍 Checking availability for 'example'...

+-------------------+------------+
|      Domain       |   Status   |
+-------------------+------------+
| example.com       | ❌ Taken    |
| example.net       | ✅ Available |
| example.dev       | ✅ Available |
+-------------------+------------+

> export csv domains.csv
💾 Results exported to Desktop as 'domains.csv'
```

---

## 🧱 Project Structure

```
dodo/
├── main.py
├── commands.py
├── checker.py
├── exporter.py
├── utils.py
├── __init__.py
├── setup.py
├── tlds.txt
```

---

## 📜 License

MIT © 2025 Oguzhan Budak  
Feel free to use, share, improve and contribute 🙌

---
