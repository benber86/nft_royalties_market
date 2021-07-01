import pytest
from brownie import (
    Token,
    Marketplace,
)


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


# account aliases


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def david(accounts):
    yield accounts[4]


@pytest.fixture(scope="module")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def royalty_wallet(accounts):
    yield accounts[-1]


# core contracts


@pytest.fixture(scope="module")
def token(Token, royalty_wallet, owner):
    yield Token.deploy(royalty_wallet, {"from": owner})


@pytest.fixture(scope="module")
def market(Marketplace, owner, token):
    yield Marketplace.deploy(token, {"from": owner})
