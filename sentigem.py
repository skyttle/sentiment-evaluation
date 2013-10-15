import logging
from api import API


LOGGER = logging.getLogger('APICompare.Sentigem')


class Sentigem(API):

    def __init__(self, api_key):
        self.name = 'sentigem'
        self.api_key = api_key
        self.url = "https://api.sentigem.com/external/get-sentiment"

    def extract_label(self, label):
        """Given scores for pos, neg and neu, output the label
        """
        if label == 'positive':
            return '+'
        elif label == 'negative':
            return '-'
        else:
            return '0'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        params = {'text': text, 'api-key': self.api_key}
        data = self.get_data(params)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['polarity'])
