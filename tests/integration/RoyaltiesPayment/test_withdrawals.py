import brownie
from brownie.test import strategy
import math


class StateMachine:

    value = strategy("uint256", min_value=1, max_value="100 ether")
    withdrawal = strategy("uint256", min_value=1, max_value="20 ether")
    address = strategy("address", length=5)

    def __init__(cls, accounts, RoyaltiesPayment):
        cls.accounts = accounts
        cls.contract = RoyaltiesPayment.deploy(accounts[1:], {"from": accounts[0]})

    def setup(self):
        self.balance = 0
        self.payouts = 0
        self.total_deposits = 0
        self.user_balances = {account: 0 for account in self.accounts[1:]}

    def rule_add_user(self, address):
        if self.contract.balances(address)["userIndex"] == 0:
            self.contract.addPayee(address, {"from": self.accounts[0]})
            self.user_balances = {account: 0 for account in self.accounts[1:]}
            self.user_balances[address] = 0
            self.payouts += 1

    def rule_deposit(self, value):
        self.accounts[0].transfer(to=self.contract, amount=value)
        self.balance += value
        self.total_deposits += value
        self.user_balances = {
            k: v + (value // len(self.user_balances))
            for k, v in self.user_balances.items()
        }

    def rule_withdraw(self, address, withdrawal):
        if (address in self.user_balances) and self.user_balances[address] >= withdrawal:
            self.contract.withdraw(withdrawal, {"from": address})
            self.user_balances[address] -= withdrawal
            self.balance -= withdrawal
        else:
            with brownie.reverts():
                self.contract.withdraw(withdrawal, {"from": address})

    def rule_withdraw_all(self, address):
        if (address in self.user_balances) and self.user_balances[address] > 0:
            self.contract.withdrawAll({"from": address})
            self.balance -= self.user_balances[address]
            self.user_balances[address] = 0
        else:
            with brownie.reverts():
                self.contract.withdrawAll({"from": address})

    def invariant(self):
        math.isclose(self.contract.balance(), self.balance, rel_tol=self.payouts)
        for user, amount in self.user_balances.items():
            assert math.isclose(
                self.contract.balances(user)["balance"], amount, rel_tol=self.payouts
            )
            assert amount <= (self.total_deposits // len(self.user_balances))


def test_withdrawals(state_machine, RoyaltiesPayment, accounts):
    state_machine(
        StateMachine, accounts, RoyaltiesPayment, settings={"max_examples": 30}
    )
