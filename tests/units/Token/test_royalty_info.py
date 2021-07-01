import brownie
import pytest

TEST_HASH = "TEST"


def test_royalty_info(token, alice, royalty_wallet):
    value = 1000
    tx_mint = token.mint(alice, TEST_HASH)
    token_id = tx_mint.return_value
    tx_royalty = token.royaltyInfo(token_id, value)
    receiver = tx_royalty["receiver"]
    royalties = tx_royalty["royaltyAmount"]
    assert receiver == royalty_wallet
    assert royalties == (value * token.royaltiesPercentage()) // 100


def test_overflow(token, alice):
    value = 2 ** 256
    tx_mint = token.mint(alice, TEST_HASH)
    token_id = tx_mint.return_value
    with pytest.raises(OverflowError):
        token.royaltyInfo(token_id, value)
