import os
import joblib
import re

# 📁 Get backend root path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

# 🔒 Safe loading
try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✅ ML model loaded successfully")
except Exception as e:
    print("❌ ERROR loading model:", e)
    model = None
    vectorizer = None


# 🧹 Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"full review:.*", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# 🔥 Sentiment Prediction (WITH NEUTRAL SUPPORT)
def predict_sentiment(text):
    if not text:
        return "neutral"

    if model is None or vectorizer is None:
        return "neutral"

    try:
        cleaned = clean_text(text)
        words = cleaned.split()

        # ✅ POSITIVE WORDS
        positive_words = [
            "good", "great", "amazing", "excellent", "love", "fantastic",
            "outstanding", "brilliant", "incredible", "masterpiece",
            "superb", "impressive", "engaging", "fun", "entertaining",
            "well done", "beautiful", "stunning", "worth watching"
        ]

        # ❌ NEGATIVE WORDS
        negative_words = [
            "bad", "worst", "boring", "terrible", "waste", "awful",
            "disappointing", "poor", "mediocre",
            "predictable", "slow", "dull", "overrated",
            "not worth it", "waste of time"
        ]

        # 😐 NEUTRAL WORDS
        neutral_words = [
            "average", "okay", "fine", "decent",
            "not bad", "not great", "mediocre",
            "so so", "nothing special", "ordinary",
            "mixed", "balanced", "fair", "acceptable",
            "passable", "just okay", "alright"
        ]

        # 🔥 SCORE-BASED APPROACH (BETTER)
        pos_score = sum(1 for word in positive_words if word in cleaned)
        neg_score = sum(1 for word in negative_words if word in cleaned)
        neu_score = sum(1 for word in neutral_words if word in cleaned)

        # 🔥 DECISION LOGIC
        if pos_score > neg_score and pos_score > neu_score:
            return "positive"

        if neg_score > pos_score and neg_score > neu_score:
            return "negative"

        if neu_score > 0:
            return "neutral"

        # 🔥 LONG TEXT fallback
        if len(words) > 40:
            return "neutral"

        # 🤖 ML fallback
        X = vectorizer.transform([cleaned])
        prediction = model.predict(X)[0]

        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(X)[0]
            if max(prob) < 0.55:
                return "neutral"

        return "positive" if prediction == 1 else "negative"

    except Exception as e:
        print("❌ Prediction error:", e)
        return "neutral"


# 🔥 Fake Review Detection
def predict_fake_review(text):
    if not text:
        return True

    text = text.lower()
    words = text.split()

    # 🚫 Too short → fake
    if len(words) < 3:
        return True

    # ✅ Long reviews → NOT fake
    if len(words) > 30:
        return False

    # 🚫 Repetitive
    if len(set(words)) / len(words) < 0.3:
        return True

    # 🚫 Spam keywords
    suspicious_keywords = [
        "buy now", "free", "click",
        "offer", "limited deal", "visit link"
    ]

    for word in suspicious_keywords:
        if word in text:
            return True

    return False