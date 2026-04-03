from collections import defaultdict, deque


def select_balanced_attacks(attacks: list, limit: int = 20) -> list:
    """
    Attack request'leri category + attack_name bazında bucketlara ayırır
    ve round-robin şekilde dengeli bir örneklem seçer.
    Amaç:
    - tek bir kategori tüm sampleı doldurmasın
    -  bir modül tüm sampleı doldurmasın
    """
    if limit <= 0 or not attacks:
        return []

    buckets: dict[tuple[str, str], deque] = defaultdict(deque)

    for attack in attacks:
        category = attack.category_hint or "unknown"
        key = (category, attack.attack_name)
        buckets[key].append(attack)

    selected = []
    bucket_keys = list(sorted(buckets.keys()))

    while len(selected) < limit and bucket_keys:
        still_active = []

        for key in bucket_keys:
            bucket = buckets[key]

            if bucket:
                selected.append(bucket.popleft())

                if len(selected) >= limit:
                    break

            if bucket:
                still_active.append(key)

        bucket_keys = still_active

    return selected