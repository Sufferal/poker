from flask import Flask
import os
from db.db_query import *
from db.db_check import *
from datetime import datetime
from utils.poker import deal_cards_all, determine_winner

app = Flask(__name__)
port = int(os.environ.get('PORT', 5111))

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
  return deal_cards(id, deal_cards_all)

@app.route("/games/<int:id>/find-winner", methods=["POST"])
def find_winner_route(id):
  return find_winner(id, determine_winner)

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=port)