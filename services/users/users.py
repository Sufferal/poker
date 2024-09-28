from flask import Flask
import os
from datetime import datetime
from db.db_query import *
from db.db_check import *

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

@app.route("/")
def home():
  return "Hello from User Management Microservice!"

@app.route('/status', methods=['GET'])
def status():
  db_status = 'connected' if check_db_connection() else 'disconnected'
  return jsonify({
    'status': 'User service is running',
    'version': '1.0.0',
    'time': datetime.now().isoformat(),
    'database': db_status
  }), 200

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