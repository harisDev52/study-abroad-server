import csv
import json
from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Custom preprocessor to handle documents with only stop words
def custom_preprocessor(doc):
    if all(word.lower() in ENGLISH_STOP_WORDS for word in doc.split()):
        return 'emptydocument'
    return doc

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

def reviews_available(university_name):
    for item in data['all']:
        if 'university' in item and item['university'] == university_name:
            return True
    return False

def get_reviews(university_name):
    reviews = []
    for item in data['all']:
        if 'university' in item and 'reviews' in item and item['university'].strip().lower() == university_name.strip().lower():
            reviews.extend([review_item['review'] for review_item in item['reviews']])
    return reviews

def read_program_data_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            return list(csv_reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"Error reading CSV file '{file_path}': {e}")

def read_description_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            return list(csv_reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"Error reading CSV file '{file_path}': {e}")

def group_programs_by_domain(programs):
    domain_programs = {}
    for program in programs:
        domain = program['domain']
        domain_programs.setdefault(domain, []).append(program)
    return domain_programs

def get_description_by_domain(descriptions, domain):
    for desc in descriptions:
        if desc.get('Domain') == domain:
            return desc.get('Description')
    return 'Description not available'

def read_reviews_from_json(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as json_file:
            reviews_data = json.load(json_file)
            return reviews_data
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"Error reading JSON file '{file_path}': {e}")

def get_reviews_by_university(reviews, university):
    all_reviews = reviews.get('all', [])
    for item in all_reviews:
        if item.get('university') == university:
            return item.get('reviews', [])
    return []

def init_profile_routes(app):
    programs = read_program_data_from_csv('programs.csv')
    domain_programs = group_programs_by_domain(programs)
    descriptions = read_description_from_csv('data2.csv')
    reviews = read_reviews_from_json('reviews.json')

    @app.route('/programs', methods=['GET'])
    def get_all_programs():
        if programs:
            return jsonify({'universities': programs}), 200
        else:
            return jsonify({'message': 'No programs found'}), 404

    @app.route('/universities/<domain>', methods=['GET'])
    def get_universities_by_domain(domain):
        universities = domain_programs.get(domain, [])
        if universities:
            return jsonify({'universities': universities}), 200
        else:
            return jsonify({'message': 'No universities found for the given domain'}), 404

    @app.route('/description/<domain>', methods=['GET'])
    def get_university_description(domain):
        description = get_description_by_domain(descriptions, domain)
        return jsonify({'description': description}), 200

    @app.route('/reviews/<university>', methods=['GET'])
    def get_reviews_by_university_api(university):
        uni_reviews = get_reviews_by_university(reviews, university)
        return jsonify({'reviews': uni_reviews}), 200
    @app.route('/recommendations', methods=['POST'])
    def get_recommendation():
        data = request.get_json()
        university_name = data.get('university', '')

        if not university_name:
            return jsonify({'error': 'University name not provided'}), 400

        recommendation = generate_recommendation(university_name)
        return jsonify({'recommendation': recommendation}), 200

