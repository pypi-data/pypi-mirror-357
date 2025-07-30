spaceship-api
#############

API client for https://www.spaceship.com/


Usage
*****

Install this package

```
pip install spaceship-api
```

.. code-block:: python3

    from spaceship_api.dns_records_types import DNSRecordTypeAdapter
    from spaceship_api.client import SpaceshipApiClient

    api_client = SpaceshipApiClient(api_key="SzhR...", api_secret="LXWT...")

    dns_records = api_client.get_dns_records("yourdomain.xyz")

    for dns_record in dns_records:
        print(dns_record)
