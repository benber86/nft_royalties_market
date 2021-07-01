import pytest
from brownie import RoyaltiesPayment
from brownie_tokens import ERC20


@pytest.fixture(scope="module")
def splitter(RoyaltiesPayment, alice, bob, charlie, owner):
    yield RoyaltiesPayment.deploy([alice, bob, charlie], {"from": owner})


@pytest.fixture(scope="module")
def token(david):
    token = ERC20("TestCoin", "TSTC", 8)
    token._mint_for_testing(david, 10 ** 19)
    yield token


@pytest.fixture(scope="module", autouse=True)
def setup(splitter, owner, david, token):
    owner.transfer(to=splitter, amount=3e19)
    token.transfer(splitter, 3e10, {"from": david})
