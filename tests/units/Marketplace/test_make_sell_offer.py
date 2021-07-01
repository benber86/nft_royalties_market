import brownie
import pytest

MIN_PRICE = 100


@pytest.mark.parametrize("price", [0, 100, 1e18])
def test_make_sell_offer(market, token_id, alice, price):
    tx = market.makeSellOffer(token_id, price, {"from": alice})
    seller, price = market.activeSellOffers(token_id)
    assert seller == alice
    assert price == price
    assert len(tx.events) == 1
    assert tx.events["NewSellOffer"]["tokenId"] == token_id
    assert tx.events["NewSellOffer"]["seller"] == alice
    assert tx.events["NewSellOffer"]["value"] == price


def test_make_sell_offer_unapproved_token(market, token, alice):
    token_id = token.mint(alice, "unnaproved_token").return_value
    with brownie.reverts("Not approved"):
        market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})


def test_make_sell_offer_non_owner(market, token_id, alice, bob):
    with brownie.reverts("Not token owner"):
        market.makeSellOffer(token_id, MIN_PRICE, {"from": bob})


def test_make_sell_offer_non_existent_token(market, alice, token):
    with pytest.raises(brownie.exceptions.VirtualMachineError):
        market.makeSellOffer(1e18, MIN_PRICE, {"from": alice})
    token_id = token.mint(alice, "new_token").return_value
    token.approve(market, token_id, {"from": alice})
    with pytest.raises(brownie.exceptions.VirtualMachineError):
        market.makeSellOffer(token_id + 1, MIN_PRICE, {"from": alice})


def test_make_two_sell_offers(market, token_id, alice):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    tx = market.makeSellOffer(token_id, MIN_PRICE + 1, {"from": alice})
    seller, price = market.activeSellOffers(token_id)
    assert seller == alice
    assert price == MIN_PRICE + 1
    assert len(tx.events) == 1
    assert tx.events["NewSellOffer"]["tokenId"] == token_id
    assert tx.events["NewSellOffer"]["seller"] == alice
    assert tx.events["NewSellOffer"]["value"] == MIN_PRICE + 1


def replace_old_owner_sell_offer(market, token, token_id, alice):
    market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})
    token.safeTransferFrom(alice, bob, token_id, {"from": alice})
    token.approve(market, token_id, {"from": bob})
    with brownie.reverts("Not token owner"):
        market.makeSellOffer(token_id, MIN_PRICE, {"from": alice})

    tx = market.makeSellOffer(token_id, MIN_PRICE + 1, {"from": bob})
    seller, price = market.activeSellOffers(token_id)
    assert seller == bob
    assert price == MIN_PRICE + 1
    assert len(tx.events) == 1
    assert tx.events["NewSellOffer"]["tokenId"] == token_id
    assert tx.events["NewSellOffer"]["seller"] == bob
    assert tx.events["NewSellOffer"]["value"] == MIN_PRICE + 1
