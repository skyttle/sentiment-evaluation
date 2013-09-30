import urllib, urllib2, json
import logging
import time


LOGGER = logging.getLogger('APICompare.Viralheat')


class Viralheat:

    def __init__(self, api_key):
        self.name = 'viralheat'
        self.api_key = api_key
        self.url = "https://app.viralheat.com/social/api/sentiment"

    def extract_label(self, label, prob):
        """Given scores for pos, neg and neu, output the label
        """
        if prob < 0.1:
            return '0'
        label = label.replace("'", "")
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
        # the API allows 1 call per 5 seconds
        time.sleep(5)
        # the API allows max 360 char long texts
        if len(text) > 360:
            LOGGER.warning('The input text is over the 360 char limit, truncated')
            text = text[360:]
        params = {'text': text, 'api_key': self.api_key}
        request = urllib2.Request(self.url, urllib.urlencode(params))
        response = urllib2.urlopen(request)
        data = json.loads(response.read())
        LOGGER.debug('Got response %r' % data)
        return self.extract_label(data['mood'], data['prob'])
