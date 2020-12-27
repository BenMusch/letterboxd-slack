import json
import os
import time

from google.oauth2 import service_account
from google.cloud import firestore

from letterboxd_slack import letterboxd, slack


def _get_firestore():
    key_path = os.environ.get("FIREBASE_PRIVATE_KEY_PATH")
    key_blob = os.environ.get("FIREBASE_PRIVATE_KEY_BLOB")
    creds = None
    if key_path:
        creds = service_account.Credentials.from_service_account_file(key_path)
    elif key_blob:
        creds = service_account.Credentials.from_service_account_info(json.loads(key_blob))
    else:
        raise ValueError(
            "Need to set `FIREBASE_PRIVATE_KEY_PATH` or `FIREBASE_PRIVATE_KEY_BLOB`"
        )
    return firestore.Client(project=os.environ["FIREBASE_PROJECT_ID"], credentials=creds)

db = _get_firestore()

def main(*args, **kwargs):
    channel_documents = db.collection("channels").get()
    for channel_document in channel_documents:
        channel_name = channel_document.id
        print(channel_name)
        channel_data = channel_document.to_dict().get("users_and_markers", {})
        last_timestamp = channel_document.to_dict().get("last_run_timestamp", 0)

        if int(time.time()) - last_timestamp < 60:
            print("skipping because it's been under 60 seconds since last run")
            continue
        else:
            ts_data = dict(last_run_timestamp=int(time.time()))
            db.collection("channels").document(channel_name).set(ts_data, merge=True)

        new_users_and_markers = {}

        for username, review_marker in channel_data.items():
            if review_marker:
                reviews = letterboxd.get_new_reviews_for_user(username, review_marker)
                for review in reviews:
                    slack.notify_review(channel_name, review)

            new_marker = letterboxd.get_most_recent_marker(username)
            new_users_and_markers[username] = new_marker
            new_channel_doc = dict(users_and_markers=new_users_and_markers)

        db.collection("channels").document(channel_name).set(new_channel_doc, merge=True)
