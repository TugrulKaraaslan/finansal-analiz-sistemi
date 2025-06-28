import requests
import urllib3

session = requests.Session()
retry = urllib3.util.retry.Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[502, 503, 504],
)
adapter = requests.adapters.HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


def http_get(url, **kwargs):
    return session.get(url, timeout=5, **kwargs)


def http_post(url, **kwargs):
    return session.post(url, timeout=5, **kwargs)
