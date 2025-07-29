# 📁 TidyBit 2

A sleek, interactive command-line tool that organizes your messy directories into neat **system folders** (`Pictures`, `Documents`, `Videos`) or custom folders like `Archives`.

✨ Features interactive folder selection, preview mode, and confirmation.

---

## 🚀 Features

- 🧭 **Interactive folder selection** with arrow keys (powered by `questionary`)
- 🔍 **Preview of file moves** (e.g., `photo.jpg → Pictures`)
- ✅ **Confirmation prompt** to accept or cancel
- 🗂️ Moves files to system folders:
  - `.jpg`, `.png` → `Pictures`
  - `.pdf`, `.docx` → `Documents`
  - `.mp4`, `.mov` → `Videos`
- 📦 Unmapped files (e.g., `.zip`, `.rar`) go to `Archives`
- 💻 Works on **Windows** and **Linux**
- 🔧 Auto-creates folders if they’re missing

---

## 🛠️ Installation

Install with a single command (no cloning needed):

### 🔧 For Linux/macOS:

```bash
curl -sSL https://pypi.org/project/tydybit2/0.1.1/.sh | bash
```

### 🪟 For Windows (PowerShell):

```powershell
iwr -useb https://yourdomain.com/install-organizer.ps1 | iex
```

---

### 🐍 Or install via pip:

```bash
pip install tidybit2
```

All dependencies (like `questionary`) will be handled automatically.

---

## 💡 Usage

### 🔄 Interactive mode:

```bash
organize
```

### 📂 Run on a specific folder:

```bash
organize ~/Downloads
```

---

## 📄 License

MIT License – free to use, remix, or deploy in your startup pitch deck (just don’t pretend you wrote it all).

---

## 🤝 Contribute

Want to make it smarter? Found a bug?  
PRs are open – fork it, improve it, and let’s tidy some bits together.

---

> 🧠 *“Clutter is just data without direction. TidyBit gives it purpose.”*
