import brownie
from brownie import ZERO_ADDRESS
import pytest


MIN_PRICE = 100


def test_withdraw_sell_offer(market, token_id, alice):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    tx = market.withdrawSellOffer(token_id, {"from": alice})
    assert market.activeSellOffers(token_id) == (ZERO_ADDRESS, 0)
    assert len(tx.events) == 1
    assert tx.events["SellOfferWithdrawn"]["tokenId"] == token_id
    assert tx.events["SellOfferWithdrawn"]["seller"] == alice


def test_withdraw_sell_offer_not_seller(market, token_id, alice, bob, owner):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    with brownie.reverts("Not seller"):
        market.withdrawSellOffer(token_id, {"from": bob})
    with brownie.reverts("Not seller"):
        market.withdrawSellOffer(token_id, {"from": owner})


def test_withdraw_nonexistent_sell_offer(market, token_id, alice):
    with brownie.reverts("No sale offer"):
        market.withdrawSellOffer(token_id, {"from": alice})


def test_withdraw_sell_offer_not_approved(market, token_id, token, alice):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    token.approve(ZERO_ADDRESS, token_id, {"from": alice})
    with brownie.reverts("Not approved"):
        market.withdrawSellOffer(token_id, {"from": alice})


def test_withdraw_sell_offer_token_approved_not_owned(
    market, token_id, token, alice, bob
):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    token.safeTransferFrom(alice, bob, token_id, {"from": alice})
    token.approve(market, token_id, {"from": bob})
    with brownie.reverts("Not seller"):
        market.withdrawSellOffer(token_id, {"from": bob})
    tx = market.withdrawSellOffer(token_id, {"from": alice})
    assert market.activeSellOffers(token_id) == (ZERO_ADDRESS, 0)
    assert len(tx.events) == 1
    assert tx.events["SellOfferWithdrawn"]["tokenId"] == token_id
    assert tx.events["SellOfferWithdrawn"]["seller"] == alice
