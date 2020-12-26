from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional, Sequence

from bs4 import BeautifulSoup
import requests

BASE_URL = "https://letterboxd.com/"
RECENT_REVIEWS_PATH = "/films/reviews/by/added"
SPOILER_WARNING_TEXT = "This review may contain spoilers. I can handle the truth."

response_cache = {}

@dataclass
class Review:
    film_name: str
    review_text: str
    review_link: str
    has_spoilers: bool
    user: str
    score: str

def get_most_recent_marker(username: str) -> str:
    all_reviews = _fetch_reviews_li(username)
    if not all_reviews: return None
    return _review_from_li(all_reviews[0], username).review_link

def get_new_reviews_for_user(username: str, until_marker: str) -> Sequence[Review]:
    print(f"Getting new reviews for {user}")
    reviews = []
    for li in _fetch_reviews_li(username):
        review = _review_from_li(li, username)
        if review.review_link == until_marker: break
        reviews += [review]
    return reviews

def _fetch_reviews_li(username: str):
    url = f"{BASE_URL}{username}{RECENT_REVIEWS_PATH}/"
    if url not in response_cache:
        resp = requests.get(url)
        if not resp.ok:
            print(f"Error fetching reviews for {username}")
            return []
        response_cache[url] = resp
    else:
        print(f"Using cache for {username}")
        resp = response_cache[url]

    soup = BeautifulSoup(resp.content, "html.parser")
    return soup.select("ul.film-list li.film-detail")

def _review_from_li(review_li, username) -> Review:
    title_node = review_li.select_one(".headline-2 a")
    review_body_node = review_li.select_one(".body-text")
    score_node = review_li.select_one(".rating")

    review_link = f"{BASE_URL}{title_node['href'][1:]}"
    print(f"Examining {review_link}")
    film_name = title_node.text.strip()
    review_text = review_body_node.text.strip()
    score = score_node.text.strip() if score_node else "(no score)"
    has_spoilers = SPOILER_WARNING_TEXT in review_text

    if has_spoilers:
        review_text = review_text.replace(SPOILER_WARNING_TEXT, "").strip()

    return Review(film_name,
                  review_text,
                  review_link,
                  has_spoilers,
                  username,
                  score)
