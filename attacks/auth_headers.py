from attacks.base import AttackModule, AttackRequest


class AuthHeadersAttack(AttackModule):
    name = "auth_headers"

    def supports(self, discovered_item) -> bool:
        """
        Bu modül auth/api 'e uygun.
        İlk sürümde sadece scan candidate olan
        auth, api ve unknown kategorilerinde calıscacak.
        """
        if not discovered_item.is_scan_candidate:
            return False

        if discovered_item.category in ("auth", "api", "unknown"):
            return True

        return False

    def generate(self, discovered_item) -> list[AttackRequest]:
        target = discovered_item.url

        return [
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "Authorization": "Bearer invalid-test-token",
                },
                category_hint=discovered_item.category,
                note="invalid bearer token test",
            ),
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "X-Auth-User": "attacker",
                },
                category_hint=discovered_item.category,
                note="x-auth-user spoof test",
            ),
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "Auth-Key": "invalid-auth-key",
                },
                category_hint=discovered_item.category,
                note="auth-key spoof test",
            ),
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "Authorization": "Basic Zm9vOmJhcg==",
                    "X-Auth-User": "attacker",
                },
                category_hint=discovered_item.category,
                note="combined auth header test",
            ),
        ]