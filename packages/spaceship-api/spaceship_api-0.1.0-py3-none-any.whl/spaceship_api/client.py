import logging
import os
from typing import List, Optional

import requests

from .dns_records_types import DNSRecord, DNSRecordTypeAdapter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SpaceshipApiClient:
    API_BASE_URL = "https://spaceship.dev/api/v1"

    def __init__(
        self,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ):
        self.api_base_url = api_base_url or self.API_BASE_URL
        self.api_key = api_key or os.getenv("SPACESHIP_API_KEY")
        self.api_secret = api_secret or os.getenv("SPACESHIP_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret must be provided or set in environment variables.")

        self.headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "accept": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.api_base_url}{path}"
        try:
            resp = requests.request(method, url, headers=self.headers, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Request to {url} failed: {e}")
            raise

        if not resp.ok:
            logger.error(f"{method.upper()} {url} failed ({resp.status_code}): {resp.text}")
        return resp

    def get_dns_records(self, domain: str) -> List[DNSRecord]:
        """
        Fetch current DNS records for the domain.
        """
        resp = self._request("get", f"/dns/records/{domain}?take=100&skip=0")
        if not resp.ok:
            return []
        try:
            items = resp.json().get("items", [])
            records = [DNSRecordTypeAdapter.validate_python(item) for item in items]
            logger.info(f"Retrieved {len(records)} records for {domain}")
            return records
        except Exception as e:
            logger.error(f"Failed to parse DNS records: {e}")
            return []

    def update_dns_records(self, domain: str, records: List[DNSRecord]) -> bool:
        """
        Replace all DNS records for the domain.
        """
        payload = {"items": [r.model_dump() for r in records]}
        resp = self._request("put", f"/dns/records/{domain}", json=payload)
        if resp.ok:
            logger.info(f"DNS records updated for {domain}")
        return resp.ok

    def delete_dns_records(self, domain: str, records: List[DNSRecord]) -> bool:
        """
        Delete DNS records for the domain.
        """
        payload = [r.model_dump() for r in records]
        resp = self._request("delete", f"/dns/records/{domain}", json=payload)
        if resp.ok:
            logger.info(f"DNS records deleted for {domain}")
        return resp.ok
