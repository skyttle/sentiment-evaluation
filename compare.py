"""Usage:

python compare.py <path to text file with annotated data> <path to config file>
"""

import sys
import os
import codecs
import csv
import logging
from collections import Counter

from bitext import Bitext
from chatterbox import Chatterbox
from datumbox import Datumbox
from lymbix import Lymbix
from repustate import Repustate
from semantria_api import Semantria
from skyttle import Skyttle
from viralheat import Viralheat
from aiapplied import AIApplied
from sentigem import Sentigem
from thr import Thr


ANALYZERS_TO_USE = [
                    'skyttle',
                    'chatterbox',
                    'datumbox',
                    'repustate',
                    'bitext',
                    'semantria',
                    'viralheat',
                    'lymbix',
                    'aiapplied',
                    'sentigem'
                ]
ANALYZERS = []
LOGGER = None


def setup_logging():
    """Log debug or higher to a file, errors to stderr
    """
    global LOGGER
    fname = 'compare.log'
    if os.path.exists(fname):
         os.unlink(fname)

    format = '%(levelname)s:%(name)s:%(message)s'

    logging.basicConfig(filename=fname, level=logging.DEBUG, format=format)
    LOGGER = logging.getLogger('APICompare')

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.ERROR)
    streamhandler.setFormatter(logging.Formatter(format))

    LOGGER.addHandler(streamhandler)


def read_evaluation_data(fname):
    """Read the gold standard data.
    :return doc_id2doc: document id to the text of the document
    :return doc_id2key: document id to the manually assigned sentiment label
    """
    doc_id2key = {}
    doc_id2doc = {}
    doc_id = 0
    for line in codecs.open(fname, 'r', 'utf8'):
        line = line.strip()
        if not line:
            continue
        try:
            document, key = line.split('\t')
            key = key.strip()
            document = document.strip()
        except ValueError:
            document = line
        if key == 'X':
            continue
        doc_id2key[doc_id] = key
        doc_id2doc[doc_id] = document
        doc_id += 1
    return doc_id2doc, doc_id2key


def read_config(config_fname=None):
    """Read API keys
    """
    config = {}
    if not config_fname:
        config_fname = 'config.txt'
    for line in codecs.open(config_fname, 'r', 'utf8'):
        key, val = line.split('\t')
        config[key.strip()] = val.strip()
    return config


def initialize_analysers(config):
    """Initialise analysers
    """
    if 'skyttle' in ANALYZERS_TO_USE:
        skyttle = Skyttle(mashape_auth=config['mashape_auth'],
                          language=config['language'])
        ANALYZERS.append(skyttle)

    if 'chatterbox' in ANALYZERS_TO_USE:
        chatterbox = Chatterbox(mashape_auth=config['mashape_auth'],
                          language=config['language'])
        ANALYZERS.append(chatterbox)

    if 'datumbox' in ANALYZERS_TO_USE:
        datumbox = Datumbox(api_key=config['datumbox_key'])
        ANALYZERS.append(datumbox)

    if 'repustate' in ANALYZERS_TO_USE:
        repustate = Repustate(api_key=config['repustate_key'])
        ANALYZERS.append(repustate)

    if 'bitext' in ANALYZERS_TO_USE:
        bitext = Bitext(user=config['bitext_user'],
                        password=config['bitext_pwd'],
                        language=config['language'])
        ANALYZERS.append(bitext)

    if 'semantria' in ANALYZERS_TO_USE:
        semantria = Semantria(consumer_key=config['semantria_consumer_key'],
                              consumer_secret=config['semantria_consumer_secret'])
        ANALYZERS.append(semantria)

    if 'viralheat' in ANALYZERS_TO_USE:
        viralheat = Viralheat(api_key=config['viralheat_key'])
        ANALYZERS.append(viralheat)

    if 'lymbix' in ANALYZERS_TO_USE:
        lymbix = Lymbix(api_key=config['lymbix_key'])
        ANALYZERS.append(lymbix)

    if 'aiapplied' in ANALYZERS_TO_USE:
        aiapplied = AIApplied(api_key=config['aiapplied_key'],
                              language=config['language'])
        ANALYZERS.append(aiapplied)

    if 'sentigem' in ANALYZERS_TO_USE:
        sentigem = Sentigem(api_key=config['sentigem_key'])
        ANALYZERS.append(sentigem)

def process_one_doc(text, key):
    """Process one document in all analyzers
    :return result_list: a list of outputs for all analyzers
    :return hits: a Counter with hits for all analyzers
    :return errors: a Counter with errors for all analyzers
    """
    global ANALYZERS

    hits = Counter()
    errors = Counter()
    results = {}
    Thr.outputs = {}
    Thr.inputs = {}

    threads = []
    for analyser in ANALYZERS:
        thr = Thr(analyser, [text])
        threads.append(thr)
        thr.start()
    for thr in threads:
        thr.join()

    for name, output in Thr.outputs.items():
        if isinstance(output, tuple) and not output[0]:
            output = 'Error'
        if output == key:
            hits[name] += 1
        elif output != 'Error':
            if key == '0' or output == '0':
                errors[name] += 1
            else:
                errors[name] += 2
        results[name] = output

    result_list = [results[x.name] for x in ANALYZERS]

    return result_list, hits, errors


def get_max_weighted_errors(doc_id2key):
    """Determine the maximum possible sum of weighted errors
    """
    max_errors = 0
    for gs_key in doc_id2key.values():
        if gs_key == '0':
            max_errors += 1
        else:
            max_errors += 2
    return float(max_errors)


def evaluate(doc_id2text, doc_id2key):
    """Send evaluation documents to each API, output all results into a table,
    and if doc_id2key are available, output accuracy and error rate.
    """
    total_hits = Counter()
    total_errors = Counter()
    accuracy = Counter()
    error_rate = Counter()

    cvswriter = csv.writer(codecs.open('results.csv', 'wb', 'utf8'), delimiter='\t')
    col_names = ['doc_id', 'text', 'gold standard'] + [x.name for x in ANALYZERS]
    cvswriter.writerow(col_names)

    for doc_id, text in sorted(doc_id2text.items()):
        key = doc_id2key.get(doc_id)
        results, doc_hits, doc_errors = process_one_doc(text, key)
        if doc_hits:
            total_hits += doc_hits
        if doc_errors:
            total_errors += doc_errors
        cvswriter.writerow([doc_id, text, key] + results)

    num_docs = float(len(doc_id2text))
    max_errors = get_max_weighted_errors(doc_id2key)

    for analyzer in ANALYZERS:
        name = analyzer.name
        accuracy[name] = total_hits.get(name, 0.0)/num_docs
        error_rate[name] = total_errors.get(name, 0.0)/max_errors

    return accuracy, error_rate


def main(eval_data_fname, config_fname):
    """Main function
    """

    setup_logging()

    # read test data
    doc_id2text, doc_id2key = read_evaluation_data(eval_data_fname)

    # read config
    config = read_config(config_fname)

    # initialise relevant analysers
    initialize_analysers(config)

    # evaluate
    accuracy, error_rate = evaluate(doc_id2text, doc_id2key)

    print "%-15s%s" % ('Analyzer', 'Accuracy')
    for name, score in accuracy.most_common():
        print "%-15s%.3f" % (name, score)
    print
    print "%-15s%s" % ('Analyzer', 'Error rate')
    for name, score in reversed(error_rate.most_common()):
        print "%-15s%.3f" % (name, score)


if __name__ == "__main__":

    eval_data_fname = None
    config_fname = None

    if len(sys.argv) > 1:
        eval_data_fname = sys.argv[1]
        if len(sys.argv) == 3:
            config_fname = sys.argv[2]
    else:
        raise Exception("Please specify the path to the file with evaluation data")

    main(eval_data_fname, config_fname)
