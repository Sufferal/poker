import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify, request
import json
import requests

def get_db_connection():
  return psycopg2.connect(
    dbname="db-games",
    user="admin",
    password="qwerty",
    host="game-db"
  )

# Lobbies
def get_lobbies():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM lobbies;')
    lobbies = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(lobbies)

def create_lobby():
  host_id = request.json.get('host_id')
  max_players = request.json.get('max_players')
  buy_in = request.json.get('buy_in')

  if not isinstance(host_id, int):
      return jsonify({'error': 'host_id must be an integer'}), 400

  if not isinstance(max_players, int):
      return jsonify({'error': 'max_players must be an integer'}), 400

  if not isinstance(buy_in, (int, float)):
      return jsonify({'error': 'buy_in must be a number'}), 400

  # Verify user_id with the users service
  USER_SERVICE_URL = f'http://users:5000/users/{host_id}'
  response = requests.get(USER_SERVICE_URL)

  if response.status_code != 200:
      return jsonify({'error': 'User not found with such id'}), 404

  conn = get_db_connection()
  cursor = conn.cursor(cursor_factory=RealDictCursor)

  # Check if the host already has an existing lobby
  cursor.execute('SELECT * FROM lobbies WHERE host_id = %s AND status = %s;', (host_id, 'waiting'))
  existing_lobby = cursor.fetchone()

  if existing_lobby:
      cursor.close()
      conn.close()
      return jsonify({'error': 'Host already has an existing lobby'}), 400

  players = [{'user_id': host_id}]

  cursor.execute(
      'INSERT INTO lobbies (host_id, max_players, buy_in, players, status) VALUES (%s, %s, %s, %s, %s) RETURNING lobby_id;',
      (host_id, max_players, buy_in, json.dumps(players), 'waiting')
  )
  lobby_id = cursor.fetchone()['lobby_id']
  conn.commit()
  cursor.close()
  conn.close()

  return jsonify({'message': 'Lobby created successfully', 'lobby_id': lobby_id}), 201

def join_lobby(lobby_id):
    user_id = request.json.get('user_id')

    if not isinstance(user_id, int):
        return jsonify({'error': 'user_id must be an integer'}), 400
    
    # Verify user_id with the users service
    user_service_url = f'http://users:5000/users/{user_id}'
    response = requests.get(user_service_url)
    
    if response.status_code != 200:
      return jsonify({'error': 'User not found with such id'}), 404

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (lobby_id,))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    if lobby['status'] != 'waiting':
        cursor.close()
        conn.close()
        return jsonify({'error': 'Cannot join a lobby that has already started'}), 400

    players = lobby['players']
    max_players = lobby['max_players']

    # Lobby is full
    if len(players) >= max_players:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby is full'}), 400
    
    # Check if user is already in the lobby
    for player in players:
        if player['user_id'] == user_id:
          cursor.close()
          conn.close()
          return jsonify({'error': 'User is already in the lobby'}), 400

    players.append({'user_id': user_id})
    # Serialize the players list to a JSON string
    players_json = json.dumps(players)

    cursor.execute('UPDATE lobbies SET players = %s WHERE lobby_id = %s;', (players_json, lobby_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User joined lobby successfully'}), 200

def leave_lobby(lobby_id):
    user_id = request.json.get('user_id')

    if not isinstance(user_id, int):
        return jsonify({'error': 'user_id must be an integer'}), 400

    # Verify user_id with the users service
    user_service_url = f'http://users:5000/users/{user_id}'
    response = requests.get(user_service_url)
    
    if response.status_code != 200:
      return jsonify({'error': 'User not found with such id'}), 404

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (lobby_id,))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    players = lobby['players']

    # Check if user is in the lobby
    user_in_lobby = False
    for player in players:
        if player['user_id'] == user_id:
            user_in_lobby = True
            players.remove(player)
            break

    if not user_in_lobby:
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not in the lobby'}), 400

    # Serialize the players list to a JSON string
    players_json = json.dumps(players)

    cursor.execute('UPDATE lobbies SET players = %s WHERE lobby_id = %s;', (players_json, lobby_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User left lobby successfully'}), 200

def start_lobby(lobby_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (lobby_id,))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    if lobby['status'] == 'started':
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby has already started'}), 400

    players = lobby['players']
    max_players = lobby['max_players']

    # Check if the lobby has enough players to start the game
    if len(players) < 2:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Not enough players to start the game'}), 400

    # Update the lobby status to 'started'
    cursor.execute('UPDATE lobbies SET status = %s WHERE lobby_id = %s;', ('started', lobby_id))

    # Create a new game entry in the games table
    cursor.execute(
        'INSERT INTO games (lobby_id) VALUES (%s) RETURNING game_id;',
        (lobby_id,)
    )
    game_id = cursor.fetchone()['game_id']
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Game started successfully', 'game_id': game_id}), 200

def delete_lobby(lobby_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (lobby_id,))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    # Delete the game associated with the lobby
    cursor.execute('DELETE FROM games WHERE lobby_id = %s;', (lobby_id,))

    # Delete the lobby
    cursor.execute('DELETE FROM lobbies WHERE lobby_id = %s;', (lobby_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Lobby deleted successfully'}), 200

# Games
def get_games():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM games;')
    games = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(games)

def get_game(game_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM games WHERE game_id = %s;', (game_id,))
    game = cursor.fetchone()
    cursor.close()
    conn.close()

    if game is None:
        return jsonify({'error': 'Game not found'}), 404

    return jsonify(game)

def deal_cards(game_id, deal_cards_all):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM games WHERE game_id = %s;', (game_id,))
    game = cursor.fetchone()

    if game is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Game not found'}), 404

    # Get the lobby associated with the game
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (game['lobby_id'],))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    players = lobby['players']
    num_players = len(players)

    if num_players < 2:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Not enough players to deal cards'}), 400

    # Deal cards
    result = deal_cards_all(num_players) 

    # Store the dealt cards in the games table
    cursor.execute('UPDATE games SET dealt_cards = %s WHERE game_id = %s;', (json.dumps(result), game_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Cards dealt successfully', 
        'cards': result
    }), 200

def find_winner(game_id, determine_winner):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM games WHERE game_id = %s;', (game_id,))
    game = cursor.fetchone()

    if game is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Game not found'}), 404

    # Get the lobby associated with the game
    cursor.execute('SELECT * FROM lobbies WHERE lobby_id = %s;', (game['lobby_id'],))
    lobby = cursor.fetchone()

    if lobby is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Lobby not found'}), 404

    players = lobby['players']
    num_players = len(players)

    if num_players < 2:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Not enough players to determine winner'}), 400

    # Determine the winner
    cards = request.json.get('cards')
    result = determine_winner(cards)

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'winner': result['winner'],
        'hands': result['hands']
    }), 200 