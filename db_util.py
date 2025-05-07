from sqlite3 import Cursor, connect
from typing import Tuple

def db_makeTables(db:Cursor) -> None:
    # create chemicals table
    db.execute("""
                create table chemicals (
                    id integer primary key,
                    cas_nr text not null unique,
                    name text not null unique,
                    amount real default 0,
                    unit text not null check (unit in ('g', 'kg', 'mg', 'ml', 'l')),
                    pubchem_cid int unique
                )
               """)

    # create users table
    db.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL UNIQUE,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    hash TEXT NOT NULL UNIQUE
                )
               """)

    # create logs table
    db.execute("""
                CREATE TABLE logs (
                    id INTEGER PRIMARY KEY,
                    chemicals_id TEXT,
                    users_id TEXT,
                    amount INTEGER,
                    unit TEXT CHECK (unit IN ('g', 'kg', 'mg', 'ml', 'l')),
                    change TEXT CHECK (change IN ('add', 'remove')),
                    date NUMERIC CURRENT_DATE,
                    time NUMERIC CURRENT_TIME,
                    FOREIGN KEY(chemicals_id) REFERENCES chemicals(id),
                    FOREIGN KEY(users_id) REFERENCES users(id)
                )
               """)
    return

def db_register_user(db:Cursor, user_name:str, first_name:str, last_name:str, hash:str) -> None:
    db.execute("INSERT INTO users (user_name, first_name, last_name, hash) VALUES (?, ?, ?, ?)", (user_name, first_name, last_name, hash))
    return

def db_get_username(db:Cursor, user_name:str) -> Tuple[str]:
    return db.execute("SELECT user_name FROM users WHERE user_name = ?", [user_name]).fetchone()

def db_get_user_info(db:Cursor, user_name:str) -> Tuple[str, str, str]:
    return db.execute("SELECT first_name, last_name, hash FROM users WHERE user_name = ?", [user_name]).fetchone()

def db_set_hash_for_user(db:Cursor, user_name:str, hash:str) -> None:
    db.execute("UPDATE users SET hash = ? WHERE user_name = ?", [hash, user_name])






