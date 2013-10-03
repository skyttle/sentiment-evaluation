"""An abstract class for all APIs accepting POST and returning JSON
"""

import urllib
import urllib2
import json


class API:

    def __init__(self):
        self.name = None
        self.url = None

    def get_data(self, params, headers=None):
        """Send a POST request, get a JSON response and return the data
        """
        if not headers:
            headers = {}
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(self.url, urllib.urlencode(params),
                                  headers=headers)
        response = opener.open(request)
        opener.close()
        contents = response.read()
        data = json.loads(contents)
        return data
