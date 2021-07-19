# Write your code here
import random
import string
import sys
import sqlite3
card_cache = {}
state = 1
card_list = []

class Card:
    def __init__(self, card_no, pin):
        self.card_no = card_no
        self.pin = pin
        self.balance = 0
        self.login = True

    # def create_card(self, card_no, pin):
    def check_login(self, card_no, pin):
        if self.card_no == card_no and self.pin == pin:
            self.login = True
        else:
            self.login = False
        return self.login

    def logout(self):
        self.login = False
        print("You have successfully logged out!")

    def get_balance(self):
        return self.balance


def get_rand_no(length):
    no = string.digits
    result_str = ''.join(random.choice(no) for i in range(length))
    return result_str

def gen_checksum(main_card_no):
    main_no = main_card_no
    main_no = list(main_no)
    for i in range(len(main_no)):
        if i % 2 == 0:
            val = int(main_no[i])
            val = val * 2
            if val > 9:
                val = val - 9
                val = str(val)
            main_no[i] = val
        main_no[i] = str(main_no[i])
    result = 0
    for i in range(len(main_no)):
        result = result + int(main_no[i])
    if (result % 10 != 0):
        temp = result % 10
        checksum = 10 - temp
    else:
        checksum = 0
    return checksum

def check_luhn(credit_card_no):
    last_no = int(credit_card_no[-1])
    new_card_no = credit_card_no[0:15]
    if last_no != gen_checksum(new_card_no):
        return False
    else:
        return True

def check_db(recipient):
    recipient_str = recipient
    query_string ='''SELECT number, pin, balance FROM card
        WHERE number =?;
        '''
    data_tuple = (recipient_str,)
    cur.execute(query_string, data_tuple)
    conn.commit()
    result = cur.fetchall()
    if len(result) == 1:
        return True
    else:
        return False

def check_match(recipient, c_no):
    if recipient == c_no:
        return True
    else:
        return False


def get_balance(c_no, pin_no=0):
    if (pin_no== 0):
        query_string ='''SELECT balance FROM card
                    WHERE number =?
                    '''
        data_tuple = (c_no,)
        cur.execute(query_string, data_tuple)
        conn.commit()
        result_set = cur.fetchall()
        return result_set[0][0]
    else:
        query_string ='''SELECT balance FROM card
                        WHERE number =? AND pin = ?
                        '''
        data_tuple = (c_no, pin_no)
        cur.execute(query_string, data_tuple)
        conn.commit()
        result_set = cur.fetchall()
        return result_set[0][0]
def set_new_balance(c_no, pin_no, money):
    money = money + get_balance(c_no)
    query_string = '''UPDATE card
    SET balance = ?
    WHERE number = ? AND pin = ?;'''
    data_tuple = (money, c_no, pin_no)
    cur.execute(query_string, data_tuple)
    conn.commit()
def set_balance(c_no, new_balance, pin_no=0, money = 0):
    if (pin_no == 0 and money==0):
        query_string = '''UPDATE card
        SET balance = ?
        WHERE number = ?;'''
        data_tuple = (new_balance, c_no)
        cur.execute(query_string, data_tuple)
        conn.commit()
    else:
        query_string = '''UPDATE card
        SET balance = ?
        WHERE number = ? AND pin = ?;'''
        data_tuple = (money, c_no, pin)
        cur.execute(query_string, data_tuple)
        conn.commit()

def delete_acct(c_no):
    query_string = '''DELETE FROM card
    WHERE number = ?;'''
    data_tuple = (c_no,)
    cur.execute(query_string, data_tuple)
    conn.commit()
# gen_checksum(IIN,acc_id)
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
query_string = '''CREATE TABLE card (
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
);'''
cur.execute("DROP TABLE IF EXISTS card")
cur.execute(query_string)
conn.commit()
i = 0
while True:
    print("1. Create an account")
    print("2. Log into an account")
    print("0. Exit")
    prompt = input()
    IIN = "400000"
    # checksum = get_rand_no(1)
    acc_id = get_rand_no(9)
    main_card_no = IIN + acc_id
    checksum = gen_checksum(main_card_no)
    card_no_main = IIN + acc_id + str(checksum)
    pin = get_rand_no(4)
    if prompt == "0":
        print("Bye!")
        break
    if prompt == "1":
        my_card = Card(card_no_main, pin)
        print("Your card has been created")
        print("Your card number:")
        print(f"{my_card.card_no}")
        print("Your card pin:")
        print(f"{my_card.pin}")
        card_list.append(my_card)
        i += 1
        query_string = '''INSERT INTO card (id, number, pin) 
        VALUES (?,?,?);'''
        data_tuple = (i, my_card.card_no, my_card.pin)
        cur.execute(query_string, data_tuple)
        conn.commit()
        # query_string = 'SELECT * FROM card'
        # cur.execute(query_string)
        # conn.commit()
        # print(cur.fetchone())
    if prompt == "2":
        print("Enter your card number")
        c_no = input()
        print("Enter your pin")
        pin_no = input()
        # c.execute("SELECT * FROM passwordDb WHERE employee_username=?", (username, ))
        query_string ='''SELECT number, pin, balance FROM card
        WHERE number =? AND pin = ?
        '''
        data_tuple = (c_no, pin_no)
        cur.execute(query_string, data_tuple)
        conn.commit()
        result = cur.fetchall()
        # print(result)
        # print(len(result))
        if len(result) == 1:
            login = True
        else:
            login = False
        if login:
            print("You have successfully logged in")
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                prompt = input()
                if prompt == "1":
                    print(f"Balance: {get_balance(c_no)}")
                if prompt == "2":
                    print("Enter income:")
                    money = int(input())
                    set_new_balance(c_no=c_no, pin_no=pin_no, money=money)
                    print("Income was added!")
                if prompt == "3":
                    print("Transfer")
                    print("Enter card number")
                    recipient = input()
                    cond1 = (check_luhn(recipient))
                    cond2 = (check_db(recipient))
                    cond3 = (check_match(recipient, c_no))
                    if (cond1 == False): # 4000004844972293
                        print("Probably you made a mistake in the card number. Please try again")
                        continue
                    if (cond1 == True and cond2 == False):
                        print("Such a card does not exist.")
                    if (cond3 == True):
                        print("You can't transfer money to the same account!")
                    if cond1 == True and cond2 == True and cond3 == False:
                        print("Enter how much money you want to transfer:")
                        transfer_money = int(input())
                        if get_balance(c_no) < transfer_money:
                            print("Not enough money")
                        else:
                            print("You have the money")
                            # you have to decrement balance and increment balance
                            new_balance = get_balance(c_no) - transfer_money
                            recipient_balance = get_balance(recipient) + transfer_money
                            set_balance(c_no, new_balance)
                            set_balance(recipient, recipient_balance)

                if prompt == "4":
                    delete_acct(c_no)
                    print("The account has been closed!")
                    break
                if prompt == "5":
                    # card_list[curr_index].logout()
                    break
                if prompt == "0":
                    sys.exit()
        else:
            print("Wrong card number or PIN!")

