from utils.ml_sentiment import predict_sentiment, predict_fake_review


def analyze_reviews(review_list):
    # 🚫 No reviews case
    if not review_list:
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "fake_percentage": 0,
            "overall_rating": 0,
            "total_reviews": 0,
            "summary": "No reviews yet"
        }

    pos = 0
    neg = 0
    neutral = 0
    fake = 0

    total_rating = 0
    rating_count = 0

    for r in review_list:
        text = r.get("review_text", "")
        rating = r.get("rating")

        # 🔥 Sentiment Prediction
        sentiment = predict_sentiment(text)

        if sentiment == "positive":
            pos += 1
        elif sentiment == "negative":
            neg += 1
        else:
            neutral += 1

        # 🔥 Fake Detection
        if predict_fake_review(text):
            fake += 1

        # 🔥 Rating calculation
        if rating is not None:
            try:
                total_rating += float(rating)
                rating_count += 1
            except:
                pass

    total = pos + neg + neutral

    # 🚫 Avoid division by zero
    if total == 0:
        total = 1

    # 📊 Percentages
    positive_pct = round((pos / total) * 100, 2)
    negative_pct = round((neg / total) * 100, 2)
    neutral_pct = round((neutral / total) * 100, 2)
    fake_pct = round((fake / total) * 100, 2)

    # ⭐ Overall Rating
    overall_rating = round(total_rating / rating_count, 2) if rating_count else 0

    # 🧠 FINAL SMART SUMMARY LOGIC (FIXED)
    if positive_pct >= 75:
        summary = "🔥 Highly Recommended"

    elif positive_pct >= 60:
        summary = "👍 Very Good Movie"

    elif positive_pct >= 50:
        summary = "🙂 Good Movie"

    elif positive_pct >= 30:
        summary = "⚠️ Mixed Reviews"

    # 🔥 IMPORTANT FIX (neutral-heavy case)
    elif neutral_pct >= 50:
        summary = "😐 Mostly Neutral Reviews"

    else:
        summary = "❌ Not Recommended"

    return {
        "positive": positive_pct,
        "negative": negative_pct,
        "neutral": neutral_pct,
        "fake_percentage": fake_pct,
        "overall_rating": overall_rating,
        "total_reviews": total,
        "summary": summary
    }