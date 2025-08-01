import sqlite3
import csv as Csv
import os
import re
from argon2 import PasswordHasher
from getpass import getpass
from db_util import *
from typing import List, Set, Tuple


LOGEDIN = False
CSVKEYS = ["amount", "cas-nr", "chemical", "unit"]

def main() -> int:
    # connect to database
    con = sqlite3.connect("lims.db")

    # set autocommit on becouse it"s a small app (and in dont want to deal with transactions)
    con.autocommit = False
    db = con.cursor()
    ph = PasswordHasher()

    # initialize the db if ther is no data
    if not db.execute("SELECT * FROM sqlite_master").fetchall():
        db_makeTables(db)
        con.commit()
    
    #TODO: Add welkome text
    #TODO: List user options what to do
    #TODO: show logs can filter logs on [date, time, person, chemical]
    # needs to be logd in to do the following things
    #TODO: add_chemicals
    #TODO: remove_chemicals 
    #TODO: use_chemicals
    #TODO: restock_chemicals
    #TODO: admin that can do following things but add name of other user
    # api stuff
    #TODO: request info of chemical with api of pubchem
    # ask to login
    user_id = login(db, ph)
    con.commit()
    add_chemical(db, con, user_id)
    #import_csv(db, con, user_id)
    show_stock(db)
    return 0

#TODO: Add color massege when somthing goes wrong and succces massege when they log in
def login(db:sqlite3.Cursor, ph:PasswordHasher) -> int:
    while True:
        user_name = input("Enter your username: ")
        pw = getpass("Enter your password: ")

        # check if user name exist
        if not db_get_user_info(db, user_name):
            print("User name or password is wrong please try again")
            continue

        # check if password is correct
        user_id, first_name, last_name, hash = db_get_user_info(db, user_name)
        try:
            ph.verify(hash, pw)
        except:
            print("User name or password is wrong please try again")
            continue

        if ph.check_needs_rehash(hash):
            db_set_hash_for_user(db, user_name, ph.hash(pw))

        LOGEDIN = True
        return user_id



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
    return True if db_get_user_info(db, user_name) else False

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

#TODO: add filters
def show_stock(db: Cursor) -> None:
    names, stock = db_get_stock(db)
    if not stock:
        print("There are no items in stock")
        return
    #TODO: add color to print

    #HACK: get length of longest str (This is slow !!!)
    n = len(stock[0])
    items_len = [len(name) for name in names]
    for row in stock:
        for i, item in enumerate(row):
            if items_len[i] < len(str(item)):
                items_len[i] = len(str(item))
    
    print("+" + "-" * (len(items_len) - 1 + sum(items_len)) + "+")
    for i, name in enumerate(names):
        n = len(name)
        left = (items_len[i] - n) // 2
        right = items_len[i] - left - n
        print("|" + " " * left + name + " " * right, end="")
    print("|")

    for i, row in enumerate(stock):
        print("+", end="")
        for l in items_len:
            print("-" * l + "+", end="")
        print()

        for y, item in enumerate(row):
            print("|" + str(item) + " " * (items_len[y] - len(str(item))), end="")
        print("|")
    print("+" + "-" * (len(items_len) - 1 + sum(items_len)) + "+")
    return

# TODO: users needs to be logd in !!!
def add_chemical(db:Cursor, con:sqlite3.Connection, user_id:int) -> None:
    #TODO: input validation loop
    cas_nr = input("Etner cas-nr: ")
    if not is_valid_cas_nr(cas_nr):
        pass
    chemical = input("Ether name of chemical: ")
    amount = input("Enter amount of chemical: ")
    if not is_valid_amount(amount):
        pass
    amount = float(amount)
    unit = input("Enter unit: ")
    if not is_valid_unit(unit):
        pass

    wrong_data = db_add_chemicals(db, [(cas_nr, chemical, amount, unit)], user_id)
    if wrong_data:
        for values in wrong_data:
            print_wrong_value(values)
        
    #con.commit()
    return

# TODO: users needs to be logd in !!!
def import_csv(db:Cursor, con:sqlite3.Connection,  user_id:int) -> None:
    path = os.getcwd()
    files = os.listdir(path + "/input_csv")
    csvs = []
    for file in files:
        if re.search(r"\.csv$", file):
            csvs.append(file)
    if not csvs:
        print("Please put csv file in folder \"input_csv\"")
        return

    print("csv's found:")
    for i, csv in enumerate(csvs):
        print(f"({i}) {csv}")

    #TODO: validate respons
    respons = input("Enter number of csv to add to data base\nEnter * to add all\n\nInput: ")
    
    data = {}
    if respons == "*":
        # import all
        for csv in csvs:
            data[csv] = get_csv_data(csv)
    else:
        data[csvs[int(respons)]] = get_csv_data(csvs[int(respons)])
    
    # add data to db and get posible wrong data
    for key in data.keys():
        data[key]["discard"].extend(db_add_chemicals(db, data[key]["data"], user_id))
    #con.commit()
    
    
    #TODO: write nice user massege

    for key in data.keys():
        # move input file to output directory
        os.rename(path + "/input_csv/" + key, path + "/output_csv/Done_" + key)

        # If there is wrong data put it in a output file and tel the user
        if data[key]["discard"]:
            with open(path + "/output_csv/" + "FIX_" + key, "w", newline="") as out_csv:
                writer = Csv.writer(out_csv)
                writer.writerow(["cas-nr", "chemical","amount", "unit"])
                for values in data[key]["discard"]:
                    writer.writerow(values)
                    print_wrong_value(values)
    return

def print_wrong_value(values:Tuple[str, str, float, str]) -> None:
    #TODO: do colors bether
    red = "\033[31m"
    reset = "\033[0m"
    bold = "\033[01m"
    orange = "\033[43m"
    green = "\033[32m"

    text = ""
    for value in values:
        value = str(value)
        if value.find("!") != -1:
            text += f"{bold}{red}READY EXIST: {reset}"
            value.replace("!", "")
        if  value.find("*") != -1:
            text += f"{bold}{red}{value.replace("*", "")}{reset},"
        else:
            text += f"{bold}{green}{value},{reset}"
    # text[:-1] to remove last ","
    print(text[:-1])

def get_csv_data(name: str) -> Dict:
    # open csv
    path = os.getcwd() + "/input_csv/"
    with open(path + name, newline= "") as f:
        reader = Csv.DictReader(f)
        if reader.fieldnames != None and set(CSVKEYS) != set(reader.fieldnames):
            print(f"The top row of the {name} need to have the names: cas-nr,chemical,amount,unit")

        # extract data from csv
        data = []
        discard = []
        for row in reader:
            # check values of import and add "*" infront if invalid for later styled print
            valid = True
            if is_valid_cas_nr(row["cas-nr"]):
                cas_nr = row["cas-nr"]
            else:
                valid = False
                cas_nr = "*" + row["cas-nr"]

            if is_valid_amount(row["amount"]):
                amount = float(row["amount"])
            else:
                valid = False
                amount = "*" + row["amount"]

            if is_valid_unit(row["unit"]):
                unit = row["unit"].lower()
            else:
                valid = False
                unit = "*" + row["unit"].lower()

            if valid:
                data.append((cas_nr, row["chemical"], amount, unit))
            else:
                discard.append((cas_nr, row["chemical"], amount, unit))

        return {"data": data, "discard": discard}


#WARN: list of values can be done smarter i think becouse if you change it in the db you need to change it hir to
def is_valid_unit(unit: str) -> bool:
    return True if unit.lower() in ("g", "kg", "mg", "ml", "l") else False

def is_valid_amount(amount: str) -> bool:
    try:
        num = float(amount)
        if num < 0:
            return False
        else:
            return True
    except ValueError:
        return False

#NOTE:This can be done BUT you need to check the name with the cas-nr API and i don"t know if you want to do this.....
def is_valid_chemical(chemical: str) -> bool:
    pass

def is_valid_cas_nr(cas_nr: str) -> bool:
    # check pattern
    if not re.search(r"^\d{2,7}-\d\d-\d$", cas_nr):
        return False

    # check if last digit is correct
    cas_nr = cas_nr.replace("-", "")
    n = len(cas_nr)
    sum = 0
    for i in range(n - 1):
        sum += int(cas_nr[i]) * (n - i - 1)
    if sum % 10 != int(cas_nr[-1]):
        return False
    return True
















if __name__ == "__main__":
    main()
