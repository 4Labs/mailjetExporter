from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

import json, sys, time, os, signal, logging

from mailjet_class import MailjetCollector
from get_docker_secret import get_docker_secret

def sigterm_handler(_signo, _stack_frame):
  sys.exit(0)

if __name__ == '__main__':

  api_key = get_docker_secret('api_key', getenv=True, autocast_name=False)
  secret_key = get_docker_secret('secret_key', getenv=True, autocast_name=False)

  # Check for required env vars
  if api_key is None or secret_key is None:
    logging.error('api_key and secret_key required')
    exit(1)

  bind_port = int(os.getenv('BIND_PORT', 80))
  start_http_server(bind_port)
  logging.warning('Starting listen on {0} '.format(bind_port))

  REGISTRY.register(MailjetCollector(
      api_key=api_key,
      secret_key=secret_key
    )
  )

  signal.signal(signal.SIGTERM, sigterm_handler)
  while True: time.sleep(1)
