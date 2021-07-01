import brownie
from brownie import ZERO_ADDRESS
import pytest

PRICE = 100


@pytest.mark.parametrize("price", [0, 100, 1e18])
def test_accept_buy_offer(market, token_id, token, alice, price, bob):
    bob_initial_balance = bob.balance()
    alice_initial_balance = alice.balance()
    expected_royalties = (price * token.royaltiesPercentage()) // 100
    net_sale_amount = price - expected_royalties

    market.makeBuyOffer(token_id, {"from": bob, "value": price})
    tx = market.acceptBuyOffer(token_id, {"from": alice})

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


def test_accept_inexistent_buy_offer(market, token_id, alice):
    with brownie.reverts("No buy offer"):
        market.acceptBuyOffer(token_id, {"from": alice})


def test_accept_buy_offer_non_owned_token(market, token_id, bob):
    with brownie.reverts("Not token owner"):
        market.acceptBuyOffer(token_id, {"from": bob})


def test_accept_buy_offer_non_approved(market, token, alice, bob):
    token_id = token.mint(bob, "2").return_value
    market.makeBuyOffer(token_id, {"from": alice, "value": PRICE})
    with brownie.reverts("Not approved"):
        market.acceptBuyOffer(token_id, {"from": bob})
