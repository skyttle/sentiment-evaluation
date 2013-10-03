import json
import logging
from api import API

LOGGER = logging.getLogger('APICompare.AIApplied')


class AIApplied(API):

    def __init__(self, api_key, language="en"):
        self.name = "AIApplied"
        self.api_key = api_key
        self.url = "http://api.ai-applied.nl/api/sentiment_api/"
        self.language_mapping = {
            'en': 'eng',
            'nl': 'nld',
            'de': 'deu',
            'fr': 'fra',
            'es': 'spa',
            'it': 'ita',
            'ru': 'rus'
        }
        self.language = self.language_mapping[language]

    def extract_label(self, original_label):
        """Given scores for pos, neg and neu, output the label
        """
        if original_label == 'positive':
            return '+'
        elif original_label == 'negative':
            return '-'
        else:
            return '0'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        request = {"data": {
                            "api_key": self.api_key,
                            "call": {
                                    "return_original": False,
                                    "classifier": "subjective",
                                    "data": [
                                        {
                                            "text": text,
                                            "language_iso": self.language,
                                            "id": 0
                                        }
                                    ]
                                }
                            }
            }
        params = {'request': json.dumps(request)}
        data = self.get_data(params)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data["response"]["data"][0]['sentiment_class'])
