import unittest
import json
from app import format_summary, format_chat_id

class TestFormatting(unittest.TestCase):
    def test_format_chat_id(self):
        self.assertEqual(format_chat_id("-100123456789"), "123456789")
        self.assertEqual(format_chat_id("123456789"), "123456789")
        self.assertEqual(format_chat_id(-100123456789), "123456789")
        self.assertEqual(format_chat_id(123456789), "123456789")

    def test_format_summary_valid_json(self):
        chat_id = "-100987654321"
        summary_json = json.dumps([
            {
                "topic": "Test Topic",
                "participants": ["User1", "User2"],
                "discussion": [
                    {
                        "point": "Discussion Point 1",
                        "key_message_ids": [10, 11]
                    }
                ]
            }
        ])
        
        expected_output = """## Test Topic
Participant: User1, User2
Discussion:
 - Discussion Point 1 <a href="https://t.me/c/987654321/10">[1]</a> <a href="https://t.me/c/987654321/11">[2]</a>"""
        
        result = format_summary(summary_json, chat_id)
        self.assertEqual(result, expected_output)

    def test_format_summary_with_markdown_blocks(self):
        chat_id = "-100987654321"
        summary_json = """```json
[
  {
    "topic": "Test Topic",
    "participants": ["User1"],
    "discussion": [
      {
        "point": "Point",
        "key_message_ids": [5]
      }
    ]
  }
]
```"""
        expected_output = """## Test Topic
Participant: User1
Discussion:
 - Point <a href="https://t.me/c/987654321/5">[1]</a>"""
        
        result = format_summary(summary_json, chat_id)
        self.assertEqual(result, expected_output)

    def test_format_summary_invalid_json(self):
        chat_id = 123
        invalid_json = "Not JSON"
        result = format_summary(invalid_json, chat_id)
        self.assertTrue(result.startswith("Error parsing summary"))

if __name__ == '__main__':
    unittest.main()
