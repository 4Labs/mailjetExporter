from prometheus_client.core import GaugeMetricFamily
from mailjet_rest import Client

import re
import logging
import datetime

class MailjetCollector(object):

  def __init__(self, api_key, secret_key, billing_day):
        """ initializing attributes"""
        self.api_key = api_key
        self.api_secret = secret_key
        self.billing_day = billing_day

        self.METRIC_PREFIX = 'mailjet_info_'

  def convertCamelToSnake(self, name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


  def getPeriodTotalSent(self, mailjet, from_date, to_date):
      # billing period stats
      r = mailjet.statcounters.get(filters={
          'CounterSource': 'APIKey',
          'CounterResolution': 'Day',
          'CounterTiming': 'Message',
          'FromTS': from_date.strftime("%Y-%m-%dT%H:%M:%S"),
          'ToTS': to_date.strftime("%Y-%m-%dT%H:%M:%S"),
          'Limit': 1000 # Max allowed
      })

      try:
          datas = r.json()['Data']
      except:
          logging.error(r.status_code)
          logging.error(r.json())
          exit(1)

      # Sum up the results
      MessageSentCount = 0

      for data in datas:
          # data should be like:
          # {'APIKeyID': 1567499, 'EventClickDelay': 0, 'EventClickedCount': 0, 'EventOpenDelay': 3358531, 'EventOpenedCount': 529, 'EventSpamCount': 0, 'EventUnsubscribedCount': 0, 'EventWorkflowExitedCount': 0, 'MessageBlockedCount': 20, 'MessageClickedCount': 0, 'MessageDeferredCount': 0, 'MessageHardBouncedCount': 20, 'MessageOpenedCount': 244, 'MessageQueuedCount': 1, 'MessageSentCount': 2821, 'MessageSoftBouncedCount': 1, 'MessageSpamCount': 0, 'MessageUnsubscribedCount': 0, 'MessageWorkFlowExitedCount': 0, 'SourceID': 0, 'Timeslice': '2021-03-11T00:00:00Z', 'Total': 2863}
          MessageSentCount += data['MessageSentCount']

      name_attribute = self.convertCamelToSnake('BillingPeriodTotalSent')
      gauge = GaugeMetricFamily(self.METRIC_PREFIX + name_attribute, 'total sent this period',
                                value=MessageSentCount)
      return gauge


  '''
  Collect stats for the billing period
  '''
  def collectMonthStats(self, mailjet):
      now = datetime.date.today()

      # From this month or previous month ?
      if (now.day <= self.billing_day):
          from_date = datetime.date(now.year, now.month - 1, self.billing_day)
      else:
          from_date = datetime.date(now.year, now.month, self.billing_day)

      yield self.getPeriodTotalSent(mailjet, from_date, now)



  def collectLifetimeStats(self, mailjet):
      metric_description = 'Mailjet number %s'
      r = mailjet.statcounters.get(filters={
          'CounterSource': 'APIKey',
          'CounterResolution': 'LifeTime',
          'CounterTiming': 'Message'
      })

      try:
          datas = r.json()['Data']
      except:
          logging.error(r.status_code)
          logging.error(r.json())
          exit(1)

      for data in datas:
          for attribute, value in data.items():
              if (value == ''):
                  value = 0

              name_attribute = self.convertCamelToSnake(attribute)
              gauge = GaugeMetricFamily(self.METRIC_PREFIX + name_attribute, metric_description % name_attribute,
                                        value=value)
              yield gauge


  def collect(self):

    mailjet = Client(auth=(self.api_key, self.api_secret), version='v3')

    # That gives a daily send count for the 31 last days
    for metric in self.collectMonthStats(mailjet):
        yield metric

    for metric in self.collectLifetimeStats(mailjet):
        yield metric
