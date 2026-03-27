from textblob import TextBlob

def analyze_reviews(review_list):
    if not review_list:
        return {
            "positive": 0,
            "negative": 0,
            "summary": "No reviews yet"
        }

    pos = 0
    neg = 0

    for r in review_list:
        text = r.get("review_text", "")
        score = TextBlob(text).sentiment.polarity

        if score >= 0:
            pos += 1
        else:
            neg += 1

    total = pos + neg

    return {
        "positive": round((pos / total) * 100, 2),
        "negative": round((neg / total) * 100, 2),
        "summary": "Mostly Positive Reviews" if pos >= neg else "Mostly Negative Reviews"
    }