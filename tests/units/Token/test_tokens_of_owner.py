import brownie


def test_tokens_of_owner(token, alice):
    alice_tokens = [token.mint(alice, "1").return_value]
    assert token.tokensOfOwner(alice) == alice_tokens


def test_tokens_of_owner_no_tokens(token, alice):
    assert token.tokensOfOwner(alice) == []
