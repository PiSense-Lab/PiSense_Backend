import openmeteo_requests
import requests_cache
from retry_requests import retry
import os

# Cached + retry session
cache_dir = os.path.dirname(os.path.realpath(__file__))
cache_path = os.path.join(cache_dir, '.cache')

cache_session = requests_cache.CachedSession(
    cache_path,
    expire_after=3600,
    backend="sqlite"
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo_client = openmeteo_requests.Client(
    session=retry_session
)
