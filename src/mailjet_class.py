from prometheus_client.core import GaugeMetricFamily
from mailjet_rest import Client

import re

class MailjetCollector(object):

  def __init__(self, api_key, secret_key):
        """ initializing attributes"""
        self.api_key = api_key
        self.api_secret = secret_key

        self.METRIC_PREFIX = 'mailjet_info_'

  def convertCamelToSnake(self, name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

  def collect(self):
    metric_description = 'Mailjet number %s'
    filters = {
        'CounterSource': 'APIKey',
        'CounterResolution': 'LifeTime',
        'CounterTiming': 'Message'
    }
    mailjet = Client(auth=(self.api_key, self.api_secret), version='v3')
    r = mailjet.statcounters.get(filters=filters)
    datas = r.json()['Data']

    for data in datas:
        for attribute, value in data.items():
            if (value == ''):
                value = 0

            name_attribute = self.convertCamelToSnake(attribute)
            gauge = GaugeMetricFamily(self.METRIC_PREFIX + name_attribute, metric_description % name_attribute, value=value)
            yield gauge
