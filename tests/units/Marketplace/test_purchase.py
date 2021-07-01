import brownie
from brownie import ZERO_ADDRESS
import pytest

TEST_HASH = "TEST"
PRICE = 100


@pytest.mark.parametrize("price", [0, 100, 1e18])
def test_purchase(alice, bob, market, token, token_id, price):
    market.makeSellOffer(token_id, price, {"from": alice})

    bob_initial_balance = bob.balance()
    alice_initial_balance = alice.balance()
    expected_royalties = (price * token.royaltiesPercentage()) // 100
    net_sale_amount = price - expected_royalties

    tx = market.purchase(token_id, {"from": bob, "value": price})

    assert token.ownerOf(token_id) == bob

    assert alice.balance() == alice_initial_balance + net_sale_amount
    assert bob.balance() == bob_initial_balance - price

    assert market.activeBuyOffers(token_id) == (ZERO_ADDRESS, 0, 0)
    assert market.activeSellOffers(token_id) == (ZERO_ADDRESS, 0)

    assert len(tx.events) == 4

    assert "Transfer" in tx.events
    assert "Approval" in tx.events

    assert tx.events["RoyaltiesPaid"]["tokenId"] == token_id
    assert tx.events["RoyaltiesPaid"]["value"] == expected_royalties

    assert tx.events["Sale"]["tokenId"] == token_id
    assert tx.events["Sale"]["seller"] == alice
    assert tx.events["Sale"]["buyer"] == bob
    assert tx.events["Sale"]["value"] == price


def test_purchase_no_sell_offer(bob, market, token_id):
    with brownie.reverts("No active sell offer"):
        market.purchase(token_id, {"from": bob, "value": PRICE})


def test_purchase_by_token_owner(alice, market, token_id):
    with brownie.reverts("Token owner not allowed"):
        market.purchase(token_id, {"from": alice, "value": PRICE})


def test_purchase_withdrawn_sell_offer(alice, bob, market, token_id):
    market.makeSellOffer(token_id, PRICE, {"from": alice})
    market.withdrawSellOffer(token_id, {"from": alice})
    with brownie.reverts("No active sell offer"):
        market.purchase(token_id, {"from": bob, "value": PRICE})


def test_purchase_low_offer(alice, bob, market, token_id):
    market.makeSellOffer(token_id, PRICE, {"from": alice})
    with brownie.reverts("Amount sent too low"):
        market.purchase(token_id, {"from": bob, "value": PRICE - 1})


def test_purchase_unapproved_token(alice, bob, market, token, token_id):
    market.makeSellOffer(token_id, PRICE, {"from": alice})
    token.approve(ZERO_ADDRESS, token_id, {"from": alice})
    with brownie.reverts("Invalid sell offer"):
        tx = market.purchase(token_id, {"from": bob, "value": PRICE})
        assert len(tx.events) == 1
        assert tx.events["SellOfferWithdrawn"]["tokenId"] == token_id
        assert tx.events["SellOfferWithdrawn"]["seller"] == alice
        assert market.activeSellOffers(token_id) == (ZERO_ADDRESS, 0)
