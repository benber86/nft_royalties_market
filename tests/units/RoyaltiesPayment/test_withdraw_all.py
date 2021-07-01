import brownie


def test_withdraw_all(splitter, alice, bob):
    initial_alice_balance = alice.balance()
    initial_contract_balance = splitter.balance()
    initial_alice_contract_balance = splitter.balances(alice)["balance"]
    initial_bob_balance = bob.balance()
    initial_bob_contract_balance = splitter.balances(bob)["balance"]
    splitter.withdrawAll({"from": alice})
    assert alice.balance() - initial_alice_balance == initial_alice_contract_balance
    assert initial_bob_balance == bob.balance()
    assert initial_bob_contract_balance == splitter.balances(bob)["balance"]
    assert splitter.balances(alice)["balance"] == 0
    assert (
        splitter.balance() == initial_contract_balance - initial_alice_contract_balance
    )


def test_withdraw_all_zero_amount(splitter, alice):
    splitter.withdrawAll({"from": alice})
    with brownie.reverts():
        splitter.withdrawAll({"from": alice})


def test_withdraw_all_not_payee(splitter, david):
    with brownie.reverts():
        splitter.withdrawAll({"from": david})
