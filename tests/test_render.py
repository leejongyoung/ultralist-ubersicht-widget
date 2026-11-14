import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("widget", Path(__file__).resolve().parents[1] / "main.py")
widget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(widget)


class RenderTest(unittest.TestCase):
    def todo(self, **overrides):
        item = dict(id=1, subject="hello", due="", projects=[], contexts=[],
                    archived=False, completed=False)
        return dict(item, **overrides)

    def output_for(self, data, raw=False):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "todos.json"
            path.write_text(data if raw else json.dumps(data), encoding="utf-8")
            return widget.build_output(path)

    def test_subject_is_text_not_html(self):
        output = widget.render_todos([self.todo(subject='<b>demo</b> & "quoted"')])
        self.assertNotIn('<b>', output)
        self.assertIn('&lt;b&gt;demo&lt;/b&gt;', output)
        self.assertIn('&amp;', output)
        self.assertIn('&quot;quoted&quot;', output)

    def test_project_and_context_labels_are_escaped(self):
        output = widget.render_todos([self.todo(subject='+<b> @<i>', projects=['<b>'], contexts=['<i>'])])
        self.assertNotIn('<b>', output)
        self.assertNotIn('<i>', output)
        self.assertIn('+&lt;b&gt;</span>', output)
        self.assertIn('@&lt;i&gt;</span>', output)

    def test_broken_json_has_visible_error(self):
        self.assertIn('Invalid todo data', self.output_for('{broken', raw=True))

    def test_invalid_schema_has_visible_error(self):
        for data in ({'items': []}, [{}], [self.todo(projects=None)]):
            with self.subTest(data=data):
                self.assertIn('Invalid todo data', self.output_for(data))

    def test_invalid_due_date_has_visible_error(self):
        self.assertIn('Invalid todo data', self.output_for([self.todo(due='bad-date')]))

    def test_missing_file_has_help(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIn('ultralist init', widget.build_output(Path(temp) / 'missing.json'))

    def test_completed_and_archived_items_stay_hidden(self):
        output = widget.render_todos([self.todo(subject='visible'),
                                     self.todo(subject='hidden-completed', completed=True),
                                     self.todo(subject='hidden-archived', archived=True)])
        self.assertIn('visible', output)
        self.assertNotIn('hidden-', output)

    def test_default_path_uses_actual_home(self):
        self.assertEqual(widget.path_to_todos, Path.home() / '.todos.json')


if __name__ == '__main__':
    unittest.main()
