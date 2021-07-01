import brownie
import pytest


def test_remove_payee(splitter, alice, bob, owner, charlie):
    initial_alice_balance = alice.balance()
    initial_contract_balance = splitter.balance()
    splitter.removePayee(bob, {"from": owner})
    assert splitter.balances(alice)["balance"] == 0
    assert splitter.balances(charlie)["balance"] == 0
    assert alice.balance() > initial_alice_balance
    assert splitter.balance() < initial_contract_balance

    assert splitter.balances(bob)["userIndex"] == 0
    assert splitter.balances(charlie)["userIndex"] == 2

    owner.transfer(to=splitter, amount=2e19)
    initial_charlie_balance = charlie.balance()
    splitter.withdraw(1e19, {"from": charlie})
    assert charlie.balance() - initial_charlie_balance == 1e19

    with brownie.reverts():
        splitter.withdraw(1e19, {"from": charlie})
    with pytest.raises(brownie.exceptions.VirtualMachineError):
        splitter.payees(2)


def test_remove_payee_not_owner(splitter, alice, david):
    with brownie.reverts():
        splitter.removePayee(david, {"from": alice})


def test_remove_payee_not_payee(splitter, alice, david):
    with brownie.reverts():
        splitter.removePayee(david, {"from": alice})
