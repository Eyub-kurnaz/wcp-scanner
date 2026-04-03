from attacks.forwarded_headers import ForwardedHeadersAttack
from attacks.auth_headers import AuthHeadersAttack


def load_attack_modules():
    return [
        ForwardedHeadersAttack(),
        AuthHeadersAttack(),
    ]