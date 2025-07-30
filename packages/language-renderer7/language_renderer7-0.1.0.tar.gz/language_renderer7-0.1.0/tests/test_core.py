import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from language_renderer7.core import LanguageRenderer


class TestLanguageRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = LanguageRenderer()

    def test_render_javascript(self):
        code = 'console.log("Hello");'
        output = self.renderer.render(code, 'javascript', highlight=False)
        self.assertIn('print("Hello")', output)

    def test_render_java(self):
        code = 'System.out.println("Hi"); int x = 5;'
        output = self.renderer.render(code, 'java', highlight=False)
        self.assertIn('print("Hi")', output)
        self.assertIn('x = 5', output)

    def test_render_c(self):
        code = 'printf("C language");'
        output = self.renderer.render(code, 'c', highlight=False)
        self.assertIn('print("C language")', output)

    def test_render_cpp(self):
        code = 'std::cout << "C++" << std::endl;'
        output = self.renderer.render(code, 'cpp', highlight=False)
        self.assertIn('print("C++")', output)

    def test_render_go(self):
        code = 'fmt.Println("GoLang")'
        output = self.renderer.render(code, 'go', highlight=False)
        self.assertIn('print("GoLang")', output)

    def test_render_php(self):
        code = 'echo "PHP";'
        output = self.renderer.render(code, 'php', highlight=False)
        self.assertIn('print("PHP")', output)

    def test_render_ruby(self):
        code = 'puts "Ruby"'
        output = self.renderer.render(code, 'ruby', highlight=False)
        self.assertIn('print("Ruby")', output)

    def test_unsupported_language(self):
        with self.assertRaises(ValueError):
            self.renderer.render('println("oops")', 'kotlin')

    def test_render_batch(self):
        items = [
            ("javascript", 'console.log("Batch");'),
            ("php", 'echo "Hello";'),
            ("ruby", 'puts "Ruby";')
        ]
        result = self.renderer.render_batch(items, highlight=False)
        self.assertEqual(len(result), 3)
        for out in result:
            self.assertIn("print(", out)


    def test_scrape_doc_mock(self):
        # Tes URL dummy agar tetap stabil
        result = self.renderer.scrape_doc("https://invalid.localhost.test")
        self.assertTrue("Error" in result or isinstance(result, str))

    def test_log_and_stats(self):
        self.renderer.render('console.log("Test");', 'javascript')
        self.assertEqual(len(self.renderer.log), 1)
        self.assertEqual(self.renderer.log[0][0], 'javascript')

if __name__ == '__main__':
    unittest.main()
