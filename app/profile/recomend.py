from flask import jsonify, request
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json


# Load the sentiment analysis model
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

# Train the sentiment analysis model with n-grams
model = make_pipeline(CountVectorizer(preprocessor=custom_preprocessor, ngram_range=(1, 2)), MultinomialNB())
model.fit(reviews, sentiments)

# Create a sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Custom preprocessor to handle documents with only stop words
def custom_preprocessor(doc):
    if all(word.lower() in ENGLISH_STOP_WORDS for word in doc.split()):
        return 'emptydocument'
    return doc

@app.route('/recommendations', methods=['POST'])
def get_recommendation():
    data = request.get_json()
    university_name = data.get('university', '')

    if not university_name:
        return jsonify({'error': 'University name not provided'}), 400

    recommendation = generate_recommendation(university_name)
    return jsonify({'recommendation': recommendation}), 200

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

