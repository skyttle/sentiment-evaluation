
import logging
from api import API

LOGGER = logging.getLogger('APICompare.Skyttle')


class Skyttle(API):

    def __init__(self, mashape_auth, language='en', domain=None):
        self.name = 'skyttle'
        self.language = language
        self.domain = domain
        self.mashape_auth = mashape_auth
        self.url = "https://sentinelprojects-skyttle20.p.mashape.com/"

    def extract_label(self, scores):
        """Given scores for pos, neg and neu, output the label
        """
        if scores['pos'] == scores['neg']:
            return '0'
        elif scores['pos'] > scores['neg']:
            return '+'
        else:
            return '-'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        params = {'text': text, 'lang': self.language, 'keywords': 0,
                  'sentiment': 1}
        if self.domain:
            params['domain'] = self.domain
        headers = {'X-Mashape-Authorization': self.mashape_auth}
        data = self.get_data(params, headers)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['docs'][0]['sentiment_scores'])
