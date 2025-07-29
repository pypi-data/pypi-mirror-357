import requests as req
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from socket import gethostbyname, socket, timeout
import tldextract

urls = set()
lock = Lock()

http = ""
https = ""

def wispscan(ports, urls):
    def scan_port(ip, port):
        try:
            with socket() as s:
                s.settimeout(0.2)
                s.connect((ip, port))
                return True
        except (timeout, ConnectionRefusedError, OSError):
            return False

    def worker(url):
        try:
            parsed_url = urlparse(url)
            ip = gethostbyname(parsed_url.hostname)
            open_ports = [port for port in ports if scan_port(ip, port)]
            if open_ports:
                with lock:
                    with open("ports.out", "a") as port_file:
                        for port in open_ports:
                            port_file.write(f"{ip}:{port}\n")
        except Exception as e:
            print(f"[ERROR] Port scan failed for {url}: {e}")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(worker, url) for url in urls]
        for f in futures:
            f.result()

def get_links(URL):
    found = set()
    try:
        response = req.get(URL, timeout=0.3)
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

    with open(http_path, "a") as http_file, open(https_path, "a") as https_file:
        for link in urls_set:
            formatted = f"<[{link}]>\n"
            if link.startswith("http://"):
                http_file.write(formatted)
            elif link.startswith("https://"):
                https_file.write(formatted)

def _send_webhook(url, data):
    try:
        headers = {"Content-Type": "text/plain"}
        r = req.post(url, data=data.encode('utf-8'), headers=headers, timeout=1)
        if r.status_code >= 400:
            print(f"[WARN] Webhook {url} returned status {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Sending to webhook {url}: {e}")

def cringio_cli(start_url=None,
                url_file=None,
                max_workers=10,
                infinite=True,
                max_urls_from_file=None,
                http_webhook=None,
                https_webhook=None,
                webhook=None,
                sub_webhook=None,
                ports_webhook=None,
                ports=None):
    global urls, http, https

    if ports is None:
        ports = list(range(1, 20001))

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

                wispscan(ports, urls)

                if ports_webhook:
                    try:
                        with open("ports.out", "r") as f:
                            ports_data = f.read()
                        _send_webhook(ports_webhook, ports_data)
                    except FileNotFoundError:
                        print("[ERROR] ports.out not found.")

                if not infinite:
                    break

    except KeyboardInterrupt:
        print("\n[INFO] Scan interrupted by user.")
