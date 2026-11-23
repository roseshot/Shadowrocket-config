# Domain synchronization and registration audit

The [scheduled workflow](../.github/workflows/domain-audit.yml) runs daily at **03:00 UTC** and can also be started manually. It does not run on ordinary pushes. The audit runs under Python 3.15.

## What it does

1. Downloads the `accelerated-domains.china.conf` file from [dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list/blob/master/accelerated-domains.china.conf), then regenerates the static P6b `DIRECT` section of [`shadowrocket.conf`](../shadowrocket.conf). If the upstream fetch fails, the previous configuration is retained.
2. Inventories **only** `DOMAIN`, `DOMAIN-SUFFIX`, and `DOMAIN-WILDCARD` rules with action `DIRECT` in the `[Rule]` section. All registrable subdomains share one Public Suffix List registration root.
3. Checks registration status with the IANA RDAP bootstrap and a WHOIS fallback. Explicit `PROXY` and `REJECT-DROP` rules are never inspected or deleted for registration expiry.
4. Validates the generated configuration and cache in memory before writing files: section order, immutable non-import content (apart from confirmed-invalid `DIRECT` rules), P6b format and ordering, and cache schema.
5. Saves updated registration observations and writes a single per-run change log containing both `ADD` and `DEL` entries. The workflow validates `shadowrocket.conf` formatting, checks the generated diff, and commits changed files only when those checks succeed.

## Scheduling and deletion safeguards

- Up to **2,000** registrable domains are selected per run by default. Due and unobserved manually managed `DIRECT` domains take priority over the imported P6b set.
- For domains with a known expiry, the three fixed UTC checkpoints are **expiration day (day 0)**, **day +62**, and **day +90**. The dates are never randomized, moved, or backfilled after a missed run. A newly observed renewal resets the entire checkpoint sequence.
- A `DIRECT` rule can be removed for registration expiry **only when all three checkpoints explicitly confirm an expired registration** with the same expiration date and no grace period. RDAP `not_found`, WHOIS errors, rate limits, network failures, and uncertain or missed checks do not count. Missing any checkpoint prevents deletion for that expiration date.
- The registration check does not establish DNS availability, current host ownership, or whether a service is safe to access.

## Files

| File | Purpose |
| --- | --- |
| [`scripts/sync_and_audit_domains.py`](../scripts/sync_and_audit_domains.py) | Synchronization and registration audit |
| [`scripts/check_conf_format.py`](../scripts/check_conf_format.py) | Lightweight Shadowrocket profile format check |
| [`scripts/requirements-domain-audit.txt`](../scripts/requirements-domain-audit.txt) | Python dependencies |
| [`data/domain-expiry-cache.json`](../data/domain-expiry-cache.json) | Persistent registration observations and fixed-date check evidence (version 1) |
| [`logs/changes.log`](../logs/changes.log) | Net `ADD` and `DEL` domain-rule changes from the latest run; deletions include their reason |

The log is overwritten on **every** successful run, including runs with no changes. Each changed rule is prefixed with `ADD` or `DEL`; deletions are annotated with `registration_expired` or `upstream` as applicable. Git history retains previous run snapshots. The cache is durable application state, not a disposable build artifact. The cache retains version 1 with fixed-date check evidence. Legacy randomized review fields and historical deletion evidence are not accepted.

## Local commands

Run from the repository root:

```bash
python scripts/check_conf_format.py shadowrocket.conf
python -m pip install --upgrade -r scripts/requirements-domain-audit.txt
python scripts/sync_and_audit_domains.py --max-checks 2000 --workers 4 --timeout 12
```

The final command performs network requests and **can modify** the main profile, cache, and logs. Use `--no-sync` to audit without fetching the upstream domain list.

The scheduled workflow upgrades dependencies and checks the generated profile's section layout and directive formats before committing. No push-triggered CI or unit-test suite is configured. The format checker is structural and does not guarantee compatibility with every Shadowrocket client version.
