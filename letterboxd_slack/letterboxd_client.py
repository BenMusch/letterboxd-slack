from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional, Sequence

import requests

BASE_URL = "https://letterboxd.com/"
RECENT_REVIEWS_PATH = "/films/reviews/by/added"

@dataclass
class Review:
    film_name: str
    film_link: str
    review_text: str
    review_link: str
    score: Optional[float]


def get_users_and_last_review_markers() -> Dict[str, str]:
    """
    Mapping of followed users to the identifier of their last scraped review
    """
    return {
        "benmusch": "/film/green-book"
    }

def get_new_reviews() -> Sequence[Review]:
    for username, marker in get_users_and_last_review_markers():
        requests.get(BASE_URL + username + RECENT_REVIEWS_PATH)
        import pdb; pdb.set_trace()
