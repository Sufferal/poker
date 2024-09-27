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
- User Service
  - (All Users) - [http://localhost:5000/users](http://localhost:5000/users)
  - (User by ID) - [http://localhost:5000/users/1](http://localhost:5000/users/1)
4. If you want to delete all containers, networks, volumes, images, run the following command in the root directory. If you want to remove the volumes as well, add the `--volumes` or `-v` flag.
```bash
docker compose down
```
