import logging
from api import API


LOGGER = logging.getLogger('APICompare.Lymbix')


class Lymbix(API):

    def __init__(self, api_key):
        self.name = 'lymbix'
        self.api_key = api_key
        self.url = "http://api.lymbix.com/tonalize"

    def extract_label(self, original_label):
        """Given scores for pos, neg and neu, output the label
        """
        if original_label == 'Positive':
            return '+'
        elif original_label == 'Negative':
            return '-'
        else:
            return '0'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        params = {'article': text, 'return_fields': [u'article_sentiment']}
        headers = {'Authentication': self.api_key,
                   'Accept': 'application/json',
                   'Version': '2.2'}
        data = self.get_data(params, headers)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['article_sentiment']['sentiment'])
