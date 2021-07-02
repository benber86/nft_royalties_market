import brownie
from brownie.test import strategy
from brownie import ZERO_ADDRESS
import math


class StateMachine:

    value = strategy("uint256", min_value=25, max_value="10 ether")
    tokens_to_buy = strategy("uint256", max_value=5)
    address = strategy("address", length=5)

    def __init__(self, accounts, RoyaltiesPayment, Token, Marketplace):
        self.accounts = accounts
        self.royalty_wallet = RoyaltiesPayment.deploy(
            accounts[1:2], {"from": accounts[0]}
        )
        self.token = Token.deploy(self.royalty_wallet, {"from": accounts[0]})
        self.market = Marketplace.deploy(self.token, {"from": accounts[0]})

    def setup(self):
        self.total_paid = 0
        self.token_owners = {
            account: [
                self.token.mint(
                    account, str(i), {"from": self.accounts[0]}
                ).return_value
            ]
            for i, account in enumerate(self.accounts)
        }
        self.token_count = len(self.accounts)

    def rule_mint(self, address):
        if address in self.token_owners:
            self.token_owners[address].append(
                self.token.mint(
                    address, str(self.token_count), {"from": self.accounts[0]}
                ).return_value
            )
            self.token_count += 1

    def rule_sell_offer(self, value):
        for i, account in enumerate(self.token_owners):
            if len(self.token_owners[account]) > 0:
                self.token.approve(
                    self.market, self.token_owners[account][0], {"from": account}
                )
                self.market.makeSellOffer(
                    self.token_owners[account][0], value, {"from": account}
                )

    def rule_purchase(self, address, tokens_to_buy, value):
        for token_id in range(tokens_to_buy):
            offer = self.market.activeSellOffers(token_id + 1)
            if (
                (token_id + 1) not in self.token_owners[address]
                and offer["seller"] != ZERO_ADDRESS
                and offer["minPrice"] <= value
            ):
                self.market.purchase(token_id + 1, {"from": address, "value": value})
                self.total_paid += ((value * 5) // 100)
                self.token_owners[offer["seller"]].pop(self.token_owners[offer["seller"]].index(token_id + 1))
                self.token_owners[address].append(token_id + 1)

    def invariant(self):
        assert self.royalty_wallet.balance() == self.total_paid


def test_royalties_payout(
    state_machine, accounts, RoyaltiesPayment, Token, Marketplace
):
    state_machine(
        StateMachine,
        accounts[:5],
        RoyaltiesPayment,
        Token,
        Marketplace,
        settings={"max_examples": 15},
    )
