import re


def is_valid_trx_address(address):
    if len(address) != 42:
        return False
    if not address.startswith("T"):
        return False
    if not re.match("^[a-fA-F0-9]*$", address[2:]):
        return False
    return True
