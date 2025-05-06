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
    register_user(db)
    return 0


def register_user(db:"Cursor") -> None:
    data = {}

    # get user name and check if it is unique
    data["user_name"] = get_user_name(db)
    
    # get first and last name
    data["first_name"] = get_first_name()
    data["last_name"] = get_last_name()

    # get password and hash it
    ph = PasswordHasher()
    data["hash"] = ph.hash(get_password())

    # Ask for conformation
    while True:
        print(f"\nYou have enterd:\n(1) User name:  {data['user_name']}\n(2) First name: {data['first_name']}\n(3) Last name:  {data['last_name']}\n\nEnter the number ( ) for editing else to confirm press enter:")
        option = input()

        # check input
        while True:
            if option not in "0123":
                option = input("Please put in one of the follow numbers 0, 1, 2, 3: \n")
            else:
                break

        # check options
        if not option:
            # Put data in db
            db_register_user(db, data["user_name"], data["first_name"], data["last_name"], data["hash"])
            return
        elif option == "1":
            data["user_name"] = get_user_name(db)
        elif option == "2":
            data["first_name"] = get_first_name()
        elif option == "3":
            data["last_name"] = get_last_name()

def get_user_name(db) -> "str":
    while True:
        user_name = input("Enter your username: ")
        if not db.execute("SELECT user_name FROM users WHERE user_name = ?", [user_name]).fetchall():
            break
        else:
            user_name = input("Username already exist please enter a unique username: ")
    return user_name

def get_first_name() -> "str":
    return input("Enter your first_name: ")

def get_last_name() -> "str":
    return input("Enter your last_name: ")

def get_password() -> "str":
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
    return pw



























if __name__ == "__main__":
    main()
