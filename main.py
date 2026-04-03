import asyncio
import aiohttp

from cli import parse_args
from core.orchestrator import ScanOrchestrator
from core.scheduler import select_balanced_attacks
from attacks.registry import load_attack_modules
from detection.validator import AttackValidator
from output.writers import build_report_data, write_report


MAX_ATTACK_EXECUTION = 20


async def async_main():
    config = parse_args()

    print("[+] Starting scanner")
    print(f"[+] Target: {config.target_url}")
    print(f"[+] Max depth: {config.max_depth}")
    print(f"[+] Max pages: {config.max_pages}")

    orchestrator = ScanOrchestrator(config)
    result = await orchestrator.run()

    print(f"\n[+] Crawled pages: {len(result['crawled_pages'])}")
    print(f"[+] Discovered URLs: {len(result['discovered_urls'])}")
    print(f"[+] Scan candidates: {len(result['scan_candidates'])}")

    print("\n[+] Crawled page summary:")
    for page in result["crawled_pages"][:10]:
        if page["error"]:
            print(f" - [ERROR] {page['url']} -> {page['error']}")
        else:
            print(
                f" - [{page['status']}] {page['url']} "
                f"[cache_vendor={page['cache_vendor']}, cache_status={page['cache_status']}]"
            )

    print("\n[+] Cache hint details:")
    for page in result["crawled_pages"][:10]:
        if not page["error"]:
            print(
                f" - {page['url']} -> "
                f"{page['cache_vendor']} / {page['cache_status']} / {page['cache_evidence']}"
            )

    print("\n[+] Sample discovered URLs:")
    for item in result["discovered_urls"][:20]:
        print(
            f" - {item.url} "
            f"[source={item.source}, category={item.category}, "
            f"candidate={item.is_scan_candidate}, in_scope={item.in_scope}]"
        )

    print("\n[+] Sample scan candidates:")
    for item in result["scan_candidates"][:20]:
        print(
            f" - {item.url} "
            f"[source={item.source}, category={item.category}, in_scope={item.in_scope}]"
        )

    modules = load_attack_modules()
    generated_attacks = []

    print(f"\n[+] Loaded attack modules: {[m.name for m in modules]}")

    for item in result["scan_candidates"]:
        for module in modules:
            if module.supports(item):
                generated_attacks.extend(module.generate(item))

    print(f"\n[+] Generated attack requests: {len(generated_attacks)}")

    print("\n[+] Sample generated attacks:")
    for attack in generated_attacks[:20]:
        print(
            f" - [{attack.attack_name}] {attack.target_url} "
            f"[category={attack.category_hint}] "
            f"headers={attack.headers} "
            f"note={attack.note}"
        )

    to_execute = select_balanced_attacks(
        generated_attacks,
        limit=MAX_ATTACK_EXECUTION,
    )

    print(
        f"\n[+] Executing balanced sample of {len(to_execute)} attack requests "
        f"(category + module aware)..."
    )

    print("\n[+] Selected attacks for execution:")
    for attack in to_execute:
        print(
            f" - [{attack.attack_name}] {attack.target_url} "
            f"[category={attack.category_hint}] note={attack.note}"
        )

    validator = AttackValidator(
        timeout=config.timeout,
        concurrency=config.concurrency,
    )

    execution_results = []
    async with aiohttp.ClientSession() as session:
        for attack in to_execute:
            result_item = await validator.execute(session, attack)
            execution_results.append(result_item)

    changed_count = sum(1 for item in execution_results if item["changed"])
    validation_changed_count = sum(1 for item in execution_results if item["validation_changed"])
    suspicious_count = sum(1 for item in execution_results if item["suspicious_cache_effect"])
    error_count = sum(1 for item in execution_results if item["error"])

    print(f"\n[+] Executed attacks: {len(execution_results)}")
    print(f"[+] Attack response changed: {changed_count}")
    print(f"[+] Validation response changed: {validation_changed_count}")
    print(f"[+] Suspicious cache effect: {suspicious_count}")
    print(f"[+] Errors: {error_count}")

    print("\n[+] Sample execution results:")
    for item in execution_results[:20]:
        if item["error"]:
            print(
                f" - [{item['attack_name']}] {item['target_url']} "
                f"-> ERROR: {item['error']}"
            )
            continue

        print(
            f" - [{item['attack_name']}] {item['target_url']} "
            f"[attack_changed={item['changed']}, validation_changed={item['validation_changed']}, "
            f"suspicious_cache_effect={item['suspicious_cache_effect']}] "
            f"status={item['baseline_status']}->{item['attack_status']}->{item['validation_status']} "
            f"length={item['baseline_length']}->{item['attack_length']}->{item['validation_length']} "
            f"note={item['note']} cb={item['cache_buster_value']}"
        )

        if item["attack_evidence"]:
            for ev in item["attack_evidence"][:3]:
                print(f"    * attack: {ev}")

        if item["validation_evidence"]:
            for ev in item["validation_evidence"][:3]:
                print(f"    * validation: {ev}")

    if config.output_path:
        report_data = build_report_data(result, execution_results)
        write_report(config.output_path, report_data)
        print(f"\n[+] Report written to: {config.output_path}")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()