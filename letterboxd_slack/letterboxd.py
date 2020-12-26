from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional, Sequence

from bs4 import BeautifulSoup
import requests

BASE_URL = "https://letterboxd.com/"
RECENT_REVIEWS_PATH = "/films/reviews/by/added"
SPOILER_WARNING_TEXT = "This review may contain spoilers. I can handle the truth."

@dataclass
class Review:
    film_name: str
    review_text: str
    review_link: str
    has_spoilers: bool
    user: str
    score: str


def get_users_and_last_review_markers() -> Dict[str, Optional[str]]:
    """
    Mapping of followed users to the identifier of their last scraped review
    """
    return {
        "benmusch": "https://letterboxd.com/benmusch/film/wolfwalkers/"
    }

def get_new_reviews() -> Sequence[Review]:
    reviews = []
    for username, marker in get_users_and_last_review_markers().items():
        # assumption: cron runs faster than user submits reviews, no need to paginate
        reviews += get_new_reviews_for_user(username, marker)
    return reviews

def get_new_reviews_for_user(username: str, until_marker: str) -> Sequence[Review]:
    resp = requests.get(f"{BASE_URL}{username}{RECENT_REVIEWS_PATH}")
    if not resp.ok:
        print(f"Error fetching reviews for {username}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    reviews = []

    for review_li in soup.select("ul.film-list li.film-detail"):
        title_node = review_li.select_one(".headline-2 a")
        review_body_node = review_li.select_one(".body-text")
        score_node = review_li.select_one(".rating")

        review_link = f"{BASE_URL}{title_node['href'][1:]}"
        if review_link == until_marker: break

        film_name = title_node.text.strip()
        review_text = review_body_node.text.strip()
        score = score_node.text.strip() if score_node else "(no score)"
        has_spoilers = SPOILER_WARNING_TEXT in review_text

        if has_spoilers:
            review_text = review_text.replace(SPOILER_WARNING_TEXT, "").strip()

        review = Review(film_name,
                review_text,
                review_link,
                has_spoilers,
                username,
                score)

        reviews += [review]

    return reviews
