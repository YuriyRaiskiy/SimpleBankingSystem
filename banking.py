# Write your code here
import random
import sqlite3

global currently_used_card


# Write your code here
class SimpleBankingSystem:

    def __init__(self):
        self.welcome_menu = '1. Create an account\n' \
                            '2. Log into account\n' \
                            '0. Exit\n'
        self.account_menu = '1. Balance\n' \
                            '2. Add income\n' \
                            '3. Do transfer\n' \
                            '4. Close account\n' \
                            '5. Log out\n' \
                            '0. Exit\n'
        self.closed_account_message = '\nThe account has been closed!\n'
        self.added_income_message = '\nIncome was added!\n'
        self.user_card_PIN = int()
        self.existing_cards = dict()
        self.user_created_cards = int()
        # initialize user card number with default IIN that is 400000
        self.bank_identification_number = [int(digit) for digit in '400000']
        self.user_created_cards = int()
        self.card_exists = False
        self.invalid_input_message = '\nWrong card number of PIN!\n'
        self.log_in_message = '\nYou have successfully logged in!\n'
        self.log_out_message = '\nYou have successfully logged out!\n'
        self.goodbye_message = '\nBye!'
        self.chosen_card = dict()
        self.correct_user_input = False
        self.full_exit = False
        self.conn = sqlite3.connect('card.s3db')
        self.cursor = self.conn.cursor()
        # create table card if it doesn't exist
        self.cursor.execute('CREATE TABLE IF NOT EXISTS card ('
                            '                                 id INTEGER, '
                            '                                 number TEXT, '
                            '                                 pin TEXT, '
                            '                                 balance INTEGER DEFAULT 0 '
                            '                                )')
        # calculate number of rows in table card
        self.cursor.execute('SELECT * FROM card')
        self.user_created_cards = len(self.cursor.fetchall())

    def user_interface(self):
        # terminate process if user chose Exit in account menu
        while not self.full_exit:
            # welcome user and process his menu option
            user_choice = input(self.welcome_menu)
            # terminate program execution if user chose 0. Exit menu option
            if user_choice == '0':
                break
            # create an account if user chose to
            elif user_choice == '1':
                SimpleBankingSystem.create_an_account(self)
            # go to login menu if user chose to
            elif user_choice == '2':
                SimpleBankingSystem.log_into_account(self)
        print(self.goodbye_message)
        # close connection to cards database
        self.conn.close()

    # script for Luhn algorithm
    def run_Luhn_algorithm(self, card_number):
        # create temp list that stores first 15 card digits to find control number using Luhn algorithm
        card_15_digits = []
        # run Luhn algorithm to find control number for generated card number
        # step 1: multiply odd digits by 2
        for i in range(len(card_number)):
            # check if digit is odd
            if i % 2 == 0:
                card_15_digits.append(card_number[i] * 2)
            else:
                card_15_digits.append(card_number[i])
            # step 2: subtract 9 to numbers over 9
            if card_15_digits[i] > 9:
                card_15_digits[i] -= 9
        # find checksum digit using control number for generated 15 digits of card number and append it
        # to the card number
        # check if checksum digit should be 0
        if sum(card_15_digits) % 10 == 0:
            card_number.extend([0])
        else:
            card_number.extend([10 - sum(card_15_digits) % 10])

    def create_an_account(self):
        user_card_number = []
        # generate first 15 digits for user card
        user_card_number.extend(self.bank_identification_number)
        user_card_number.extend([random.randint(0, 9) for _i in range(0, 9)])
        # run Luhn algorithm to get checksum digit and finish card number generation
        SimpleBankingSystem.run_Luhn_algorithm(self, user_card_number)
        user_card_number = ''.join(str(digit) for digit in user_card_number)
        # generate PIN for user card
        user_card_pin = ''.join([str(random.randint(0, 9)) for _i in range(0, 4)])
        print(f'\nYour card has been created\n'
              f'Your card number:\n{user_card_number}\n'
              f'Your card PIN:\n{user_card_pin}\n')
        # increase number of user created cards
        self.user_created_cards += 1
        # store created card credentials in card.s3db
        self.cursor.execute(f'INSERT INTO card(id, number, pin) '
                            f'VALUES('
                            f'      {self.user_created_cards},'
                            f'      {user_card_number}, '
                            f'      {user_card_pin})'
                            )

        # save changes
        self.conn.commit()

    def log_into_account(self):
        global currently_used_card
        # store currently used card value in memory
        currently_used_card = input('\nEnter your card number:\n')
        # check if card credentials provided by user exist in 'cards' table
        self.cursor.execute('SELECT number, pin '
                            'FROM card '
                            'WHERE number=? AND pin=?',
                            (
                                currently_used_card,
                                input('Enter your PIN:\n')
                            )
                            )
        # proceed with login to user account if user provided card number that exists in 'card' database
        # and correct PIN for it
        if self.cursor.fetchall():
            SimpleBankingSystem.work_with_account(self)
        else:
            print(self.invalid_input_message)

    # script to display current card balance
    def display_balance(self):
        current_card_balance = self.cursor.execute('SELECT balance FROM card '
                                                   'WHERE number = ?', (currently_used_card,)
                                                   ).fetchall()[0][0]
        return f'\nBalance: {current_card_balance}\n'

    # script for updating card balance with income provided by user
    def add_income(self, income):
        global currently_used_card
        self.cursor.execute('UPDATE card '
                            'SET balance = balance + ?'
                            'WHERE number = ?', (income, currently_used_card)
                            )
        # save changes
        self.conn.commit()
        return self.added_income_message

    # script for making transfers between cards stored in database card.s3db
    def do_transfer(self):
        global currently_used_card
        # get current balance for user card
        current_card_balance = self.cursor.execute('SELECT balance FROM card '
                                                   'WHERE number = ?', (currently_used_card,)
                                                   ).fetchall()[0][0]
        # specify card number for transfer
        transfer_card = [int(digit) for digit in input('\nTransfer\nEnter card number:\n')]
        # check if transfer card number has the same number with currently used card
        if ''.join([str(digit) for digit in transfer_card]) == currently_used_card:
            return f'You can\'t transfer money to the same account!\n'
        # get first 15 card numbers for Luhn algorithm
        transfer_card_to_check = [int(transfer_card[i]) for i in range(len(transfer_card) - 1)]
        # run Luhn algorithm for transfer card
        SimpleBankingSystem.run_Luhn_algorithm(self, transfer_card_to_check)
        # output error message if transfer card number didn't pass Luhn algorithm
        if transfer_card_to_check != transfer_card:
            return f'Probably you made mistake in the card number. Please try again!\n'
        # check if transfer card exists in database
        try:
            self.cursor.execute('SELECT number FROM card '
                                'WHERE number=?', (''.join([str(digit) for digit in transfer_card]),)
                                ).fetchall()[0][0]
        except IndexError:
            return f'Such a card does not exist.\n'
        # specify transfer amount
        transfer_amount = int(input('Enter how much money you want to transfer:\n'))
        # check if transfer amount is available on currently used card
        if current_card_balance < transfer_amount:
            return f'Not enough money!\n'
        else:
            # proceed with transfer
            # update balance of card which user makes transfer from
            self.cursor.execute('UPDATE card '
                                'SET balance = balance - ?'
                                'WHERE number = ?', (transfer_amount, currently_used_card)
                                )
            # update balance of card which receives transfer
            self.cursor.execute('UPDATE card '
                                'SET balance = balance + ?'
                                'WHERE number = ?', (transfer_amount, ''.join([str(digit) for digit in transfer_card]))
                                )
            # save changes
            self.conn.commit()
            return 'Success!\n'

    # script for closing user account
    def close_account(self):
        global currently_used_card
        # store all current ids in the list current_ids and print them
        current_ids = [_id[0] for _id in self.cursor.execute('SELECT id FROM card').fetchall()]
        # print(f'Current IDs are: {current_ids}')
        # get id of currently used card
        currently_used_card_id = self.cursor.execute('SELECT id FROM card '
                                                     'WHERE number=?', (currently_used_card,)
                                                     ).fetchall()[0][0]
        # get index of currently_used_card_id in current_ids list and print it
        currently_used_card_id_index = current_ids.index(currently_used_card_id)
        # delete chosen card from 'card' table
        self.cursor.execute('DELETE FROM card '
                            'WHERE number=?', (currently_used_card,))
        # update IDs in the 'card' table
        for i in range(currently_used_card_id_index + 1, len(current_ids)):
            # select next to deleted card from the table
            next_card_number = self.cursor.execute('SELECT number FROM card '
                                                   'WHERE id=?', (i + 1, )
                                                   ).fetchall()[0][0]
            # update next card number id to its id minus 1
            self.cursor.execute('UPDATE card '
                                'SET id=? '
                                'WHERE number=?', (i, next_card_number)
                                )
        # save changes
        self.conn.commit()
        return self.closed_account_message

    def work_with_account(self):
        print(self.log_in_message)
        while True:
            user_input = input(self.account_menu)
            # exit account if user chose to
            if user_input == '0':
                self.full_exit = True
                break
            # display card balance
            elif user_input == '1':
                print(SimpleBankingSystem.display_balance(self))
            # add income if user chose to
            elif user_input == '2':
                print(SimpleBankingSystem.add_income(self, input('\nEnter income:\n')))
            # make card2card transfer
            elif user_input == '3':
                print(SimpleBankingSystem.do_transfer(self))
            # delete user account if user chose to
            elif user_input == '4':
                print(SimpleBankingSystem.close_account(self))
                # return to the previous menu
                break
            # log out and return to previous menu is user chose to
            elif user_input == '2':
                print(self.log_out_message)
                break


if __name__ == '__main__':
    # create class instance and enable user interface
    banking_system = SimpleBankingSystem()
    banking_system.user_interface()
