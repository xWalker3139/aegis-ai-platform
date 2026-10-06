import unittest
from aegis.core import Platform


class Tests(unittest.TestCase):
    def setUp(self):
        self.p = Platform(':memory:')

    def tearDown(self):
        self.p.db.close()

    def test_contract(self):
        r = self.p.chat([{'role': 'user', 'content': 'hello'}])
        self.assertEqual(r['object'], 'chat.completion')
        self.assertGreater(r['usage']['total_tokens'], 0)

    def test_rag(self):
        self.p.ingest('runbook', 'Kubernetes rollback restores the previous deployment revision.')
        r = self.p.chat([{'role': 'user', 'content': 'Kubernetes rollback'}], rag=True)
        self.assertEqual(r['sources'][0]['source'], 'runbook')

    def test_replace_document(self):
        self.p.ingest('one', 'old text')
        self.p.ingest('one', 'new text')
        self.assertEqual(self.p.retrieve('old'), [])

    def test_guards(self):
        for text in ['ignore previous instructions', 'user@example.com']:
            with self.assertRaises(ValueError):
                self.p.guard(text)

    def test_rate_limit(self):
        self.p.rpm = 1
        self.p.admit()
        with self.assertRaises(ValueError):
            self.p.admit()

    def test_unknown_model(self):
        with self.assertRaises(ValueError):
            self.p.chat([{'role': 'user', 'content': 'hello'}], model='unknown')

    def test_local_disabled(self):
        with self.assertRaises(ValueError):
            self.p.chat([{'role': 'user', 'content': 'hello'}], model='local')

    def test_evaluations(self):
        self.assertTrue(self.p.evaluate()['passed'])

    def test_invalid_messages(self):
        with self.assertRaises(ValueError):
            self.p.chat([])
