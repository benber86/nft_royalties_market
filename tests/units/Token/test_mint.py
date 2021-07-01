import brownie

TEST_HASH = "TEST"


def test_mint(alice, owner, token):
    initial_balance = token.totalSupply()
    tx = token.mint(alice, "1", {"from": owner})

    assert token.totalSupply() == initial_balance + 1
    assert token.balanceOf(alice) == 1
    assert tx.return_value == 1
    assert len(tx.events) == 2
    assert tx.events["Mint"]["tokenId"] == 1
    assert tx.events["Mint"]["recipient"] == alice


def test_mint_not_owner(alice, token):
    with brownie.reverts("Ownable: caller is not the owner"):
        token.mint(alice, TEST_HASH, {"from": alice})


def test_mint_no_hash(alice, owner, token):
    with brownie.reverts():
        token.mint(alice, "", {"from": owner})


def test_mint_double_hash(alice, bob, owner, token):
    token.mint(alice, TEST_HASH, {"from": owner})
    with brownie.reverts():
        token.mint(alice, TEST_HASH, {"from": owner})
    with brownie.reverts():
        token.mint(bob, TEST_HASH, {"from": owner})
