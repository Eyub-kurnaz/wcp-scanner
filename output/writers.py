import json
from pathlib import Path
from dataclasses import asdict, is_dataclass


def _serialize_item(item):
    if is_dataclass(item):
        return asdict(item)
    return item


def _serialize_list(items):
    return [_serialize_item(item) for item in items]


def build_report_data(scan_result: dict, execution_results: list[dict]) -> dict:
    discovered_urls = _serialize_list(scan_result.get("discovered_urls", []))
    scan_candidates = _serialize_list(scan_result.get("scan_candidates", []))
    crawled_pages = scan_result.get("crawled_pages", [])

    return {
        "target": scan_result.get("target"),
        "summary": {
            "crawled_pages": len(crawled_pages),
            "discovered_urls": len(discovered_urls),
            "scan_candidates": len(scan_candidates),
            "executed_attacks": len(execution_results),
            "changed_attacks": sum(1 for item in execution_results if item.get("changed")),
            "validation_changed_attacks": sum(
                1 for item in execution_results if item.get("validation_changed")
            ),
            "suspicious_cache_effects": sum(
                1 for item in execution_results if item.get("suspicious_cache_effect")
            ),
            "errors": sum(1 for item in execution_results if item.get("error")),
        },
        "crawled_pages": crawled_pages,
        "discovered_urls": discovered_urls,
        "scan_candidates": scan_candidates,
        "execution_results": execution_results,
    }


def write_json_report(path: str, report_data: dict) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)


def write_text_report(path: str, report_data: dict) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = report_data.get("summary", {})
    crawled_pages = report_data.get("crawled_pages", [])
    discovered_urls = report_data.get("discovered_urls", [])
    scan_candidates = report_data.get("scan_candidates", [])
    execution_results = report_data.get("execution_results", [])

    lines = []
    lines.append("WCP Scanner Report")
    lines.append("=" * 80)
    lines.append(f"Target: {report_data.get('target')}")
    lines.append("")

    lines.append("Summary")
    lines.append("-" * 80)
    lines.append(f"Crawled pages: {summary.get('crawled_pages', 0)}")
    lines.append(f"Discovered URLs: {summary.get('discovered_urls', 0)}")
    lines.append(f"Scan candidates: {summary.get('scan_candidates', 0)}")
    lines.append(f"Executed attacks: {summary.get('executed_attacks', 0)}")
    lines.append(f"Changed attacks: {summary.get('changed_attacks', 0)}")
    lines.append(f"Validation changed attacks: {summary.get('validation_changed_attacks', 0)}")
    lines.append(f"Suspicious cache effects: {summary.get('suspicious_cache_effects', 0)}")
    lines.append(f"Errors: {summary.get('errors', 0)}")
    lines.append("")

    lines.append("Crawled Pages")
    lines.append("-" * 80)
    for page in crawled_pages[:50]:
        lines.append(
            f"[{page.get('status')}] {page.get('url')} "
            f"(cache_vendor={page.get('cache_vendor')}, cache_status={page.get('cache_status')})"
        )
    lines.append("")

    lines.append("Sample Discovered URLs")
    lines.append("-" * 80)
    for item in discovered_urls[:50]:
        lines.append(
            f"{item.get('url')} "
            f"[source={item.get('source')}, category={item.get('category')}, "
            f"candidate={item.get('is_scan_candidate')}, in_scope={item.get('in_scope')}]"
        )
    lines.append("")

    lines.append("Sample Scan Candidates")
    lines.append("-" * 80)
    for item in scan_candidates[:50]:
        lines.append(
            f"{item.get('url')} "
            f"[source={item.get('source')}, category={item.get('category')}, in_scope={item.get('in_scope')}]"
        )
    lines.append("")

    lines.append("Execution Results")
    lines.append("-" * 80)
    for item in execution_results[:100]:
        if item.get("error"):
            lines.append(
                f"[{item.get('attack_name')}] {item.get('target_url')} "
                f"ERROR: {item.get('error')}"
            )
            continue

        lines.append(
            f"[{item.get('attack_name')}] {item.get('target_url')} "
            f"attack_changed={item.get('changed')} "
            f"validation_changed={item.get('validation_changed')} "
            f"suspicious_cache_effect={item.get('suspicious_cache_effect')} "
            f"status={item.get('baseline_status')}->{item.get('attack_status')}->{item.get('validation_status')} "
            f"length={item.get('baseline_length')}->{item.get('attack_length')}->{item.get('validation_length')} "
            f"note={item.get('note')} cb={item.get('cache_buster_value')}"
        )

        for ev in item.get("attack_evidence", [])[:3]:
            lines.append(f"  attack: {ev}")

        for ev in item.get("validation_evidence", [])[:3]:
            lines.append(f"  validation: {ev}")

    lines.append("")

    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_report(path: str, report_data: dict) -> None:
    lower_path = path.lower()

    if lower_path.endswith(".json"):
        write_json_report(path, report_data)
        return

    if lower_path.endswith(".txt"):
        write_text_report(path, report_data)
        return

    raise ValueError("Unsupported output format. Use .json or .txt")