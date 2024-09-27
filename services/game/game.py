from flask import Flask
import os
from db.db_query import *

app = Flask(__name__)
port = int(os.environ.get('PORT', 5111))

@app.route("/", methods=["GET"])
def home():
  return "Hello from Game Management Microservice!"

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

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=port)