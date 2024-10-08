from flask import Flask, jsonify
from flask_socketio import SocketIO, send, emit
import os
import redis
from db.db_query import *
from db.db_check import *
from datetime import datetime
from utils.poker import deal_cards_all, determine_winner

app = Flask(__name__)
socketio = SocketIO(app)
port = int(os.environ.get('PORT', 5111))

# Redis
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.StrictRedis.from_url(redis_url)

@app.route("/", methods=["GET"])
def home():
  return "Hello from Game Management Microservice!"

@app.route('/status', methods=['GET'])
def status():
  db_status = 'connected' if check_db_connection() else 'disconnected'
  return jsonify({
    'status': 'Game service is running',
    'version': '1.0.0',
    'time': datetime.now().isoformat(),
    'database': db_status
  }), 200

# Lobbies
@app.route("/lobby", methods=["GET"])
def get_lobbies_route():
  return get_lobbies()

@app.route("/lobby/create", methods=["POST"])
def create_lobby_route():
  return create_lobby()

@app.route("/lobby/<int:id>/join", methods=["POST"])
def join_lobby_route(id):
  return join_lobby(id)

@app.route("/lobby/<int:id>/leave", methods=["POST"])
def leave_lobby_route(id):
  return leave_lobby(id)

@app.route("/lobby/<int:id>/start", methods=["GET"])
def start_lobby_route(id):
  return start_lobby(id)

@app.route("/lobby/<int:id>", methods=["DELETE"])
def delete_lobby_route(id):
  return delete_lobby(id)

# Games
@app.route("/games", methods=["GET"])
def get_games_route():
  return get_games() 

@app.route("/games/<int:id>", methods=["GET"])
def get_game_route(id):
  return get_game(id)

@app.route("/games/<int:id>/deal-cards", methods=["GET"])
def deal_cards_route(id):
  ignore_cache = request.args.get('ignore_cache', 'false').lower() == 'true'
  cache_key = f"game:{id}:dealt_cards"

  if not ignore_cache:
    cached_dealt_cards = redis_client.get(cache_key)
    if cached_dealt_cards:
      return jsonify({
        'message': 'Cards dealt successfully (from cache)', 
        'cards': json.loads(cached_dealt_cards)
      }), 200

  response, status_code = deal_cards(id, deal_cards_all)
  if status_code == 200:
    result_data = response.get_json()
    redis_client.set(cache_key, json.dumps(result_data['cards']))

  return response, status_code

@app.route("/games/<int:id>/find-winner", methods=["POST"])
def find_winner_route(id):
  return find_winner(id, determine_winner)

@socketio.on('connect')
def handle_connect():
  send("Connected to the websocket server")

@socketio.on('bet')
def handle_bet(data):
  emit('bet', f"Player with id {data['id']} did a bet of {data['amount']}", broadcast=True)

@socketio.on('fold')
def handle_fold(data):
  emit('fold', f"Player with id {data['id']} folded", broadcast=True)

@socketio.on('message')
def handle_message(message):
  send(f"Message: {message}")

if __name__ == "__main__":
  socketio.run(app, debug=True, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)