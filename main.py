import sqlite3
from argon2 import PasswordHasher
from getpass import getpass
from util import *
from typing import List, Dict

def main() -> int:
    # connect to database
    con = sqlite3.connect("lims.db")

    # set autocommit on becouse it's a small app (and in dont want to deal with transactions)
    con.autocommit = True
    db = con.cursor()

    # initialize the db if ther is no data
    if not db.execute("SELECT * FROM sqlite_master").fetchall():
        db_makeTables(db)
        
    # ask to login
    return 0


def register_user(db:"Cursor") -> None:
    data = {}

    # get user name and check if it is unique
    data["user_name"] = input("Enter your username: ")
    while True:
        if not db.execute("SELECT user_name FROM users WHERE user_name = ?", [data["user_name"]]).fetchall():
            break       
        else:
            data["user_name"] = input("Username already exist please enter a unique username: ")
    
    # get first and last name
    data["first_name"] = input("Enter your first_name: ")
    data["last_name"] = input("Enter your last_name: ")

    # get password and verify it
    ph = PasswordHasher()
    while True:
        while True:
            pw = getpass("Enter your password: ")
            if len(pw) < 5 or len(pw) > 32:
                print("Password has to be at least 6 characters and at most 32")
            else:
                break
        pw2 = getpass("Verify password: ")
        if pw == pw2:
            break
        else:
            print("Passwords did not match")

    # hash the password
    data["hash"] = ph.hash(pw)

    # Put data in db
    db_register_user(db, data["user_name"], data["first_name"], data["last_name"], data["hash"])

    return 
































if __name__ == "__main__":
    main()
