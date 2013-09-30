import logging
from api import API


LOGGER = logging.getLogger('APICompare.Repustate')


class Repustate(API):

    def __init__(self, api_key, language='en'):
        """:param language: one of: en, ar, zh, de, fr, es, it
        """
        self.name = 'repustate'
        self.language = language
        self.url = "http://api.repustate.com/v2/%s/score.json" % api_key

    def extract_label(self, score):
        """Given the score, output the label
        """
        if -0.2 < score < 0.2:
            return '0'
        elif score > 0.2:
            return '+'
        else:
            return '-'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        params = {'text': text, 'lang': self.language}
        data = self.get_data(params)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['score'])
