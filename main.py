import sqlite3
from util import makeTables

def main():
    # connect to database
    db = sqlite3.connect("chemicals.db").cursor()

    # initialize the db if ther is no data
    if not db.execute("SELECT * FROM sqlite_master").fetchall():
        makeTables(db)

 
    return 0



if __name__ == "__main__":
    main()
