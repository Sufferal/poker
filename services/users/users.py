from flask import Flask
import os
from db.db_query import get_users, get_user, register_user, authenticate_user, update_balance, delete_user

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

@app.route("/")
def home():
    return "Hello from User Management Microservice!"

@app.route('/users', methods=['GET'])
def get_users_route():
    return get_users()

@app.route('/users/<int:id>', methods=['GET'])
def get_user_route(id):
    return get_user(id)

@app.route('/users/register', methods=['POST'])
def register_user_route():
    return register_user()

@app.route('/users/login', methods=['POST'])
def authenticate_user_route():
    return authenticate_user()

@app.route('/users/<int:id>/balance', methods=['PATCH'])
def update_balance_route(id):
    return update_balance(id)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user_route(id):
    return delete_user(id)

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=port)