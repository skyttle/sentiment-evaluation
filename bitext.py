import logging
from api import API


LOGGER = logging.getLogger('APICompare.Bitext')
LANGUAGE_MAPPING = {
    'en': 'Eng',
    'es': 'Esp',
    'pt': 'Por',
    'it': 'Ita',
}


class Bitext(API):

    def __init__(self, user, password, language='en'):
        """:param language: en, es, pt, it
        """
        self.name = 'bitext'
        self.user = user
        self.password = password
        self.language = LANGUAGE_MAPPING[language]
        self.url = "http://svc8.bitext.com/WS_NOps_Val/Service.aspx"

    def extract_label(self, score):
        """Given the score, output the label. Ranges {-2, 2}
        """
        if -0.4 < score < 0.4:
            return '0'
        elif score > 0.4:
            return '+'
        else:
            return '-'

    def analyse(self, text):
        """Assign the sentiment label for the text.
        :return label: +, -, or 0
        """
        params = {
            'User': self.user,
            'Pass': self.password,
            'Text': text,
            'Lang': self.language,
            'ID': 0,
            'Detail': 'Global',
            'OutFormat': 'JSON',
            'Normalized': 'Both'
        }
        data = self.get_data(params)
        LOGGER.debug("Got response: %r" % data)
        return self.extract_label(data['data'][0]['global_value'])
