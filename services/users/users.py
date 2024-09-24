import requests 
from flask import Flask, jsonify, request, make_response
import jwt
from functools import wraps
import json
import os
import random 
from jwt.exceptions import DecodeError

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

# Users data (temporary)
with open('./data/users.json', 'r') as f:
  USERS = json.load(f)

@app.route("/")
def home():
  return "Hello from User Management Microservice!"

@app.route('/users')
def get_users():
  return jsonify(USERS)

@app.route('/users/<int:id>')
def get_user(id):
  user = next((user for user in USERS if user['id'] == id), None)
  if user:
    return jsonify(user)
  return jsonify({'error': 'User not found'}), 404

@app.route('/register', methods=['POST'])
def register_user():
  username = request.json.get('username')
  password = request.json.get('password')

  for user in USERS:
    if user['username'] == username:
      return jsonify({'error': 'Username already exists'}), 400
    
  with open('./data/users.json', 'w') as f:
    USERS.append({
      'id': random.randint(1, 1000000), 
      'username': username,
      'password': password,
      'balance': 0
    })
    json.dump(USERS, f, indent=2)

  return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def authenticate_user():
  username = request.json.get('username')
  password = request.json.get('password')
  
  if not username or not password:
      return jsonify({'error': 'Please provide both username and password'}), 400
  
  for user in USERS:
    if user['username'] == username and user['password'] == password:
      return jsonify({'message': 'Authentication successful'}), 200  
  
  return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users/<int:id>/balance', methods=['PATCH'])
def update_balance(id):
  user = next((user for user in USERS if user['id'] == id), None)
  if not user:
    return jsonify({'error': 'User not found'}), 404

  balance = request.json.get('balance')
  if not balance:
    return jsonify({'error': 'Please provide an amount'}), 400

  user['balance'] = balance
  with open('./data/users.json', 'w') as f:
    json.dump(USERS, f, indent=2)

  return jsonify({'message': 'Balance updated successfully'}), 200

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=port)