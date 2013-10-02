# -*- coding: UTF-8 -*-

import unittest
from collections import Counter
from mock import Mock, patch

import compare
from compare import read_evaluation_data
from compare import read_config
from compare import process_one_doc
from compare import initialize_analysers
from compare import evaluate
from compare import get_max_weighted_errors


def get_mock_analyzer(name, output):
    mock_analyzer = Mock()
    mock_analyzer.analyse = Mock(return_value=output)
    mock_analyzer.name = name
    return mock_analyzer


class TestCase(unittest.TestCase):

    def test_read_config(self):
        lines = ["a\tb"]
        mock_open = Mock(return_value=lines)
        with patch('compare.codecs.open', mock_open):
            actual = read_config()
            self.assertEqual(actual, {'a': 'b'})

    def test_read_evaluation_data(self):
        exp_doc_id2doc = {0: 'a', 1: 'b', 2: 'c'}
        exp_doc_id2key = {0: '+', 1: '-', 2: '0'}
        lines = ["a\t+", "b\t-", "c\t0"]
        mock_open = Mock(return_value=lines)
        with patch('compare.codecs.open', mock_open):
            act_doc_id2doc, act_doc_id2key = read_evaluation_data('test.txt')
            self.assertEqual(act_doc_id2key, exp_doc_id2key)
            self.assertEqual(act_doc_id2doc, exp_doc_id2doc)

    def test_read_evaluation_data__ignores_documents_marked_as_irrelevant(self):
        exp_doc_id2doc = {0: 'a', 1: 'c'}
        exp_doc_id2key = {0: '+', 1: '0'}
        lines = ["a\t+", "b\tX", "c\t0"]
        mock_open = Mock(return_value=lines)
        with patch('compare.codecs.open', mock_open):
            act_doc_id2doc, act_doc_id2key = read_evaluation_data('test.txt')
            self.assertEqual(act_doc_id2key, exp_doc_id2key)
            self.assertEqual(act_doc_id2doc, exp_doc_id2doc)

    def test_process_one_doc(self):
        mock_analyzers = [
            get_mock_analyzer('one', '+'),
            get_mock_analyzer('two', '-'),
            get_mock_analyzer('three', '0'),
        ]
        exp_results = ['+', '-', '0']
        exp_accuracy = {'one': 1}
        exp_error_rate = {'two': 2, 'three': 1}
        with patch('compare.ANALYZERS', mock_analyzers), patch('compare.LOGGER'):
            act_results, act_accuracy, act_error_rate = process_one_doc("some text", "+")
            self.assertEqual(act_results, exp_results)
            self.assertEqual(sorted(act_accuracy.items()), sorted(exp_accuracy.items()))
            self.assertEqual(sorted(act_error_rate.items()), sorted(exp_error_rate.items()))

    def test_process_one_doc__deals_with_analyzer_errors(self):
        mock_analyzers = [
            get_mock_analyzer('one', '+'),
            get_mock_analyzer('two', (None, 'Some error msg')),
            get_mock_analyzer('three', '0'),
        ]
        exp_results = ['+', 'Error', '0']
        with patch('compare.ANALYZERS', mock_analyzers), patch('compare.LOGGER'):
            act_results = process_one_doc("some text", "+")[0]
            self.assertEqual(act_results, exp_results)

    def test_initialize_analysers(self):
        analysers_to_use = ['skyttle', 'chatterbox', 'datumbox', 'repustate',
                            'bitext', 'alchemy', 'viralheat', 'semantria']
        config = {
            'mashape_auth': '',
            'language': 'en',
            'datumbox_key': '',
            'repustate_key': '',
            'bitext_user': '',
            'bitext_pwd': '',
            'alchemy_key': '',
            'semantria_consumer_key': '',
            'semantria_consumer_secret': '',
            'viralheat_key': '',
        }
        with patch('compare.ANALYZERS_TO_USE', analysers_to_use):
            initialize_analysers(config)
            self.assertEqual(len(compare.ANALYZERS), len(analysers_to_use))

    def test_evaluate(self):
        exp_accuracy = {'one': 1.0}
        exp_error_rate = {'one': 0.0}
        mock_analyzer = get_mock_analyzer('one', '+')
        mock_process = Mock(return_value=(['+'], Counter({'one': 1}), Counter()))
        doc_id2text = {0: 'Some text.'}
        doc_id2key = {0: '+'}
        with patch('compare.process_one_doc', mock_process), \
                patch('compare.csv'), \
                patch('compare.codecs'), \
                patch('compare.ANALYZERS', [mock_analyzer]):
            act_accuracy, act_error_rate = evaluate(doc_id2text, doc_id2key)
            self.assertEqual(sorted(act_accuracy.items()), sorted(exp_accuracy.items()))
            self.assertEqual(sorted(act_error_rate.items()), sorted(exp_error_rate.items()))

    def test_get_max_weighted_errors(self):
        doc_id2key = {'doc1': '0', 'doc2': '+'}
        actual = get_max_weighted_errors(doc_id2key)
        self.assertEqual(actual, 3.0)
