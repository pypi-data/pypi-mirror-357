# 📁 Tidybit2

A beautiful, interactive command-line tool that organizes your messy directories into neat **system folders** (`Pictures`, `Documents`, `Videos`) or custom folders like `Archives`.

✨ Now with interactive folder selection and preview mode.

---

## 🚀 Features

- 🧭 **Interactive folder selection** using arrow keys (powered by `questionary`)
- 🔍 **Preview of file moves** before execution (e.g., `photo.jpg → Pictures`)
- ✅ **Confirmation prompt** to accept or cancel the operation
- 🗂️ Automatically moves files to system folders:
  - `.jpg`, `.png` → `Pictures`
  - `.pdf`, `.docx` → `Documents`
  - `.mp4`, `.mov` → `Videos`
- 📦 Unmapped files (e.g., `.zip`, `.rar`) go to an `Archives` folder
- 💻 Supports both **Windows** and **Linux**
- 🔧 Auto-creates folders if they don’t exist

---

## 🛠️ Installation

### 1. Clone the repository:

```bash
git clone <your-repo-url>
cd file-organizer
```

### 2. Install the tool:

```bash
pip install .
```

All dependencies (like `questionary`) will be installed automatically.

---

## 💡 Usage

### 🔄 Interactive Mode (default)

Organize files by **interactively selecting a directory** and previewing the changes:

```bash
organize
```

### 📂 Target Specific Folder

Run directly on a known folder, with a preview + confirmation:

```bash
organize ~/Downloads
```

---

## 💻 Example

**Before:**

```
~/Downloads/
├── cat.png
├── report.pdf
├── movie.mkv
├── old_files.zip
```

**After:**

```
~/Pictures/cat.png
~/Documents/report.pdf
~/Videos/movie.mkv
~/Downloads/Archives/old_files.zip
```

---

## 📦 Requirements

- Python **3.6+**
- `questionary` (installed automatically with `pip install .`)

---

## 🔭 Planned Features

- 🛠️ **Custom folder mappings** via config file (YAML/JSON)
- 📝 **Logging** of file moves for audit/history
- ♻️ **Undo** functionality in case you regret everything

---

## 📄 License

MIT License – do what you want, just don’t sell it to your grandma as your idea.

---

## 🤝 Contributing

Found a bug or want to add a cool feature? PRs are welcome.  
Open an issue, fork the project, and let’s make directory chaos a thing of the past.

---

> 🧠 *“Clutter is just postponed decisions. Let File Organizer decide for you.”*
