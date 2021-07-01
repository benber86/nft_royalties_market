import pytest
import brownie

TEST_HASH = "TEST"


@pytest.fixture(scope="function", autouse=True)
def token_id(token, alice, market):
    token_id = token.mint(alice, TEST_HASH).return_value
    token.approve(market, token_id, {"from": alice})
    yield token_id


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
