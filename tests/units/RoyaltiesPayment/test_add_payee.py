import brownie


def test_add_payee(splitter, alice, bob, owner, david):
    initial_alice_balance = alice.balance()
    initial_contract_balance = splitter.balance()
    initial_bob_balance = bob.balance()
    splitter.addPayee(david, {"from": owner})
    assert splitter.balances(alice)["balance"] == 0
    assert splitter.balances(bob)["balance"] == 0
    assert alice.balance() > initial_alice_balance
    assert (
        alice.balance() - initial_alice_balance == bob.balance() - initial_bob_balance
    )
    assert splitter.balance() < initial_contract_balance
    assert splitter.balances(david)["userIndex"] == 4
    initial_david_balance = david.balance()
    owner.transfer(to=splitter, amount=4e19)
    splitter.withdraw(1e19, {"from": david})
    assert david.balance() - initial_david_balance == 1e19


def test_add_payee_not_owner(splitter, alice, david):
    with brownie.reverts():
        splitter.addPayee(david, {"from": alice})


def test_add_payee_already_payee(splitter, alice, bob):
    with brownie.reverts():
        splitter.addPayee(bob, {"from": alice})
