import brownie
from brownie import ZERO_ADDRESS
import pytest

PRICE = 100
DAY = 86400


def verify_tx_valid(tx, token_id_to_test, buyer, price):
    assert len(tx.events) == 1
    assert tx.events["NewBuyOffer"]["tokenId"] == token_id_to_test
    assert tx.events["NewBuyOffer"]["buyer"] == buyer
    assert tx.events["NewBuyOffer"]["value"] == price


def test_make_buy_offer_no_sell_offer(market, token_id, bob):
    initial_contract_balance = market.balance()
    initial_bob_balance = bob.balance()
    tx = market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    assert market.buyOffersEscrow(bob, token_id) == PRICE
    assert market.balance() == initial_contract_balance + PRICE
    assert bob.balance() == initial_bob_balance - PRICE
    assert market.activeBuyOffers(token_id) == (bob, PRICE, tx.timestamp)

    verify_tx_valid(tx, token_id, bob, PRICE)


def test_owner_make_buy_offer(market, token_id, alice):
    with brownie.reverts("Token owner not allowed"):
        market.makeBuyOffer(token_id, {"from": alice, "value": PRICE})


def test_make_buy_offer_unapproved_token(market, token, bob, alice):
    token_id = token.mint(alice, "2").return_value
    tx = market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    verify_tx_valid(tx, token_id, bob, PRICE)


def test_make_buy_offer_unminted_token(market, token_id, bob):
    with pytest.raises(brownie.exceptions.VirtualMachineError):
        market.makeBuyOffer(token_id + 1, {"from": bob, "value": PRICE})
    with pytest.raises(brownie.exceptions.VirtualMachineError):
        market.makeBuyOffer(0, {"from": bob, "value": PRICE})


def test_make_buy_offer_lower_sale_offer(market, token_id, bob, alice):
    market.makeSellOffer(token_id, PRICE, {"from": alice})
    assert market.activeSellOffers(token_id)["minPrice"] == PRICE
    with brownie.reverts("Sell order at this price or lower exists"):
        market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    with brownie.reverts("Sell order at this price or lower exists"):
        market.makeBuyOffer(token_id, {"from": bob, "value": PRICE - 1})


def test_replace_non_expired_buy_offer_lower(market, token_id, bob, charlie):
    market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    with brownie.reverts("Previous buy offer higher or not expired"):
        market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    with brownie.reverts("Previous buy offer higher or not expired"):
        market.makeBuyOffer(token_id, {"from": charlie, "value": PRICE - 1})


def test_replace_non_expired_buy_offer_higher(market, token_id, bob, charlie):
    initial_contract_balance = market.balance()
    initial_bob_balance = bob.balance()
    initial_charlie_balance = charlie.balance()
    market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})

    tx = market.makeBuyOffer(token_id, {"from": charlie, "value": PRICE + 1})

    verify_tx_valid(tx, token_id, charlie, PRICE + 1)
    assert market.buyOffersEscrow(bob, token_id) == 0
    assert market.buyOffersEscrow(charlie, token_id) == PRICE + 1
    assert market.balance() == initial_contract_balance + PRICE + 1
    assert bob.balance() == initial_bob_balance
    assert charlie.balance() == initial_charlie_balance - (PRICE + 1)
    assert market.activeBuyOffers(token_id) == (charlie, PRICE + 1, tx.timestamp)


def test_replace_expired_buy_offer(market, chain, token_id, bob, charlie):
    initial_contract_balance = market.balance()
    initial_bob_balance = bob.balance()
    initial_charlie_balance = charlie.balance()
    market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})

    chain.sleep(DAY + 1)
    tx = market.makeBuyOffer(token_id, {"from": charlie, "value": PRICE - 1})
    verify_tx_valid(tx, token_id, charlie, PRICE - 1)
    assert market.buyOffersEscrow(bob, token_id) == 0
    assert market.buyOffersEscrow(charlie, token_id) == PRICE - 1
    assert market.balance() == initial_contract_balance + PRICE - 1
    assert bob.balance() == initial_bob_balance
    assert charlie.balance() == initial_charlie_balance - (PRICE - 1)
    assert market.activeBuyOffers(token_id) == (charlie, PRICE - 1, tx.timestamp)

    chain.sleep(DAY + 1)
    tx = market.makeBuyOffer(token_id, {"from": bob, "value": PRICE})
    verify_tx_valid(tx, token_id, bob, PRICE)
    assert market.buyOffersEscrow(charlie, token_id) == 0
    assert market.buyOffersEscrow(bob, token_id) == PRICE
    assert market.balance() == initial_contract_balance + PRICE
    assert charlie.balance() == initial_charlie_balance
    assert bob.balance() == initial_bob_balance - (PRICE)
    assert market.activeBuyOffers(token_id) == (bob, PRICE, tx.timestamp)
