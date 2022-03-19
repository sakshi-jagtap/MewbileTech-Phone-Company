"""
CSC148, Winter 2022
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.
        bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]
    end: datetime.date
    return_deposit: bool
    date: datetime.date
    started: bool
    deposit: int

    def __init__(self, start: datetime.date = datetime.date(2017, 12, 25),
                 end: datetime.date = datetime.date(2019, 6, 25)) -> None:
        Contract.__init__(self, start)
        self.end = end
        self.return_deposit = False
        self.deposit = int(TERM_DEPOSIT)
        self.date = start
        self.bill = None
        self.started = False

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        """
        self.bill = bill
        if self.date.month != month or self.date.year != year:
            bill.set_rates("term", TERM_MINS_COST)
            bill.add_fixed_cost(TERM_MONTHLY_FEE)
            bill.free_min = 0
            bill.billed_min = 0

        elif (self.date.month == self.start.month or self.date.year
              == self.start.year) and not self.started:
            bill.free_min = 0
            bill.billed_min = 0
            bill.set_rates("term", TERM_MINS_COST)
            bill.add_fixed_cost(TERM_MONTHLY_FEE + TERM_DEPOSIT)
            self.started = True
        self.date = datetime.date(year, month, 1)
        if self.end <= datetime.date(year, month, 1):
            self.return_deposit = True

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

            Precondition:
            - a bill has already been created for the month+year when the <call>
            was made. In other words, you can safely assume that self.bill
            has been
            already advanced to the right month+year.
            """

        if TERM_MINS >= self.bill.free_min + ceil(call.duration / 60):
            self.bill.add_free_minutes(ceil(call.duration / 60))
        else:
            amount_free = TERM_MINS - self.bill.free_min
            free_used = ceil(call.duration / 60) - amount_free
            self.bill.add_billed_minutes(free_used)
            self.bill.free_min = TERM_MINS

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        if self.return_deposit:
            return self.bill.get_cost() - TERM_DEPOSIT
        else:
            return self.bill.get_cost()


class MTMContract(Contract):
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    bill: Optional[Bill]
    date: datetime.date
    started: bool

    def __init__(self, start: datetime.date = datetime.date(2017, 12, 25)) \
            -> None:
        Contract.__init__(self, start)
        self.bill = None
        self.date = start
        self.started = False

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        """
        self.bill = bill
        if self.date.month != month or self.date.year != year:
            bill.set_rates("mtm", MTM_MINS_COST)
            bill.add_fixed_cost(MTM_MONTHLY_FEE)
            self.date = datetime.date(year, month, 1)
            bill.free_min = 0
            bill.billed_min = 0
        if self.date.month == self.start.month or self.date.year \
                == self.start.year and not self.started:
            bill.set_rates("mtm", MTM_MINS_COST)
            bill.add_fixed_cost(MTM_MONTHLY_FEE)
            self.date = datetime.date(year, month, 1)
            bill.free_min = 0
            bill.billed_min = 0

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

            Precondition:
            - a bill has already been created for the month+year when the <call>
            was made. In other words, you can safely assume that self.bill has
            been
            already advanced to the right month+year.
            """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        self.started = False
        return self.bill.get_cost()


class PrepaidContract(Contract):
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]
    return_deposit: bool
    date: datetime.date
    started: bool
    balance: int

    def __init__(self, start: datetime.date = datetime.date(2017, 12, 25),
                 balance: int = 100) -> None:
        Contract.__init__(self, start)
        self.bill = None
        self.date = start
        self.balance = abs(balance) * -1
        self.started = False

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        """

        self.bill = bill
        bill.set_rates("prepaid", PREPAID_MINS_COST)

        if self.date.month != month or self.date.year != year:
            if self.balance > -10:
                self.balance = self.balance - 25
            bill.add_fixed_cost(self.balance)
            bill.free_min = 0
            bill.billed_min = 0

        elif (self.date.month == self.start.month or self.date.year
              == self.start.year) and not self.started:
            if self.balance > -10:
                self.balance = self.balance - 25
            bill.add_fixed_cost(self.balance)
            self.started = True
            bill.free_min = 0
            bill.billed_min = 0
        self.date = datetime.date(year, month, 1)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))
        self.balance -= ceil(call.duration / 60) * PREPAID_MINS_COST

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.started = False
        if self.balance > 0:
            return self.balance
        return 0


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
