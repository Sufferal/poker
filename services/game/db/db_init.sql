CREATE TABLE IF NOT EXISTS lobbies (
    lobby_id SERIAL PRIMARY KEY,
    host_id INTEGER NOT NULL,
    max_players INTEGER NOT NULL,
    buy_in NUMERIC(10, 2) NOT NULL,
    players JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting'
);

CREATE TABLE IF NOT EXISTS games (
    game_id SERIAL PRIMARY KEY,
    lobby_id INTEGER NOT NULL,
    winner_id INTEGER,
    FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id)
);