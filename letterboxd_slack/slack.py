import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def _get_slack_client():
    return WebClient(token=os.environ['SLACK_TOKEN'])

def notify_review(channel, review):
    print(f"Notifying {channel} about {review}")
    client = _get_slack_client()
    try:
        response = client.chat_postMessage(
            channel=channel,
            blocks=format_message(review)
        )
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")

def format_message(review):
    review_text = review.review_text
    user = review.user
    prelude = f"New <{review.review_link}|review> from <https://letterboxd.com/{user}|{user}>"
    title_and_score = f"_{review.film_name}_ - {review.score}"
    if review.has_spoilers:
        review_text = "This review has spoilers. View on letterboxd to read it."
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{prelude}: {title_and_score}",
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": review_text,
            }
        },
    ]
