import json
import base64
import hmac
import hashlib
import requests
from scrapy.http import HtmlResponse


class AskPablosScrapyAPI:
    """
    Scrapy middleware to route selected requests through AskPablos proxy API.

    This middleware activates **only** for requests that include:
        meta = {
            "askpablos_api_map": {
                "browser": True,          # Optional: Use headless browser
                "rotate_proxy": True      # Optional: Use rotating proxy IP
            }
        }

    It will bypass any request that does not include the `askpablos_api_map` key or has it as an empty dict.

    Configuration (via settings.py or `CUSTOM_SETTINGS`):
        API_KEY      = "<your API key>"
        SECRET_KEY   = "<your secret key>"
    """

    API_URL = "http://10.10.10.178:7500/api/proxy/"

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("API_KEY")
        secret_key = crawler.settings.get("SECRET_KEY")

        if not api_key or not secret_key:
            raise ValueError("API_KEY and SECRET_KEY must be defined in settings.")

        return cls(api_key=api_key, secret_key=secret_key)

    def process_request(self, request, spider):
        proxy_cfg = request.meta.get("askpablos_api_map")

        if not proxy_cfg or not isinstance(proxy_cfg, dict) or not proxy_cfg:
            return None  # Skip proxying

        browser = proxy_cfg.get("browser", False)
        rotate_proxy = proxy_cfg.get("rotate_proxy", False)

        payload = {
            "url": request.url,
            "method": "GET",
            "browser": browser,
            "rotateProxy": rotate_proxy
        }

        try:
            request_json = json.dumps(payload, separators=(',', ':'))
            signature = hmac.new(
                self.secret_key.encode(),
                request_json.encode(),
                hashlib.sha256
            ).digest()
            signature_b64 = base64.b64encode(signature).decode()

            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "X-Signature": signature_b64
            }

            response = requests.post(self.API_URL, data=request_json, headers=headers, timeout=30)
            response.raise_for_status()

            try:
                proxy_response = response.json()
            except ValueError:
                spider.logger.error(f"[AskPablos API] Invalid JSON response from {self.API_URL}")
                return None

            html_body = proxy_response.get("body")
            if not html_body:
                spider.logger.error(f"[AskPablos API] No 'body' in response for {request.url}")
                return None

            return HtmlResponse(
                url=request.url,
                body=html_body,
                encoding="utf-8",
                request=request
            )

        except Exception as e:
            spider.logger.error(f"[AskPablos API] Error processing {request.url}: {e}")
            return None
