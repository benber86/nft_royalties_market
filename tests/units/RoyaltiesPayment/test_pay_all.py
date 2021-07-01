import brownie
import math


def test_pay_all(splitter, alice, bob, charlie, owner):
    initial_alice_balance = alice.balance()
    initial_contract_balance = splitter.balance()
    tx = splitter.payAll({"from": owner})
    assert math.isclose(alice.balance(), initial_contract_balance / 3, rel_tol=1)
    assert math.isclose(splitter.balance(), 0, rel_tol=1)
    assert bob.balance() == charlie.balance()
    assert alice.balance() == bob.balance()
    assert initial_alice_balance < alice.balance()
    assert splitter.balances(alice)["balance"] == splitter.balances(bob)["balance"]
    assert splitter.balances(alice)["balance"] == 0
    assert len(tx.internal_transfers) == 3
    assert tx.internal_transfers[0]["value"] == tx.internal_transfers[1]["value"]


def test_pay_all_one_empty_balance(splitter, alice, owner):
    splitter.withdrawAll({"from": alice})
    tx = splitter.payAll({"from": owner})
    assert len(tx.internal_transfers) == 2


def test_pay_all_not_owner(splitter, alice):
    with brownie.reverts():
        splitter.payAll({"from": alice})
