import json
import os
from unittest import TestCase
import pymustache as mustache

class TestMustache(TestCase):
    def _prepare_data(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'spec/specs/', filename)) as fp:
            data = json.load(fp)['tests']
        for test in data:
            context = test['data']
            if 'lambda' in context:
                context['lambda'] = eval(context['lambda']['python'])
        return data

    def _run_test(self, filename):
        tests = self._prepare_data(filename)
        for test in tests:
            context = test['data']
            template = test['template']
            expected = test['expected']
            partials = test['partials'] if 'partials' in test else {}
            result = mustache.render(template, context, partials)
            self.assertEqual(result, expected, test['name'])

    def test_comments(self):
        """Verify comments.json"""
        self._run_test('comments.json')

    def test_delimiters(self):
        """Verify delimiters.json"""
        self._run_test('delimiters.json')

    def test_interpolation(self):
        """Verify interpolation.json"""
        self._run_test('interpolation.json')

    def test_inverted(self):
        """Verify inverted.json"""
        self._run_test('inverted.json')

    def test_lambdas(self):
        """Verify lambdas.json"""
        self._run_test('~lambdas.json')

    def test_partials(self):
        """Verify partials.json"""
        self._run_test('partials.json')

    def test_sections(self):
        """Verify sections.json"""
        self._run_test('sections.json')

if __name__ == '__main__':
    unittest.main()
