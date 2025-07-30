import re
import colorama
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style
from bs4 import BeautifulSoup
from rich.console import Console
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from tqdm import tqdm
import networkx as nx
import requests

colorama.init()
console = Console()

SUPPORTED_LANGUAGES = ["javascript", "java", "c", "cpp", "go", "php", "ruby"]

class LanguageRenderer:
    def __init__(self):
        self.rules = {
            "javascript": self.from_js,
            "java": self.from_java,
            "c": self.from_c,
            "cpp": self.from_cpp,
            "go": self.from_go,
            "php": self.from_php,
            "ruby": self.from_ruby,
        }
        self.graph = nx.DiGraph()
        self.log = []
    
    def render_from_file(self, filepath: str, lang: str, highlight: bool = True) -> str:
        with open(filepath, encoding="utf-8") as f:
            code = f.read()
        return self.render(code, lang, highlight=highlight)


    def render(self, code: str, lang: str, highlight: bool = True) -> str:
        lang = lang.lower()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"{Fore.RED}{lang} not supported.{Style.RESET_ALL}")
        console.print(f"[bold blue]Rendering from {lang} to Python...[/bold blue]")
        result = self.rules[lang](code)
        self.log.append((lang, code))
        self.graph.add_node(lang)
        self.graph.add_edge(lang, "python")
        print(f"{Fore.GREEN}✔ Rendered successfully!{Style.RESET_ALL}")
        return self.highlight_python(result) if highlight else result

    def highlight_python(self, code: str) -> str:
        return highlight(code, PythonLexer(), TerminalFormatter())

    def from_js(self, code):
        return re.sub(r'console\.log\((.+?)\);', r'print(\1)', code)

    def from_java(self, code):
        code = re.sub(r'System\.out\.println\((.+?)\);', r'print(\1)', code)
        return re.sub(r'int\s+(\w+)\s*=', r'\1 =', code)

    def from_c(self, code):
        return re.sub(r'printf\("([^"]+)"\);', r'print("\1")', code)

    def from_cpp(self, code):
        return re.sub(r'std::cout\s*<<\s*(.+?)\s*<<\s*std::endl;', r'print(\1)', code)

    def from_go(self, code):
        return re.sub(r'fmt\.Println\((.+?)\)', r'print(\1)', code)

    def from_php(self, code):
        return re.sub(r'echo\s+(.+?);', r'print(\1)', code)

    def from_ruby(self, code):
        return re.sub(r'puts\s+(.+)', r'print(\1)', code)

    def show_graph(self):
        nx.draw(self.graph, with_labels=True, node_color='lightblue', edge_color='gray')
        plt.title("Language Conversion Graph")
        plt.show()

    def show_stats(self):
        lang_counts = {lang: sum(1 for l, _ in self.log if l == lang) for lang in SUPPORTED_LANGUAGES}
        langs = list(lang_counts.keys())
        values = list(lang_counts.values())
        y_pos = np.arange(len(langs))

        plt.figure(figsize=(10,5))
        plt.bar(y_pos, values, color='skyblue')
        plt.xticks(y_pos, langs)
        plt.xlabel("Language")
        plt.ylabel("Conversions")
        plt.title("Conversion Statistics")
        plt.show()

    def scrape_doc(self, url: str, tag: str = 'pre') -> str:
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, 'lxml')
            snippets = soup.find_all(tag)
            return "\n\n".join(s.get_text() for s in snippets[:3])
        except Exception as e:
            return f"{Fore.RED}Error: {e}{Style.RESET_ALL}"

    def render_batch(self, items, highlight: bool = True):
        outputs = []
        for item in tqdm(items, desc="Rendering batch"):
            lang, code = item
            try:
                outputs.append(self.render(code, lang, highlight=highlight))
            except Exception as e:
                outputs.append(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return outputs

if __name__ == '__main__':
    renderer = LanguageRenderer()
    js = 'console.log("Hello, world!");'
    print(renderer.render(js, "javascript"))
    print(renderer.scrape_doc("https://www.w3schools.com/js/js_examples.asp"))
    renderer.show_stats()
    renderer.show_graph()
