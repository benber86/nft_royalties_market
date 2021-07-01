import brownie
import math


def test_receive_no_remainder(splitter, alice, bob, charlie, david):
    original_alice_balance = splitter.balances(alice)["balance"]
    original_contract_balance = splitter.balance()
    david.transfer(to=splitter, amount=3e19)
    assert splitter.balances(alice)["balance"] == splitter.balances(bob)["balance"]
    assert splitter.balances(alice)["balance"] == splitter.balances(charlie)["balance"]
    assert splitter.balances(alice)["balance"] - original_alice_balance == 1e19
    assert splitter.balance() == original_contract_balance + 3e19


def test_receive_remainder(splitter, alice, bob, charlie, david):
    original_alice_balance = splitter.balances(alice)["balance"]
    david.transfer(to=splitter, amount=2e19)
    assert splitter.balances(alice)["balance"] == splitter.balances(bob)["balance"]
    assert splitter.balances(alice)["balance"] == splitter.balances(charlie)["balance"]
    assert math.isclose(
        splitter.balances(alice)["balance"] - original_alice_balance,
        2e19 / 3,
        rel_tol=1,
    )
    splitter.payAll()
    assert splitter.balance() == (2e19 % 3)
