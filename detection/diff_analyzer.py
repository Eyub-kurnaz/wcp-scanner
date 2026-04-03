from models import HttpResponse


def _body_length(resp: HttpResponse) -> int:
    return len(resp.body or b"")


def analyze_difference(baseline: HttpResponse, mutated: HttpResponse) -> dict:
    """
    Baseline ve mutated response arasında temel fark analizi yapar.
    Şimdilik:
    - status code
    - body length
    - Location header
    - cache-related header değişimleri
    """
    evidence: list[str] = []
    changed = False

    baseline_headers = baseline.headers or {}
    mutated_headers = mutated.headers or {}

    # 1) status farkı
    if baseline.status != mutated.status:
        changed = True
        evidence.append(
            f"status changed: {baseline.status} -> {mutated.status}"
        )

    # 2) body length farkı
    baseline_len = _body_length(baseline)
    mutated_len = _body_length(mutated)

    if baseline_len != mutated_len:
        changed = True
        evidence.append(
            f"body length changed: {baseline_len} -> {mutated_len}"
        )

    # 3) redirect target farkı
    baseline_location = baseline_headers.get("Location") or baseline_headers.get("location")
    mutated_location = mutated_headers.get("Location") or mutated_headers.get("location")

    if baseline_location != mutated_location:
        changed = True
        evidence.append(
            f"location changed: {baseline_location!r} -> {mutated_location!r}"
        )

    # 4) cache header farkı (informational)
    baseline_x_cache = baseline_headers.get("X-Cache") or baseline_headers.get("x-cache")
    mutated_x_cache = mutated_headers.get("X-Cache") or mutated_headers.get("x-cache")

    if baseline_x_cache != mutated_x_cache:
        evidence.append(
            f"x-cache changed: {baseline_x_cache!r} -> {mutated_x_cache!r}"
        )

    baseline_cf_cache = baseline_headers.get("CF-Cache-Status") or baseline_headers.get("cf-cache-status")
    mutated_cf_cache = mutated_headers.get("CF-Cache-Status") or mutated_headers.get("cf-cache-status")

    if baseline_cf_cache != mutated_cf_cache:
        evidence.append(
            f"cf-cache-status changed: {baseline_cf_cache!r} -> {mutated_cf_cache!r}"
        )

    return {
        "changed": changed,
        "evidence": evidence,
        "baseline_status": baseline.status,
        "mutated_status": mutated.status,
        "baseline_length": baseline_len,
        "mutated_length": mutated_len,
    }