import sqlite3
from argon2 import PasswordHasher
from getpass import getpass
from db_util import *
from typing import List, Dict, Tuple

LOGEDIN = False

def main() -> int:
    # connect to database
    con = sqlite3.connect("lims.db")

    # set autocommit on becouse it"s a small app (and in dont want to deal with transactions)
    con.autocommit = True
    db = con.cursor()
    ph = PasswordHasher()

    # initialize the db if ther is no data
    if not db.execute("SELECT * FROM sqlite_master").fetchall():
        db_makeTables(db)
    
    #TODO: Add welkome text
    #TODO: List user options what to do
    #TODO: login / register
    #TODO: show_stock 
    #TODO: show logs can filter logs on [date, time, person, chemical]
    # needs to be logd in to do the following things
    #TODO: add_chemicals
    #TODO: remove_chemicals 
    #TODO: add_stock
    #TODO: remove_stock
    #TODO: import cvs
    #TODO: admin that can do following things but add name of other user
    # api stuff
    #TODO: request info of chemical with api of pubchem
    # ask to login
    first_name, last_name = login(db, ph)
    print(first_name, last_name)
    return 0

#TODO: Add color massege when somthing goes wrong and succces massege when they log in
def login(db:sqlite3.Cursor, ph:PasswordHasher) -> Tuple[str, str]:
    while True:
        user_name = input("Enter your username: ")
        pw = getpass("Enter your password: ")

        # check if user name exist
        if not check_user_exist(db, user_name):
            print("User name or password is wrong please try again")
            continue

        # check if password is correct
        first_name, last_name, hash = db_get_user_info(db, user_name)
        if not ph.verify(hash, pw):
            print("User name or password is wrong please try again")
            continue

        if ph.check_needs_rehash(hash):
            db_set_hash_for_user(db, user_name, ph.hash(pw))
        LOGEDIN = True
        return (first_name, last_name)



#TODO: Add color massege when somthing goes wrong and succces massege when they log in
def register_user(db:sqlite3.Cursor, ph:PasswordHasher) -> None:
    # get user name and check if it is unique
    user_name = register_user_name(db)
    
    # get first and last name
    first_name = get_first_name()
    last_name = get_last_name()

    # get password and hash it
    hash = ph.hash(get_password())

    # Ask for conformation
    while True:
        print(f"\nYou have enterd:\n(1) User name:  {user_name}\n(2) First name: {first_name}\n(3) Last name:  {last_name}\n\nEnter the number ( ) for editing else to confirm press enter:")
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
            db_register_user(db, user_name, first_name, last_name, hash)
            return
        elif option == "1":
            register_user_name(db)
        elif option == "2":
            first_name = get_first_name()
        elif option == "3":
            last_name = get_last_name()


def get_user_name() -> str:
    return input("Enter your username: ")

def get_first_name() -> str:
    return input("Enter your first_name: ")

def get_last_name() -> str:
    return input("Enter your last_name: ")

def check_user_exist(db: sqlite3.Cursor, user_name: str) -> bool:
    return True if db_get_username(db, user_name) else False

# NOTE: function needs bether naem
def register_user_name(db: sqlite3.Cursor) -> str:
    user_name = get_user_name()
    while True:
        if check_user_exist(db, user_name):
            user_name = input("Username already exist please enter unique user name: ")
            continue
        else:
            break
    return user_name

def get_password() -> str:
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
