import brownie
import pytest

"""
MAX_SUPPLY = 7777

@pytest.mark.skip_coverage
def test_mint_max_supply(alice, token):
    for i in range(MAX_SUPPLY):
        token.mint(alice, str(i), {"from": alice})
    assert token.balanceOf(alice) == MAX_SUPPLY
    with brownie.reverts("All tokens minted"):
        token.mint(alice, str(MAX_SUPPLY + 1), {"from": alice})
"""
