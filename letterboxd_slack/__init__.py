import os

import firebase_admin
from firebase_admin import credentials, firestore

from letterboxd_slack import letterboxd, slack

def _get_firestore():
    key_path = os.environ.get("FIREBASE_PRIVATE_KEY_PATH")
    key_blob = os.environ.get("FIREBASE_PRIVATE_KEY_BLOB")
    if not (key_path or key_blob):
        raise ValueError(
            "Need to set `FIREBASE_PRIVATE_KEY_PATH` or `FIREBASE_PRIVATE_KEY_BLOB`"
        )
    creds = credentials.Certificate(key_path or key_blob)
    firebase_admin.initialize_app(creds)
    return firestore.client()

db = _get_firestore()

def main(*args, **kwargs):
    channel_documents = db.collection("channels").get()
    for channel_document in channel_documents:
        channel_name = channel_document.id
        channel_data = channel_document.to_dict().get("users_and_markers", {})

        new_users_and_markers = {}

        for username, review_marker in channel_data.items():
            if review_marker:
                reviews = letterboxd.get_new_reviews_for_user(username, review_marker)
                for review in reviews:
                    slack.notify_review(channel_name, review)

            new_marker = letterboxd.get_most_recent_marker(username)
            new_users_and_markers[username] = new_marker
            new_channel_doc = dict(users_and_markers=new_users_and_markers)

        db.collection("channels").document(channel_name).set(new_channel_doc)
