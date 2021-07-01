import brownie
import pytest


@pytest.mark.parametrize("amount", [1, 100, 1e18])
def test_withdraw(splitter, alice, bob, amount):
    initial_alice_balance = alice.balance()
    initial_contract_balance = splitter.balance()
    initial_alice_contract_balance = splitter.balances(alice)["balance"]
    initial_bob_balance = bob.balance()
    splitter.withdraw(amount, {"from": alice})
    assert alice.balance() - initial_alice_balance == amount
    assert initial_bob_balance == bob.balance()
    assert (
        splitter.balances(alice)["balance"] == initial_alice_contract_balance - amount
    )
    assert splitter.balance() == initial_contract_balance - amount


def test_withdraw_zero_amount(splitter, alice):
    with brownie.reverts():
        splitter.withdraw(0, {"from": alice})


def test_withdraw_over_balance(splitter, alice):
    with brownie.reverts():
        splitter.withdraw(splitter.balances(alice)["balance"] + 1, {"from": alice})


def test_withdraw_full_balance(splitter, alice):
    splitter.withdraw(splitter.balances(alice)["balance"], {"from": alice})
    assert splitter.balances(alice)["balance"] == 0


def test_withdraw_not_payee(splitter, owner):
    with brownie.reverts():
        splitter.withdraw(100, {"from": owner})
