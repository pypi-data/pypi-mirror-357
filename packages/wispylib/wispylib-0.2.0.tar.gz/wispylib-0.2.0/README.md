# wispylib
A prototype for a crawling module


<h3>USAGE:</h3>

```python
from wispylib import cringio, cringio_cli

# Simple single URL scan, send both http+https to one webhook:
cringio("https://example.com", webhook="https://myhook.site/abcdef")

# Customizable infinite scan with file + separate webhooks:
cringio_cli(url_file="urls.txt", max_workers=20, infinite=True, delay=10,
            http_webhook="https://hook1.site/abc", https_webhook="https://hook2.site/xyz")
```

