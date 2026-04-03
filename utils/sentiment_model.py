import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 🔹 Sample dataset (replace with real dataset later)
data = {
    "text": [
        "Amazing movie", "Loved it", "Best film ever",
        "Worst movie", "Not good", "Waste of time"
    ],
    "label": [1, 1, 1, 0, 0, 0]
}

df = pd.DataFrame(data)

# 🔹 Vectorization
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["text"])

# 🔹 Model
model = LogisticRegression()
model.fit(X, df["label"])

# 💾 Save model
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")