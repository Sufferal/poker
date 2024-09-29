# 🤩 Online Poker Game
If you like poker, you're going to like poker done through distributed systems.

## 📚 Table of Contents
- [Architecture](./architecture/architecture.md) - this explains the architecture of the project in detail.

## 📦 Prerequisites
- [Docker](https://www.docker.com/)

## 🚀 Getting Started
1. Clone the repository
```bash
git clone https://github.com/Sufferal/poker.git
```
2. Build and run the project in the root directory
```bash
docker compose up --build -d
```
3. Access the endpoints. For more endpoints, check Postman collections.
- **Game Service (Lobby + Game)**
  - Create a lobby - [http://localhost:5111/lobby/create](http://localhost:5111/lobby/create)
    - Request Body
    ```json
    {
      "host_id": 1,
      "max_players": 2,
      "buy_in": 1000
    }
    ```
  - Join a lobby - [http://localhost:5111/lobby/1/join](http://localhost:5111/lobby/1/join)
    - Request Body
    ```json
    {
      "user_id": 2
    }
    ```
  - All Games - [http://localhost:5111/games](http://localhost:5111/games)
  - Game by ID - [http://localhost:5111/games/1](http://localhost:5111/games/1)
  - Deal cards to all players - [http://localhost:5111/games/1/deal-cards](http://localhost:5111/games/1/deal-cards)
  - Determine winner - [http://localhost:5111/games/1/find-winner](http://localhost:5111/games/1/find-winner)
    - Request Body (*this is a general overview of the request body, check the Postman collection for more details*)
    ```json
    {
      "cards": {
        "flop": ["card_1", "card_2", "card_3"],
        "turn": "card_4",
        "river": "card_5",
        "players": [
          {
            "id": 1,
            "cards": ["card_6", "card_7"]
          },
          {
            "id": 2,
            "cards": ["card_8", "card_9"]
          }
        ]
      }
    }
    ```
- **User Service**
  - All Users - [http://localhost:5000/users](http://localhost:5000/users)
  - User by ID - [http://localhost:5000/users/1](http://localhost:5000/users/1)
- **Gateway**
  - All lobbies - [http://localhost:3333/lobby](http://localhost:3333/lobby)
  - Join a lobby - [http://localhost:3333/lobby/1/join](http://localhost:3333/lobby/1/join)
  - Leave a lobby - [http://localhost:3333/lobby/1/leave](http://localhost:3333/lobby/1/leave)
  - Register a user - [http://localhost:3333/users/register](http://localhost:3333/users/register)
    - Request Body
    ```json
    {
      "username": "Michelangelo",
      "password": "David"
    }
    ```
  - Login a user - [http://localhost:3333/users/login](http://localhost:3333/users/login)
    - Request Body
    ```json
    {
      "username": "admin",
      "password": "test"
    }
    ```
- **Cache**
  - Deal cards to all players - [http://localhost:5111/games/1/deal-cards](http://localhost:5111/games/1/deal-cards)
  - If you want to deal new cards, you can ignore the cache by adding the `ignore_cache` query parameter. - [http://localhost:5111/games/1/deal-cards?ignore_cache=true](http://localhost:5111/games/1/deal-cards?ignore_cache=true)
4. If you want to delete all containers, networks, volumes, images, run the following command in the root directory. If you want to remove the volumes as well, add the `--volumes` or `-v` flag.
```bash
docker compose down
```
