import openmeteo_requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(
    ".cache",
    expire_after=3600,
    #backend="filesystem"
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo_client = openmeteo_requests.Client(
    session=retry_session
)
