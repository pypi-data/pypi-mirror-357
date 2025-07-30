# AskPablos Scrapy API

**AskPablosScrapyAPI** is a seamless integration for Scrapy that allows your spiders to route specific requests through the AskPablos proxy service. It supports headless browser rendering and rotating proxies on a per-request basis, while integrating cleanly with Scrapy's native settings system.

---

## 🚀 Features

- ✅ Selective request routing - only processes requests you explicitly flag
- ✅ Supports rotating proxies and headless browser rendering
- ✅ Compatible with per-spider `CUSTOM_SETTINGS`
- ✅ Automatic HMAC request signing for security
- ✅ Clean plug-and-play design for reuse across Scrapy projects

---

## 📦 Installation

Install via pip:

```bash
pip install askpablos-scrapy-api
```

Or directly from the repository:

```bash
pip install git+https://github.com/fawadss1/askpablos-scrapy-api.git
```

---

## 🔧 Quick Setup

1. Add AskPablosScrapyAPI to your Scrapy project using `CUSTOM_SETTINGS` (can be used in settings.py or spider file):

```python
# Using in settings.py or spider file
CUSTOM_SETTINGS = {
    "DOWNLOADER_MIDDLEWARES": {
        "askpablos_scrapy_api.AskPablosScrapyAPI": 543,
    },
    "API_KEY": "your-api-key",
    "SECRET_KEY": "your-secret-key"
}
```

2. Use in your spider by adding `askpablos_api_map` to the request meta:

```python
def start_requests(self):
    yield scrapy.Request(
        url="https://example.com",
        callback=self.parse,
        meta={
            "askpablos_api_map": {
                "browser": True,        # Use headless browser
                "rotate_proxy": True    # Use rotating proxy IP
            }
        }
    )
```

---

## 📚 Documentation

For detailed usage instructions and advanced configurations:

- [Usage Guide](https://github.com/fawadss1/askpablos-scrapy-api/blob/main/docs/usage.md)
- [FAQ](https://github.com/fawadss1/askpablos-scrapy-api/blob/main/docs/faq.md)

---

## 📋 Requirements

- Python 3.7+
- Scrapy 2.6+
- Valid AskPablos Proxy API credentials

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

Fawad Ali ([@fawadss1](https://github.com/fawadss1))
