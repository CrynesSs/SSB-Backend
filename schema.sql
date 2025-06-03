DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS room_members;
DROP TABLE IF EXISTS user_data;
DROP TABLE IF EXISTS cookies;



CREATE TABLE IF NOT EXISTS users
(
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    vanity_name           TEXT UNIQUE NOT NULL ,
    username_hash         TEXT UNIQUE NOT NULL,
    password_hash         TEXT        NOT NULL,
    passphrase_hash       TEXT        NOT NULL,
    username_salt         TEXT        NOT NULL,
    password_salt         TEXT        NOT NULL,
    passphrase_salt       TEXT        NOT NULL,
    pubkey                BLOB        NOT NULL, -- used to encrypt data
    max_storage_bytes     INTEGER DEFAULT 52428800,
    current_storage_bytes INTEGER DEFAULT 0,
    retention_seconds     INTEGER DEFAULT 7200
);

CREATE TABLE IF NOT EXISTS rooms
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_token TEXT UNIQUE NOT NULL, -- 32-byte hex or base64
    join_limit INTEGER   DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creator    TEXT        NOT NULL,
    FOREIGN KEY (creator) REFERENCES users (username_hash) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS room_members
(
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS data_packet
(
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_user_id INTEGER NOT NULL,
    sender_user_id    INTEGER,
    data              BLOB    NOT NULL,
    uploaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (sender_user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS cookies
(
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cookie  BLOB    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)

