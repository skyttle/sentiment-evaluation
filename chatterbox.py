
import logging
from api import API


LOGGER = logging.getLogger('APICompare.Chatterbox')


class Chatterbox(API):

    def __init__(self, mashape_auth, language='en', domain=None):
        self.name = 'chatterbox'
        self.language = language
        self.mashape_auth = mashape_auth
        self.url = "https://chatterbox-analytics-sentiment-analysis-free.p.mashape.com/sentiment/current/classify_text/"

    def extract_label(self, score):
        """Given the score, output the label. Ranges {-1, 1}
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
        headers = {'X-Mashape-Authorization': self.mashape_auth}
        data = self.get_data(params, headers)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['value'])
