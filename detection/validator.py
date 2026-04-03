import aiohttp

from attacks.base import AttackRequest
from core.cache_buster import CacheBuster
from core.http_client import AsyncHttpClient
from detection.diff_analyzer import analyze_difference


class AttackValidator:
    def __init__(self, timeout: int = 10, concurrency: int = 10):
        self.client = AsyncHttpClient(timeout=timeout, concurrency=concurrency)
        self.cache_buster = CacheBuster()

    async def execute(self, session: aiohttp.ClientSession, attack: AttackRequest) -> dict:
        """
        3-request modeli:

        1) baseline req-> cache buster ile temiz normal request
        2) attack requ-> aynı cache buster ile mutated request
        3) validation req-> aynı cache buster ile tekrar temiz request
        """
        cb_value = self.cache_buster.new_value()

        baseline_url = self.cache_buster.apply(attack.target_url, cb_value)
        attack_url = self.cache_buster.apply(attack.target_url, cb_value)
        validation_url = self.cache_buster.apply(attack.target_url, cb_value)

        baseline = await self.client.fetch(
            session,
            method=attack.method,
            url=baseline_url,
        )

        attack_resp = await self.client.fetch(
            session,
            method=attack.method,
            url=attack_url,
            headers=attack.headers,
        )

        validation = await self.client.fetch(
            session,
            method=attack.method,
            url=validation_url,
        )

        if baseline.error or attack_resp.error or validation.error:
            return {
                "attack_name": attack.attack_name,
                "target_url": attack.target_url,
                "note": attack.note,
                "category_hint": attack.category_hint,
                "headers": attack.headers,
                "error": baseline.error or attack_resp.error or validation.error,
                "changed": False,
                "validation_changed": False,
                "suspicious_cache_effect": False,
                "attack_evidence": [],
                "validation_evidence": [],
            }

        attack_diff = analyze_difference(baseline, attack_resp)
        validation_diff = analyze_difference(baseline, validation)

        # attack response değişmiş mi?
        changed = attack_diff["changed"]

        # validation response baseline'dan farklı mı?
        validation_changed = validation_diff["changed"]

        # kaba ilk heuristic:
        # attack değiştiyse ve validation da değişiyorsa,
        # bu cache etkisi / kalıcılık yönünde şüpheli bir sinyal olabilir
        suspicious_cache_effect = changed and validation_changed

        return {
            "attack_name": attack.attack_name,
            "target_url": attack.target_url,
            "note": attack.note,
            "category_hint": attack.category_hint,
            "headers": attack.headers,
            "error": None,

            "changed": changed,
            "validation_changed": validation_changed,
            "suspicious_cache_effect": suspicious_cache_effect,

            "attack_evidence": attack_diff["evidence"],
            "validation_evidence": validation_diff["evidence"],

            "baseline_status": baseline.status,
            "attack_status": attack_resp.status,
            "validation_status": validation.status,

            "baseline_length": attack_diff["baseline_length"],
            "attack_length": attack_diff["mutated_length"],
            "validation_length": validation_diff["mutated_length"],

            "cache_buster_value": cb_value,
        }