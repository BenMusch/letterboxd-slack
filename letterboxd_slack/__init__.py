from letterboxd_slack import letterboxd, slack

def main(*args, **kwargs):
    reviews = letterboxd.get_new_reviews()
    for review in reviews:
        slack.notify_review("#ben-test", review)
