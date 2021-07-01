import brownie


def test_set_royalties_receiver(token, owner, alice, royalty_wallet):
    previous_royalties_receiver = token.royaltiesReceiver().return_value
    token.setRoyaltiesReceiver(alice, {"from": owner})
    new_royalties_receiver = token.royaltiesReceiver().return_value
    assert previous_royalties_receiver == royalty_wallet
    assert previous_royalties_receiver != new_royalties_receiver
    assert new_royalties_receiver == alice


def test_set_royalties_receiver_not_owner(token, bob):
    with brownie.reverts():
        token.setRoyaltiesReceiver(bob, {"from": bob})


def test_set_royalties_receiver_same_address(token, owner, royalty_wallet):
    with brownie.reverts():
        token.setRoyaltiesReceiver(royalty_wallet, {"from": owner})
