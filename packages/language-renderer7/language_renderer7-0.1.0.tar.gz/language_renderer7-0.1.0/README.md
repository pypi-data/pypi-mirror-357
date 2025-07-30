# LanguageRenderer7

**LanguageRenderer7** is a Python-based language converter that supports converting code from 7 popular programming languages into Python. It includes syntax transformers, code visualization, statistical insights, and rich colored terminal output.

## 🌍 Supported Input Languages

* JavaScript
* Java
* C
* C++
* Go
* PHP
* Ruby

---

## 🚀 Features

* Convert code from 7 languages to Python.
* Render with syntax highlighting using `pygments`.
* Beautiful CLI output with `rich` and `colorama`.
* Analyze conversion frequency and visualize using `matplotlib` and `networkx`.
* Batch rendering with `tqdm` progress bar.
* Web scraping code snippets using `requests` and `beautifulsoup4`.
* Logs all conversions and builds a language graph.

---

## 🛠 Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -U pip
pip install language-renderer7
```

Or Clone With Git
```bash
git clone https://github.com/EdenGithhub/LanguageRenderer7
```
> ⚠️ Requires Python 3.7+

---

## 📦 Dependencies

* `matplotlib`
* `numpy`
* `colorama`
* `rich`
* `pygments`
* `beautifulsoup4`
* `requests`
* `tqdm`
* `lxml`
* `networkx`

Install all via:

```bash
pip install -r requirements.txt
```

---

## 📄 Example: Basic Usage

```python
from language_renderer7.core import LanguageRenderer

renderer = LanguageRenderer()
code = 'console.log("Hello from JS!");'
output = renderer.render(code, "javascript")
print(output)
```

---

## 📁 Example: Render from File

```python
output = renderer.render_from_file("examples/example.c", "c", highlight=False)
print(output)
```

---

## 🔁 Batch Rendering Example

```python
items = [
    ("javascript", 'console.log("Hello")'),
    ("php", 'echo "Hi!";'),
    ("ruby", 'puts "Hey!"')
]
results = renderer.render_batch(items, highlight=False)
```

---

## 🌐 Web Scrape Docs

```python
snippets = renderer.scrape_doc("https://www.w3schools.com/js/js_examples.asp")
print(snippets)
```

---

## 📊 Show Stats and Graph

```python
renderer.show_stats()
renderer.show_graph()
```

---

## ✅ Testing

Run full tests:

```bash
python -m unittest tests/test_core.py -v
```

---

## 📤 Publishing to PyPI

Use your PowerShell with env token:

```powershell
$env:PYPI_USERNAME="your-username"
$env:PYPI_TOKEN="pypi-***"
python -m build
python -m twine upload dist/* --username $env:PYPI_USERNAME --password $env:PYPI_TOKEN --verbose
```

---

## 📚 License

MIT License

---

## ✨ Author

Created with ❤️ by `Adam Alcander et Eden`.

Contact : Email = aeden6877@gmail.com
          GitHub = EdenGithhub

---

## 🔮 Future Plans

* Add Kotlin and Swift support
* LLM-powered smart converter (experimental)
* GUI version with drag & drop support
* VS Code extension
* Live conversion mode via socket
* Language auto-detection
* Integration with GitHub Copilot
* Export to `.py` files directly
* Dark/light themes for terminal
* API endpoints for external tools

© Eden Simamora\2025
