import brownie

INTERFACE_ID_ERC2981 = 0x2A55205A
INTERFACE_ID_ERC721 = 0x2A55205A
INTERFACE_ID_RANDOM = 0x00001337


def test_supports_interface(token):
    interfaces = [INTERFACE_ID_ERC2981, INTERFACE_ID_ERC721, INTERFACE_ID_RANDOM]
    expected_values = [True, True, False]
    for interface, supported in zip(interfaces, expected_values):
        assert token.supportsInterface(interface) == supported
