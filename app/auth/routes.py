from flask import jsonify, request, current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies, get_jwt_identity
from ..extensions import db, mail
from flask_mail import Message
import datetime
from bson.objectid import ObjectId

bcrypt = Bcrypt()


def init_auth_routes(app):
    @app.route('/register', methods=['POST', 'OPTIONS'])
    def register():
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        user = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        }
        result = db.users.insert_one(user)
        return jsonify({'message': 'User registered successfully', 'user_id': str(result.inserted_id)}), 201

    @app.route('/login', methods=['POST', 'OPTIONS'])
    def login():
        data = request.get_json()
        user = db.users.find_one({'email': data['email']})
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({'message': 'Logged in successfully', 'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401

    @app.route('/user_profile', methods=['GET'])
    @jwt_required()
    def get_user_profile():
        try:
            current_identity = get_jwt_identity()
            user = db.users.find_one({'_id': ObjectId(current_identity)})
            if user:
                return jsonify({
                    'id': str(user.get("_id")),
                    'first_name': str(user.get("first_name")),
                    'last_name': user.get("last_name"),
                    'email': user.get("email"),
                    'created_at': user.get("created_at"),
                }), 200
            else:
                return jsonify({'message': 'User not found'}), 404
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
        
    @app.route('/get_universities', methods=['GET'])
    def get_filtered_universities():
        try:
            query_params = {
                'id': request.args.get('id'),
                'domain': request.args.get('domain'),
                'duration': request.args.get('duration'),
                'university': request.args.get('university'),
                'fees': request.args.get('fees'),
                'cgpa': request.args.get('cgpa'),
                'ielts': request.args.get('ielts'),
                'independent_scholarship': request.args.get('independent_scholarship'),
                'university_scholarship': request.args.get('university_scholarship')
            }
            
            query_params = {k: v for k, v in query_params.items() if v is not None}

            query = {}
            for key, value in query_params.items():
                if value is not None:
                    if key in ['fees', 'cgpa', 'ielts']:
                        query[key] = str(float(value)) if '.' in value else str(int(value))
                    else:
                        query[key] = {'$regex': value, '$options': 'i'}

            universities = list(db.universites.find(query))
            for universite in universities:
                universite['_id'] = str(universite['_id'])

            return jsonify(universities), 200
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    
    @app.route('/get_suggestions', methods=['GET'])
    def get_suggestions():
        universities_domain = [i['domain'] for i in list(db.universites.find())]
        return jsonify(universities_domain), 200
    
    @app.route('/logout', methods=['POST'])
    def logout():
        response = jsonify({'message': 'Logged out successfully'})
        unset_jwt_cookies(response)  # Clear JWT token from client-side
        return response, 200

    @app.route('/forgot-password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        email = data.get('email')

        user = db.users.find_one({'email': email})
        if user:
            # Generate a password reset token
            reset_token = create_access_token(identity=str(
                user['_id']), expires_delta=datetime.timedelta(hours=1))

            # Send an email with the password reset link
            send_reset_email(email, reset_token)

            return jsonify({'message': 'Password reset instructions sent to your email'}), 200
        else:
            return jsonify({'error': 'User with provided email not found'}), 404

    @app.route('/reset-password', methods=['POST'])
    def reset_password():
        data = request.get_json()
        email = data.get('email')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        # Verify if old password matches
        user = db.users.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], old_password):
            # Update user's password
            hashed_password = bcrypt.generate_password_hash(
                new_password).decode('utf-8')
            db.users.update_one({'_id': user['_id']}, {
                                '$set': {'password': hashed_password}})
            return jsonify({'message': 'Password reset successfully'}), 200
        else:
            return jsonify({'error': 'Invalid email or old password'}), 401


def send_reset_email(email, reset_token):
    msg = Message('Password Reset', recipients=[email])
    msg.body = f'Click the following link to reset your password: {current_app.config["RESET_URL"]}/{reset_token}'
    mail.send(msg)
