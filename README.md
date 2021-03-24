
# Prometheus mailjet exporter

Manage your MailJet API keys: https://app.mailjet.com/account/api_keys

## Deploy in stack

Provide api_key and secret_key as docker secrets.

## Development environment

Use provided docker-compose file to start.

```shell
cp docker-compose.yaml{.dist,}
## EDIT docker-compose file ##
docker-compose up
```

