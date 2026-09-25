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


KEYWORD_TO_INSIGHT = {
    "crash": "Users report frequent crashes — prioritize stability and crash-reporting fixes.",
    "freeze": "Freezing issues detected — investigate performance bottlenecks under load.",
    "login": "Login-related complaints found — review authentication flow and error handling.",
    "slow": "Multiple mentions of slowness — consider performance profiling and optimization.",
    "battery": "Battery drain complaints — audit background processes and wake locks.",
    "support": "Customer support dissatisfaction noted — review response time and support quality.",
    "bug": "General bug reports present — increase QA coverage before releases.",
    "ads": "Users are annoyed by ads — reconsider ad frequency or placement.",
    "price": "Pricing concerns raised — review pricing strategy or communicate value more clearly.",
    "update": "Update-related issues — verify backward compatibility and rollout process.",
}

DEFAULT_INSIGHT = (
    "Review the most common negative keywords manually for deeper context."
)

POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

SORT_MODES = ("mostrecent", "mosthelpful")
REVIEWS_PER_PAGE = 50
MAX_PAGES_PER_SORT = 5

METHODS = ["vader", "classical", "bert"]
TEMPLATE_DIR = "app/templates"
