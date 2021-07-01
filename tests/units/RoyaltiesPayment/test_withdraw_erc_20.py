import brownie
from brownie_tokens import ERC20


def test_withdraw_erc_20(splitter, owner, alice, charlie, bob, token):
    splitter.withdrawErc20(token, {"from": owner})
    assert token.balanceOf(bob) == token.balanceOf(alice)
    assert token.balanceOf(bob) == token.balanceOf(charlie)


def test_withdraw_erc_20_not_owner(splitter, alice, token):
    with brownie.reverts():
        splitter.withdrawErc20(token, {"from": alice})


def test_withdraw_erc_20_not_received(splitter, david, owner):
    token = ERC20("CoinTest", "CTST", 8)
    token._mint_for_testing(david, 10 ** 19)
    with brownie.reverts():
        splitter.withdrawErc20(token, {"from": owner})
