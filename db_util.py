from sqlite3 import Cursor, OperationalError, IntegrityError
from typing import Tuple, List, Dict

def db_makeTables(db:Cursor) -> None:
    # create chemicals table
    db.execute("""
                create table chemicals (
                    cas_nr TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    amount REAL DEFAULT 0,
                    unit TEXT NOT NULL CHECK (unit in ('g', 'kg', 'mg', 'ml', 'l')),
                    pubchem_cid INT UNIQUE
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
                    chemicals_cas_nr TEXT,
                    users_id TEXT,
                    action TEXT CHECK (action IN ('add', 'remove', 'use', 'restock')),
                    amount REAL DEFAULT 0,
                    date NUMERIC DEFAULT CURRENT_DATE,
                    time NUMERIC DEFAULT CURRENT_TIME,
                    FOREIGN KEY(chemicals_cas_nr) REFERENCES chemicals(cas_nr),
                    FOREIGN KEY(users_id) REFERENCES users(id)
                )
               """)
    return

def db_register_user(db:Cursor, user_name:str, first_name:str, last_name:str, hash:str) -> None:
    db.execute("INSERT INTO users (user_name, first_name, last_name, hash) VALUES (?, ?, ?, ?)", (user_name, first_name, last_name, hash))
    return

def db_get_user_info(db:Cursor, user_name:str) -> Tuple[int, str, str, str]:
    return db.execute("SELECT id, first_name, last_name, hash FROM users WHERE user_name = ?", [user_name]).fetchone()

def db_set_hash_for_user(db:Cursor, user_name:str, hash:str) -> None:
    db.execute("UPDATE users SET hash = ? WHERE user_name = ?", [hash, user_name])

def db_get_stock(db:Cursor):
    result = db.execute("SELECT cas_nr, name, amount, unit FROM chemicals")
    names = [description[0] for description in result.description]
    return names, result.fetchall()

def db_add_logs(db:Cursor, data:Tuple[str, int, str, float]) -> None:
    db.execute("INSERT INTO logs (chemicals_cas_nr, users_id, action, amount) VALUES (?, ?, ?, ?)", data)
    return

def db_add_chemicals(db:Cursor, data:List[Tuple[str, str, float, str]], user_id:int) -> List[Tuple[str, str, float, str]]:
    wrong_data = []
    for value in data:
        try:
            db.execute("INSERT INTO chemicals (cas_nr, name, amount, unit) VALUES (?, ?, ?, ?)", value)
            db_add_logs(db, (value[0], user_id, "add", value[2]))
        except IntegrityError:
            value = list(value)
            value[0] = f"!{value[0]}" 
            wrong_data.append(tuple(value))
    return wrong_data

