import re


SORT_MODES = ("mostrecent", "mosthelpful")
REVIEWS_PER_PAGE = 50
MAX_PAGES_PER_SORT = 5

APP_STORE_URL_PATTERN = re.compile(
    r"apps\.apple\.com/(?P<country>[a-z]{2})/app/[^/]+/id(?P<app_id>\d+)",
    re.IGNORECASE,
)

MULTIPLE_SPACES = re.compile(r"\s+")
URL_PATTERN = re.compile(r"https?://\S+")

MIN_MEANINGFUL_WORDS = 3
