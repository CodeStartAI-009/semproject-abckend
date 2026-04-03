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
    text = re.sub(r"http\S+", "", text)  # remove links
    text = re.sub(r"full review:.*", "", text)  # remove full review section
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # remove special chars
    text = re.sub(r"\s+", " ", text).strip()
    return text


# 🔥 Sentiment Prediction (FINAL FIXED)
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
            "solid", "competent", "enjoyable", "nice",
            "outstanding", "brilliant", "incredible", "masterpiece",
            "superb", "impressive", "engaging", "fun", "entertaining",
            "well done", "well made", "beautiful", "stunning",
            "emotional", "heartwarming", "touching", "memorable",
            "captivating", "charming", "spectacular", "epic",
            "strong performance", "great acting", "great story",
            "great visuals", "amazing soundtrack", "worth watching"
        ]

        # ❌ NEGATIVE WORDS
        negative_words = [
            "bad", "worst", "boring", "terrible", "waste", "awful",
            "disappointing", "poor", "mediocre",
            "predictable", "cliche", "unoriginal", "generic",
            "slow", "dull", "confusing", "messy", "weak",
            "bad acting", "poor acting", "bad script", "weak story",
            "poor direction", "bad direction",
            "overrated", "underwhelming", "forgettable",
            "annoying", "cringe", "forced", "dragging",
            "not worth it", "waste of time", "disappointing experience"
        ]

        # 🔥 KEYWORD CHECK FIRST (IMPORTANT)
        if any(word in cleaned for word in positive_words):
            return "positive"

        if any(word in cleaned for word in negative_words):
            return "negative"

        # 🔥 LONG TEXT → neutral (only if no strong keywords)
        if len(words) > 40:
            return "neutral"

        # 🤖 ML fallback
        X = vectorizer.transform([cleaned])
        prediction = model.predict(X)[0]

        # 🔥 Confidence handling
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

    # 🚫 Repetitive text
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