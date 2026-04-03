from attacks.base import AttackModule, AttackRequest


class ForwardedHeadersAttack(AttackModule):
    name = "forwarded_headers"

    def supports(self, discovered_item) -> bool:
        """
        İlk sürümde sadece scan candidate olan
        page / auth / unknown kategorilerinde calıscak.
        Asset ve marketingde önceliği düşük tutcaz.


        """
        if not discovered_item.is_scan_candidate:
            return False

        if discovered_item.category in ("page", "auth", "unknown"):
            return True

        return False

    def generate(self, discovered_item) -> list[AttackRequest]:
        target = discovered_item.url

        return [
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "X-Forwarded-Host": "evil.example.com",
                },
                category_hint=discovered_item.category,
                note="host override test",
            ),
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "X-Forwarded-Proto": "http",
                },
                category_hint=discovered_item.category,
                note="proto downgrade test",
            ),
            AttackRequest(
                attack_name=self.name,
                target_url=target,
                headers={
                    "X-Forwarded-Host": "evil.example.com",
                    "X-Forwarded-Proto": "http",
                },
                category_hint=discovered_item.category,
                note="combined host+proto test",
            ),
        ]