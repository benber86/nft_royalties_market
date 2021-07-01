import brownie
from brownie.test import strategy


class StateMachine:

    address = strategy("address", length=10)

    def __init__(self, accounts, RoyaltiesPayment):
        self.accounts = accounts
        self.payees = [accounts[1], accounts[2]]
        self.contract = RoyaltiesPayment.deploy(self.payees, {"from": accounts[0]})

    def setup(self):
        self.payees = [self.accounts[1], self.accounts[2]]

    def rule_remove_user(self, address):
        if address in self.payees:
            self.contract.removePayee(address, {"from": self.accounts[0]})
            self.payees[self.payees.index(address)] = self.payees[-1]
            self.payees = self.payees[:-1]
        else:
            with brownie.reverts():
                self.contract.removePayee(address, {"from": self.accounts[0]})

    def rule_add_user(self, address):
        if address not in self.payees:
            self.contract.addPayee(address, {"from": self.accounts[0]})
            self.payees.append(address)
        else:
            with brownie.reverts():
                self.contract.addPayee(address, {"from": self.accounts[0]})

    def invariant(self):
        for i, payee in enumerate(self.payees):
            assert self.contract.payees(i) == payee
            assert self.contract.balances(payee)["userIndex"] == i + 1


def test_add_remove_payees(state_machine, RoyaltiesPayment, accounts):
    state_machine(
        StateMachine, accounts[:10], RoyaltiesPayment, settings={"max_examples": 15}
    )
