import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify, request

def get_db_connection():
  return psycopg2.connect(
    dbname="db-users",
    user="admin",
    password="qwerty",
    host="users-db"
  )

def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users;')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

def get_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

def register_user():
    username = request.json.get('username')
    password = request.json.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s;', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    cursor.execute(
        'INSERT INTO users (username, password, balance) VALUES (%s, %s, %s) RETURNING id;',
        (username, password, 0)
    )
    user_id = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully', 'id': user_id}), 201

def authenticate_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Please provide both username and password'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s;', (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({'message': 'Authentication successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

def update_balance(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    balance = request.json.get('balance')
    if not balance:
        return jsonify({'error': 'Please provide an amount'}), 400

    # Check if balance is a valid number
    try:
        balance = float(balance)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

    cursor.execute('UPDATE users SET balance = %s WHERE id = %s;', (balance, id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Balance updated successfully'}), 200

def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    cursor.execute('DELETE FROM users WHERE id = %s;', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User deleted successfully'}), 200