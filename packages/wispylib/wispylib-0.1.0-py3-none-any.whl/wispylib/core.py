import requests as req
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urls = set()
lock = Lock()

http = ""  # holds contents of http.out after cringio
https = ""


def get_links(URL):
    found = set()
    try:
        response = req.get(URL, timeout=1)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all('a'):
            if isinstance(link, Tag):
                href = link.get('href')
                if href:
                    full = urljoin(URL, str(href))
                    found.add(full)
    except Exception as e:
        print(f"[ERROR] {URL}: {e}")
    return found


def test_redirects(URL):
    redirects = set()
    try:
        r = req.get(URL, allow_redirects=True, timeout=1)
        for resp in r.history:
            redirects.add(resp.url)
    except Exception as e:
        print(f"[ERROR] Redirects for {URL}: {e}")
    return redirects


def save_links(http_path="http.out", https_path="https.out", urls_set=None):
    if urls_set is None:
        print("[ERROR] No URLs provided to save.")
        return

    with open(http_path, "a") as http_file, open(https_path,
                                                 "a") as https_file:
        for link in urls_set:
            formatted = f"<[{link}]>\n"
            if link.startswith("http://"):
                http_file.write(formatted)
            elif link.startswith("https://"):
                https_file.write(formatted)


def _send_webhook(url, data):
    try:
        headers = {"Content-Type": "text/plain"}
        r = req.post(url,
                     data=data.encode('utf-8'),
                     headers=headers,
                     timeout=1)
        if r.status_code >= 400:
            print(f"[WARN] Webhook {url} returned status {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Sending to webhook {url}: {e}")


def cringio(start_url,
            max_workers=10,
            scan_loops=1,
            http_webhook=None,
            https_webhook=None,
            webhook=None):
    """
    If webhook is set, both http and https contents are sent there.
    Otherwise, sends http and https separately if their webhook URLs are provided.
    """
    global urls, http, https

    def worker(url):
        found = get_links(url)
        redirs = test_redirects(url)
        with lock:
            urls.update(found)
            urls.update(redirs)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _ in range(scan_loops):
            futures.append(executor.submit(worker, start_url))
        for f in futures:
            f.result()

    save_links(urls_set=urls)

    try:
        with open("http.out", "r") as f:
            http = f.read()
    except FileNotFoundError:
        http = ""

    try:
        with open("https.out", "r") as f:
            https = f.read()
    except FileNotFoundError:
        https = ""

    if webhook:
        _send_webhook(webhook, http + "\n" + https)
    else:
        if http_webhook and http:
            _send_webhook(http_webhook, http)
        if https_webhook and https:
            _send_webhook(https_webhook, https)


def cringio_cli(start_url=None,
                url_file=None,
                max_workers=10,
                infinite=True,
                max_urls_from_file=None,
                delay=0.5,
                http_webhook=None,
                https_webhook=None,
                webhook=None):
    """
    Parameters:
    - start_url: str, single URL to scan (ignored if url_file provided)
    - url_file: str, path to file with URLs (one per line)
    - max_workers: int, number of threads
    - infinite: bool, run forever until interrupted
    - max_urls_from_file: int or None, limit URLs from file
    - delay: seconds to wait between loops
    - http_webhook / https_webhook / webhook: webhook URLs for POST
    """
    global urls, http, https

    def worker(url):
        found = get_links(url)
        redirs = test_redirects(url)
        with lock:
            urls.update(found)
            urls.update(redirs)

    url_list = []
    if url_file:
        try:
            with open(url_file, "r") as f:
                url_list = [line.strip() for line in f if line.strip()]
            if max_urls_from_file is not None:
                url_list = url_list[:max_urls_from_file]
        except Exception as e:
            print(f"[ERROR] Could not read URL file: {e}")
            return
    elif start_url:
        url_list = [start_url]
    else:
        print("[ERROR] Must provide start_url or url_file")
        return

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while True:
                futures = [executor.submit(worker, url) for url in url_list]
                for f in futures:
                    f.result()

                save_links(urls_set=urls)

                try:
                    with open("http.out", "r") as f:
                        http = f.read()
                except FileNotFoundError:
                    http = ""

                try:
                    with open("https.out", "r") as f:
                        https = f.read()
                except FileNotFoundError:
                    https = ""

                if webhook:
                    _send_webhook(webhook, http + "\n" + https)
                else:
                    if http_webhook and http:
                        _send_webhook(http_webhook, http)
                    if https_webhook and https:
                        _send_webhook(https_webhook, https)

                if not infinite:
                    break

                print(f"[INFO] Waiting {delay} seconds before next scan...")

    except KeyboardInterrupt:
        print("\n[INFO] Scan interrupted by user.")