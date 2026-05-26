import unittest
from chains import parse_json_output

class TestChainsParser(unittest.TestCase):
    def test_parse_raw_json(self):
        raw_json = '{"language": "python", "explanation": "test", "bugs": [], "fixed_code": "print(1)", "improvements": []}'
        result = parse_json_output(raw_json)
        self.assertEqual(result["language"], "python")
        self.assertEqual(result["explanation"], "test")

    def test_parse_json_with_markdown_fences(self):
        markdown_json = '```json\n{"language": "javascript", "explanation": "test js", "bugs": [], "fixed_code": "console.log(1)", "improvements": []}\n```'
        result = parse_json_output(markdown_json)
        self.assertEqual(result["language"], "javascript")
        self.assertEqual(result["explanation"], "test js")

    def test_parse_json_with_generic_fences(self):
        markdown_json = '```\n{"language": "go", "explanation": "test go", "bugs": [], "fixed_code": "fmt.Println(1)", "improvements": []}\n```'
        result = parse_json_output(markdown_json)
        self.assertEqual(result["language"], "go")
        self.assertEqual(result["explanation"], "test go")

if __name__ == "__main__":
    unittest.main()
