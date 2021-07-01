import brownie


BASE_URI = "https://gateway.pinata.cloud/ipfs/"
TEST_HASH = "TEST"


def test_token_uri(token, alice):
    token_id = token.mint(alice, TEST_HASH).return_value
    assert token.tokenURI(token_id) == BASE_URI + TEST_HASH
