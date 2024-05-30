import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Custom preprocessor to handle documents with only stop words
def custom_preprocessor(doc):
    if all(word.lower() in ENGLISH_STOP_WORDS for word in doc.split()):
        return 'emptydocument'
    return doc

# Load the dataset
with open('reviews.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Preprocess the data
reviews = []
sentiments = []
for item in data['all']:
    review = item.get('review', '')  # Use empty string as default value if 'review' key is missing
    rating = item.get('rating', 0)  # Use 0 as default value if 'rating' key is missing
    reviews.append(review)
    sentiments.append(rating > 5)   # Assume ratings > 5 are positive

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(reviews, sentiments, test_size=0.2, random_state=42)

# Train the sentiment analysis model
# Train the sentiment analysis model with n-grams
model = make_pipeline(CountVectorizer(preprocessor=custom_preprocessor, ngram_range=(1, 2)), MultinomialNB())
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
print(classification_report(y_test, y_pred))

# Create a sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to check if reviews are available for a specific university
def reviews_available(university_name):
    for item in data['all']:
        if item['university'] == university_name:
            return True
    return False

def get_reviews(university_name):
    reviews = []
    for item in data['all']:
        if 'university' in item and 'reviews' in item and item['university'].strip().lower() == university_name.strip().lower():
            reviews.extend([review_item['review'] for review_item in item['reviews']])
    return reviews

def generate_recommendation(university_name):
    if not reviews_available(university_name):
        return "No reviews found for this university."

    reviews = get_reviews(university_name)
    if not reviews:
        return "No reviews found for this university."

    # Analyze sentiment for each review
    sentiments = [analyzer.polarity_scores(review)['compound'] for review in reviews]
    positive_reviews = sum(1 for sentiment in sentiments if sentiment > 0.05)
    negative_reviews = sum(1 for sentiment in sentiments if sentiment < -0.05)
    neutral_reviews = len(sentiments) - positive_reviews - negative_reviews

    total_reviews = len(reviews)

    if positive_reviews > negative_reviews and positive_reviews > neutral_reviews:
        return f"Based on {total_reviews} reviews, {university_name} is highly recommended for admission. There are {positive_reviews} positive reviews, {negative_reviews} negative reviews, and {neutral_reviews} neutral reviews."
    elif negative_reviews > positive_reviews and negative_reviews > neutral_reviews:
        return f"Based on {total_reviews} reviews, {university_name} is not recommended for admission. There are {positive_reviews} positive reviews, {negative_reviews} negative reviews, and {neutral_reviews} neutral reviews."
    else:
        return f"Based on {total_reviews} reviews, {university_name} is neutral for admission. There are {positive_reviews} positive reviews, {negative_reviews} negative reviews, and {neutral_reviews} neutral reviews."

# Example usage
university_name = "University of Hull"
print(generate_recommendation(university_name))
