import os
import re
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# 🧹 Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# 📂 LOAD IMDB DATASET
def load_imdb_data(data_dir):
    texts = []
    labels = []

    for label_type in ["pos", "neg"]:
        dir_name = os.path.join(data_dir, label_type)

        for file in os.listdir(dir_name):
            with open(os.path.join(dir_name, file), encoding="utf-8") as f:
                texts.append(clean_text(f.read()))
                labels.append(1 if label_type == "pos" else 0)

    return pd.DataFrame({"text": texts, "label": labels})


# 🔥 CHANGE THIS PATH
TRAIN_DIR = "aclImdb/train"
TEST_DIR = "aclImdb/test"

print("📥 Loading dataset...")

train_df = load_imdb_data(TRAIN_DIR)
test_df = load_imdb_data(TEST_DIR)

print("✅ Dataset loaded!")
print("Train size:", len(train_df))
print("Test size:", len(test_df))


# 🔹 TF-IDF Vectorizer
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train = vectorizer.fit_transform(train_df["text"])
X_test = vectorizer.transform(test_df["text"])

y_train = train_df["label"]
y_test = test_df["label"]


# 🔹 Model
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

print("🚀 Training model...")
model.fit(X_train, y_train)


# 📊 Evaluation
print("\n📊 Evaluating model...")
y_pred = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
print("\nClassification Report:\n", classification_report(y_test, y_pred))


# 💾 Save model
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\n✅ Model trained and saved successfully!")