from sqlite3 import Cursor

def makeTables(db:"Cursor") -> None:
    # create chemicals table
    db.execute("""
                CREATE TABLE chemicals (
                    cas_nr TEXT,
                    name TEXT,
                    amount REAL,
                    unit TEXT,
                    pubchem_cid INT,
                    PRIMARY KEY(cas_nr)
                )
               """)

    # create persons table
    db.execute("""
                CREATE TABLE persons (
                    user_name TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    PRIMARY KEY(user_name)
                )
               """)

    # create logs table
    db.execute("""
                CREATE TABLE logs (
                    id INTEGER,
                    chemicals_cas_nr TEXT,
                    persons_user_name TEXT,
                    amount INTEGER,
                    unite TEXT,
                    change TEXT,
                    date NUMERIC,
                    time NUMERIC,
                    PRIMARY KEY(id),
                    FOREIGN KEY(chemicals_cas_nr) REFERENCES chemicals(cas_nr),
                    FOREIGN KEY(persons_user_name) REFERENCES persons(id)
                )
               """)
    return
