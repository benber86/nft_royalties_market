import brownie
from brownie import ZERO_ADDRESS
import pytest

PRICE = 100
DAY = 86400


@pytest.mark.parametrize("price", [0, 100, 1e18])
def test_withdraw_buy_offer(market, chain, token_id, bob, price):
    initial_bob_balance = bob.balance()
    initial_contract_balance = market.balance()
    market.makeBuyOffer(token_id, {"from": bob, "value": price})
    chain.sleep(DAY + 1)
    tx = market.withdrawBuyOffer(token_id, {"from": bob})

    assert market.buyOffersEscrow(bob, token_id) == 0
    assert market.balance() == initial_contract_balance
    assert bob.balance() == initial_bob_balance
    assert market.activeBuyOffers(token_id) == (ZERO_ADDRESS, 0, 0)

    assert len(tx.events) == 1
    assert tx.events["BuyOfferWithdrawn"]["tokenId"] == token_id
    assert tx.events["BuyOfferWithdrawn"]["buyer"] == bob


def test_withdraw_unexpired_offer(market, token_id, bob):
    initial_bob_balance = bob.balance()
    market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    with brownie.reverts("Buy offer not expired"):
        market.withdrawBuyOffer(token_id, {"from": bob})
    assert bob.balance() == initial_bob_balance - PRICE
    assert market.balance() == PRICE


def test_withdraw_other_offer(market, chain, token_id, bob, charlie):
    market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    chain.sleep(DAY + 1)
    with brownie.reverts("Not buyer"):
        market.withdrawBuyOffer(token_id, {"from": charlie})


def test_withdraw_nonexistent_offer(market, token_id, bob):
    with brownie.reverts("Not buyer"):
        market.withdrawBuyOffer(token_id, {"from": bob})
