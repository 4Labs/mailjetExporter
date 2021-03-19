from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

import json, sys, time, os, signal, logging


from mailjet_class import MailjetCollector


def sigterm_handler(_signo, _stack_frame):
  sys.exit(0)

if __name__ == '__main__':

  # Check for required env vars
  if not (os.getenv('SECRET_KEY') or os.getenv('API_KEY')):
    print("SECRET_KEY or API_KEY missing, exiting")
    exit(1)

  bind_port = int(os.getenv('BIND_PORT', 80))
  start_http_server(bind_port)
  logging.warning('Starting listen on {0} '.format(bind_port))

  REGISTRY.register(MailjetCollector(
      api_key=os.getenv('API_KEY'),
      secret_key=os.getenv('SECRET_KEY')
    )
  )

  signal.signal(signal.SIGTERM, sigterm_handler)
  while True: time.sleep(1)
