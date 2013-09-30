"""Based on https://semantria.com/download/documents/Semantria_API_Quick_Start_Guide.pdf
"""

import semantria
import uuid
import time
import logging


LOGGER = logging.getLogger('APICompare.Semantria')


def onError(sender, result):
    LOGGER.error(result)



class Semantria:

    def __init__(self, consumer_key, consumer_secret):
        self.name = 'semantria'
        serializer = semantria.JsonSerializer()
        self.session = semantria.Session(consumer_key, consumer_secret, serializer)
        self.session.Error += onError

    def extract_label(self, score):
        """Given scores for pos, neg and neu, output the label
        """
        if score > 0.0:
            return '+'
        elif score < 0.0:
            return '-'
        else:
            return '0'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        doc = {"id": str(uuid.uuid1()).replace("", ""), "text": text}
        status = self.session.queueDocument(doc)
        time.sleep(5)
        status = self.session.getProcessedDocuments()
        while not isinstance(status, list):
            status = self.session.getProcessedDocuments()
        LOGGER.debug("Got response: %r" % status)
        score = status[0]['sentiment_score']
        return self.extract_label(score)
