import pandas as pd
import re
import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
# from tensorflow.optimizers import Adam  # Use the updated import

nltk.download('stopwords')
from nltk.corpus import stopwords

# Load Dataset
data = pd.read_csv("./data/nexxt_change_data_for_model_training.csv")

# Data Preprocessing
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r'\n', ' ', text)  # Remove newlines
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.strip()
    return text

data['cleaned_title'] = data['title'].apply(lambda x: clean_text(str(x)))
data['cleaned_description'] = data['description'].apply(lambda x: clean_text(str(x)))
data['cleaned_long_description'] = data['long_description'].apply(lambda x: clean_text(str(x)))
data['combined_text'] = data['cleaned_title'] + ' ' + data['cleaned_description'] + ' ' + data['cleaned_long_description']

data['cleaned_branchen'] = data['branchen'].apply(lambda x: clean_text(str(x)))

# Remove stopwords
stop_words = set(stopwords.words('german'))
data['combined_text'] = data['combined_text'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

# Splitting Data
X = data['combined_text']
y = data['cleaned_branchen']  # Assuming 'branchen' is the target column with categories
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# # Model 1: Logistic Regression
# log_reg = LogisticRegression()
# log_reg.fit(X_train_tfidf, y_train)
# y_pred_log_reg = log_reg.predict(X_test_tfidf)
# print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_log_reg))
# print("Logistic Regression Classification Report:\n", classification_report(y_test, y_pred_log_reg))

# Model 2: Random Forest Classifier
# rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
# rf_clf.fit(X_train_tfidf, y_train)
# y_pred_rf = rf_clf.predict(X_test_tfidf)
# print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))
# print("Random Forest Classification Report:\n", classification_report(y_test, y_pred_rf))

# Model 3: Transformer-based Model (BERT)
# Encode target labels as integers
import pandas as pd

# Get unique labels from the training set
train_labels_set = set(y_train)

# Keep only the test samples that have labels seen in the training set
filtered_test_indices = y_test.isin(train_labels_set)
X_test_filtered = X_test[filtered_test_indices]
y_test_filtered = y_test[filtered_test_indices]

label_encoder = LabelEncoder()

# Encode the filtered labels
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test_filtered)

# Tokenizer and Model Initialization
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-german-cased")
bert_model = TFAutoModelForSequenceClassification.from_pretrained("distilbert-base-german-cased", num_labels=len(label_encoder.classes_))


# Tokenizing Data (filtered X_test)
train_encodings = tokenizer(list(X_train), truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(list(X_test_filtered), truncation=True, padding=True, max_length=128)


# Creating TensorFlow Datasets
def create_tf_dataset(encodings, labels):
    return tf.data.Dataset.from_tensor_slices((dict(encodings), labels)).shuffle(1000).batch(16)

# Creating TensorFlow Datasets
train_dataset = create_tf_dataset(train_encodings, y_train_encoded)
test_dataset = create_tf_dataset(test_encodings, y_test_encoded)

# Compiling and Training BERT Model
bert_model.compile(optimizer='adam',
                   loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                   metrics=['accuracy'])



bert_model.fit(train_dataset, epochs=3, validation_data=test_dataset)

# # Evaluation
test_loss, test_acc = bert_model.evaluate(test_dataset)
print("BERT Test Accuracy:", test_acc)

# Summary
# print("\nSummary of Model Performances:")
# print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_log_reg))
# print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))
# print("BERT Test Accuracy:", test_acc)
