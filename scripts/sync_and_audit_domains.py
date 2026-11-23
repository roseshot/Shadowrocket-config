#!/usr/bin/env python3
"""Sync upstream domains, cache registration expirations, and remove confirmed invalid domains.

Only registrable domains are queried; subdomains share their parent's registration.
Registration expiry is checked on three fixed UTC dates: the expiration day,
62 days afterward, and 90 days afterward. All three must confirm expiration.
"""
lazy import argparse
lazy import concurrent.futures
import hashlib
lazy import json
import os
import re
lazy import socket
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Literal, NotRequired, Required, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

lazy import tldextract
lazy import whois

# This program requires Python 3.15; there is no compatibility layer.
type DomainRule = tuple[str, str]
type DomainRules = list[DomainRule]
type RegistrationStatus = Literal["active", "suspect", "unknown", "invalid"]
type RegistrationFailure = Literal["expired"]


class AuditRecord(TypedDict, total=False, closed=True):
    status: Required[RegistrationStatus]
    checked: str
    source: str
    reason: RegistrationFailure
    next_check: str
    expires: str
    check_results: dict[str, Literal["expired", "unconfirmed"]]


class LookupResult(TypedDict, closed=True):
    kind: Literal["registered", "not_found", "unknown"]
    source: str
    expiry: NotRequired[date | None]
    grace: NotRequired[bool]


type AuditRecords = dict[str, AuditRecord]
type LookupObservation = LookupResult
type ImportStats = dict[str, str | int]

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket.conf"
CACHE = ROOT / "data" / "domain-expiry-cache.json"
CHANGES_LOG = ROOT / "logs" / "changes.log"
BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
RULE_KINDS = frozenset({"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD"})
LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
EXPIRE_ACTIONS = frozenset({"expiration", "expiry", "registration expiration"})
NO_MATCH = re.compile(r"(?:no match|not found|no entries found|no data found|no object found|not registered)", re.I)


# P6b upstream import and explicit PROXY/REJECT-DROP preservation.
SOURCE_URL = (
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/"
    "master/accelerated-domains.china.conf"
)
START = "# ── P6b:"
END = "# ── P7:"
LINE_RE = re.compile(r"^server=/([^/]+)/114\.114\.114\.114$")
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)


@cache
def registration_extractor() -> tldextract.TLDExtract:
    """Use only ICANN suffixes; private suffixes are not registration roots."""
    return tldextract.TLDExtract(
        suffix_list_urls=(),
        include_psl_private_domains=False,
    )


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data,
        usedforsecurity=False,
    ).hexdigest()


def ancestor_or_same(domain: str, root: str) -> bool:
    return domain == root or domain.endswith("." + root)


def base_configuration(config: str) -> tuple[str, str, str]:
    """Remove the previous P6b import so filtering ignores its own rules."""
    if config.count(START) != 1 or config.count(END) != 1:
        raise ValueError("Expected exactly one P6b block and one P7 boundary")
    begin, finish = config.index(START), config.index(END)
    if begin >= finish:
        raise ValueError("P6b must appear before P7")
    return config[:begin], config[finish:], config[:begin] + config[finish:]


def compact_configuration(config: str) -> str:
    """Keep active directives and the two importer boundary markers only.

    Do not rewrite rule values, change rule ordering or delete any directive.
    The P6b/P7 markers are machine-readable synchronization boundaries.
    """
    kept = [
        line.rstrip()
        for line in config.splitlines()
        if line.strip() and (
            not line.lstrip().startswith(("#", ";"))
            or line.startswith(START) or line.startswith(END)
        )
    ]
    return "\n".join(kept) + "\n"


def explicit_actions(config_without_import: str) -> tuple[DomainRules, DomainRules]:
    protected: DomainRules = []
    direct: DomainRules = []
    for line in config_without_import.splitlines():
        match [field.strip() for field in line.split(",")]:
            case ["DOMAIN" | "DOMAIN-SUFFIX" as kind, domain, "PROXY" | "REJECT-DROP", *_]:
                protected.append((kind, domain))
            case ["DOMAIN" | "DOMAIN-SUFFIX" as kind, domain, "DIRECT", *_]:
                direct.append((kind, domain))
    return protected, direct


def protected_overlap(domain: str, protected: DomainRules) -> bool:
    return any(
        domain == other if kind == "DOMAIN" else
        ancestor_or_same(domain, other) or ancestor_or_same(other, domain)
        for kind, other in protected
    )


def direct_already_covers(domain: str, direct: DomainRules) -> bool:
    return any(
        (kind == "DOMAIN" and domain == other) or
        (kind == "DOMAIN-SUFFIX" and ancestor_or_same(domain, other))
        for kind, other in direct
    )


def create_import(config: str, source: bytes) -> tuple[str, ImportStats]:
    pre, post, base = base_configuration(config)
    text = source.decode("utf-8")
    domains = set()
    active_lines = 0
    for line in text.splitlines():
        if match := LINE_RE.fullmatch(line.strip()):
            active_lines += 1
            domains.add(match.group(1).lower())

    legal = sorted(d for d in domains if DOMAIN_RE.fullmatch(d))
    invalid_count = len(domains) - len(legal)
    protected, direct = explicit_actions(base)
    candidates = [d for d in legal if not protected_overlap(d, protected)]
    excluded_protected = len(legal) - len(candidates)
    fresh = [d for d in candidates if not direct_already_covers(d, direct)]
    excluded_direct = len(candidates) - len(fresh)
    fresh_set = set(fresh)

    def redundant(d: str) -> bool:
        labels = d.split(".")
        return any(
            ".".join(labels[i:]) in fresh_set
            for i in range(1, len(labels) - 1)
        )

    accepted = [d for d in fresh if not redundant(d)]
    excluded_redundant = len(fresh) - len(accepted)
    source_sha = git_blob_sha(source)
    # The two boundary markers are necessary to replace this block safely
    # on future syncs; no human-facing notes are written into the profile.
    block = START + "\n"
    block += "\n".join(f"DOMAIN-SUFFIX,{d},DIRECT" for d in accepted) + "\n"
    new_config = pre + block + post
    count_all = sum(
        1 for line in new_config.splitlines()
        if line.startswith((
            "DOMAIN,", "DOMAIN-SUFFIX,", "DOMAIN-WILDCARD,",
            "DOMAIN-SET,", "DOMAIN-KEYWORD,", "DST-PORT,",
            "IP-CIDR,", "IP-CIDR6,", "IP-ASN,", "GEOIP,", "FINAL,",
        ))
    )
    result = {
        "upstream_git_blob_sha": source_sha,
        "active_source_lines": active_lines,
        "valid_domains": len(legal),
        "invalid_or_top_level": invalid_count,
        "excluded_explicit_proxy_or_drop": excluded_protected,
        "excluded_already_direct": excluded_direct,
        "excluded_redundant": excluded_redundant,
        "imported_direct": len(accepted),
        "total_rule_directives": count_all,
    }
    return new_config, result


def utc_today() -> date:
    return datetime.now(UTC).date()


def read_json_url(url: str, timeout: int = 12) -> dict:
    request = Request(url, headers={"User-Agent": "Shadowrocket-domain-audit/1.0",
                                    "Accept": "application/rdap+json, application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def registration_domain(hostname: str) -> str | None:
    """Only a known public-suffix registrable domain qualifies for WHOIS/RDAP."""
    host = hostname.strip().lower().strip(".").removeprefix("*.")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return None
    if "*" in host or len(host) > 253 or not all(LABEL_RE.fullmatch(x) for x in host.split(".")):
        return None
    parts = registration_extractor()(host)
    if not parts.domain or not parts.suffix:
        return None  # TLD rules and unknown/internal suffixes are not registrations.
    return f"{parts.domain}.{parts.suffix}"


def rule_domain(line: str) -> str | None:
    """Return a registrable root only for DIRECT domain rules."""
    stripped = line.strip()
    if not stripped or stripped[0] in "#;[":
        return None
    fields = [part.strip() for part in stripped.split(",")]
    if len(fields) < 3 or fields[0] not in RULE_KINDS or fields[2] != "DIRECT":
        return None
    return registration_domain(fields[1])


def registration_roots(config: str) -> tuple[set[str], set[str]]:
    """Inventory DIRECT registration roots across all [Rule] groups.

    Return (all DIRECT roots, DIRECT roots outside imported P6b).
    """
    roots: set[str] = set()
    non_upstream: set[str] = set()
    in_rules = False
    in_upstream = False
    for line in config.splitlines():
        stripped = line.strip()
        if stripped == "[Rule]":
            in_rules = True
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_rules:
                break
            continue
        if not in_rules:
            continue
        if stripped.startswith(START):
            in_upstream = True
        elif stripped.startswith(END):
            in_upstream = False
        root = rule_domain(line)
        if root:
            roots.add(root)
            if not in_upstream:
                non_upstream.add(root)
    return roots, non_upstream


def select_domain_checks(roots: set[str], non_upstream: set[str], records: AuditRecords,
                         today: date, max_checks: int) -> list[str]:
    """Prioritize manually configured DIRECT roots over upstream DIRECT roots."""
    scheduled = {root for root in roots
                 if root in records and due(records[root], today)}
    unseen = roots - records.keys()
    return [
        *group
        for group in (
            sorted(scheduled & non_upstream),
            sorted(unseen & non_upstream),
            sorted(scheduled - non_upstream),
            sorted(unseen - non_upstream),
        )
    ][:max_checks]


def expiration(value: object) -> date | None:
    match value:
        case list() | tuple() as values:
            return max((day for item in values if (day := expiration(item))), default=None)
        case datetime() as value:
            return value.date()
        case date() as value:
            return value
        case str() as value:
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                try:
                    return date.fromisoformat(value[:10])
                except ValueError:
                    return None
        case _:
            return None


def load_bootstrap() -> dict[str, str]:
    raw = read_json_url(BOOTSTRAP, timeout=20)
    result = {
        **{tld.lower().lstrip("."): servers[0].rstrip("/") for tld in tlds}
        for tlds, servers in raw.get("services", [])
        if servers
    }
    if not result:
        raise RuntimeError("IANA RDAP bootstrap was empty")
    return result


def rdap_server(domain: str, bootstrap: dict[str, str]) -> str | None:
    labels = domain.split(".")
    return next(
        (bootstrap[suffix] for i in range(len(labels))
         if (suffix := ".".join(labels[i:])) in bootstrap),
        None,
    )


def rdap_lookup(domain: str, bootstrap: dict[str, str], timeout: int) -> LookupObservation:
    base = rdap_server(domain, bootstrap)
    if not base:
        return {"kind": "unknown", "source": "rdap-unavailable"}
    url = f"{base}/domain/{quote(domain, safe='.-')}"
    try:
        payload = read_json_url(url, timeout=timeout)
    except HTTPError as exc:
        # An authoritative registry RDAP 404 is meaningful, but still
        # requires a second observation on a later UTC day for deletion.
        if exc.code == 404:
            return {"kind": "not_found", "source": "rdap"}
        return {"kind": "unknown", "source": f"rdap-http-{exc.code}"}
    except (URLError, OSError, ValueError, TimeoutError) as exc:
        return {"kind": "unknown", "source": f"rdap-{type(exc).__name__}"}
    if not isinstance(payload, dict) or not payload.get("ldhName", payload.get("unicodeName")):
        return {"kind": "unknown", "source": "rdap-no-domain-object"}
    dates = [expiration(event.get("eventDate"))
             for event in payload.get("events", [])
             if str(event.get("eventAction", "")).lower() in EXPIRE_ACTIONS]
    expiry = max((d for d in dates if d), default=None)
    states = [str(state).lower().replace(" ", "") for state in payload.get("status", [])]
    grace = any("autorenew" in state or "grace" in state or "redemption" in state
                for state in states)
    return {"kind": "registered", "expiry": expiry, "grace": grace, "source": "rdap"}


def whois_lookup(domain: str, timeout: int) -> LookupObservation:
    """Best-effort fallback, never interpreting a network error as unregistered."""
    try:
        previous = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
            data = whois.whois(domain)
        finally:
            socket.setdefaulttimeout(previous)
        expiry = expiration(getattr(data, "expiration_date", None))
        if expiry:
            return {"kind": "registered", "expiry": expiry, "grace": False, "source": "whois"}
        if getattr(data, "domain_name", None):
            return {"kind": "registered", "expiry": None, "source": "whois"}
        return {"kind": "unknown", "source": "whois-no-expiry"}
    except Exception as exc:
        # Parser-specific "no match" exceptions can be treated as a
        # suspicion, never a one-shot removal.
        if NO_MATCH.search(str(exc)):
            return {"kind": "not_found", "source": "whois"}
        return {"kind": "unknown", "source": f"whois-{type(exc).__name__}"}


def lookup(domain: str, bootstrap: dict[str, str], timeout: int) -> LookupObservation:
    result = rdap_lookup(domain, bootstrap, timeout)
    # Prefer RDAP. WHOIS is necessary if RDAP is unavailable or lacks expiry.
    if result["kind"] == "unknown" or (result["kind"] == "registered" and not result.get("expiry")):
        fallback = whois_lookup(domain, timeout)
        if fallback["kind"] != "unknown":
            return fallback
    return result


# Exact UTC checkpoints: expiry date, +62 days, and +90 days.
CHECK_OFFSETS = (0, 62, 90)
RETRY_DAYS = frozendict(unknown=7)
MISSING_EXPIRY = sentinel("MISSING_EXPIRY")


def fixed_check_dates(expiry: date) -> tuple[str, str, str]:
    return tuple((expiry + timedelta(days=offset)).isoformat()
                 for offset in CHECK_OFFSETS)


def confirmed_expired(record: AuditRecord) -> bool:
    """Only three explicit expiry confirmations can authorize deletion."""
    if record.get("status") != "invalid" or "expires" not in record:
        return False
    targets = fixed_check_dates(date.fromisoformat(record["expires"]))
    return record.get("check_results") == dict.fromkeys(targets, "expired")


def due(record: AuditRecord | None, today: date) -> bool:
    if record is None:
        return True
    if record["status"] == "invalid":
        return False
    if expiry_text := record.get("expires"):
        checkpoint = today.isoformat()
        return (checkpoint in fixed_check_dates(date.fromisoformat(expiry_text))
                and checkpoint not in record["check_results"])
    return today >= date.fromisoformat(record["next_check"])


def update_record(old: AuditRecord | None, observation: LookupObservation,
                  today: date) -> AuditRecord:
    """Record only on-date expiry checks; never infer missing confirmations."""
    old = old or {}
    today_text = today.isoformat()
    observed_expiry = (observation.get("expiry")
                       if observation["kind"] == "registered" else None)
    previous_expiry = expiration(old.get("expires"))
    expiry = observed_expiry or previous_expiry
    record: AuditRecord = {
        "checked": today_text,
        "source": observation["source"],
        "status": "unknown",
    }

    if expiry is None:
        record["next_check"] = (today + timedelta(days=RETRY_DAYS["unknown"])).isoformat()
        return record

    # A changed expiry resets the *entire* fixed-date evidence sequence.
    results = ({} if observed_expiry is not None and observed_expiry != previous_expiry
               else dict(old.get("check_results", {})))
    checkpoint = today_text
    if checkpoint in fixed_check_dates(expiry) and checkpoint not in results:
        confirmed = (
            observation["kind"] == "registered"
            and observed_expiry == expiry
            and expiry <= today
            and observation.get("grace") is False
        )
        results[checkpoint] = "expired" if confirmed else "unconfirmed"

    record["expires"] = expiry.isoformat()
    record["check_results"] = results
    if (len(results) == len(CHECK_OFFSETS)
            and all(outcome == "expired" for outcome in results.values())):
        record["status"] = "invalid"
        record["reason"] = "expired"
    elif "expired" in results.values():
        record["status"] = "suspect"
    elif expiry > today and (observed_expiry is not None or old.get("status") == "active"):
        record["status"] = "active"
    return record


def remove_invalid(config: str, records: AuditRecords) -> tuple[str, int]:
    """Remove confirmed-invalid DIRECT rules only from [Rule], never PROXY/DROP."""
    bad = {root for root, item in records.items() if confirmed_expired(item)}
    result: list[str] = []
    removed = 0
    in_rules = False
    for line in config.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_rules = stripped == "[Rule]"
        domain = rule_domain(line) if in_rules else None
        if domain and domain in bad:
            removed += 1
        else:
            result.append(line)
    return "".join(result), removed



def domain_rule_counts(config: str) -> Counter[str]:
    """Count canonical domain rules in [Rule], ignoring ordering and comments."""
    counts: Counter[str] = Counter()
    in_rules = False
    for line in config.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_rules = stripped == "[Rule]"
            continue
        if not in_rules or not stripped or stripped.startswith(("#", ";")):
            continue
        fields = [field.strip() for field in stripped.split(",")]
        if len(fields) >= 3 and fields[0] in RULE_KINDS:
            counts[",".join(fields)] += 1
    return counts


def domain_rule_changes(before: str, after: str) -> tuple[list[str], list[str]]:
    """Net rule additions and removals; a changed action is both."""
    old = domain_rule_counts(before)
    new = domain_rule_counts(after)
    return sorted((new - old).elements()), sorted((old - new).elements())


def write_change_log(before: str, after: str, records: AuditRecords,
                     now: datetime | None = None) -> tuple[int, int]:
    """Overwrite one UTC-stamped log with both net ADD and DEL changes."""
    now = now or datetime.now(UTC)
    run_time = now.astimezone(UTC).isoformat(timespec="seconds")
    added, removed = domain_rule_changes(before, after)
    lines = [
        f"# UTC run: {run_time}",
        f"# ADD: {len(added)} domain rule(s)",
        f"# DEL: {len(removed)} domain rule(s)",
        "# Net changes to [Rule] since the start of this run.",
    ]
    lines.extend(f"ADD\t{rule}" for rule in added)
    for rule in removed:
        root = rule_domain(rule)
        record = records.get(root, {}) if root else {}
        reason = (f"registration_{record.get('reason', 'invalid')}"
                  if record.get("status") == "invalid" else "upstream")
        lines.append(f"DEL\t{rule}\t# {reason}")
    if not added and not removed:
        lines.append("# No changes.")
    CHANGES_LOG.parent.mkdir(parents=True, exist_ok=True)
    CHANGES_LOG.write_text("\n".join(lines) + "\n",
                           encoding="utf-8", newline="\n")
    return len(added), len(removed)


CACHE_VERSION = 1


def validate_cache_records(records: AuditRecords) -> None:
    """Validate the current fixed-date check records without legacy fields."""
    for domain, record in records.items():
        if not isinstance(record, dict) or record.get("status") not in {
                "active", "suspect", "unknown", "invalid"}:
            raise ValueError(f"Invalid cache record: {domain}")
        if not isinstance(record.get("checked"), str) or not isinstance(record.get("source"), str):
            raise ValueError(f"Missing cache observation metadata: {domain}")
        if expiry_text := record.get("expires"):
            try:
                expiry = date.fromisoformat(expiry_text)
                results = record["check_results"]
                targets = set(fixed_check_dates(expiry))
                if (not isinstance(results, dict)
                        or not set(results) <= targets
                        or any(value not in {"expired", "unconfirmed"}
                               for value in results.values())):
                    raise ValueError("Invalid fixed-check evidence")
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid fixed expiry checks: {domain}") from exc
            if record["status"] == "invalid" and not confirmed_expired(record):
                raise ValueError(f"Missing three expiry confirmations: {domain}")
        elif record["status"] == "invalid" or not isinstance(record.get("next_check"), str):
            raise ValueError(f"Missing retry date: {domain}")
        if "check_dates" in record or "checks_done" in record:
            raise ValueError(f"Obsolete randomized checks in cache: {domain}")


def validate_sync_result(before: str, after: str, records: AuditRecords) -> None:
    """Reject malformed output or unapproved edits before writing generated files."""
    validate_cache_records(records)
    sections = ("[General]", "[Rule]", "[Host]", "[MITM]")
    for config in (before, after):
        boundaries = [f"{section}\n" for section in sections]
        if (any(config.count(boundary) != 1 for boundary in boundaries)
                or [config.index(boundary) for boundary in boundaries]
                != sorted(config.index(boundary) for boundary in boundaries)):
            raise ValueError("Missing, repeated, or reordered configuration section")

    # Everything outside P6b must remain byte-for-byte identical, except
    # DIRECT rules whose registration root is confirmed invalid in the cache.
    _, _, before_base = base_configuration(before)
    _, _, after_base = base_configuration(after)
    expected_base, _ = remove_invalid(before_base, records)
    if compact_configuration(after_base) != compact_configuration(expected_base):
        raise ValueError("Unexpected changes outside the imported P6b section")
    if after != compact_configuration(after):
        raise ValueError("Configuration must contain only directives and import markers")

    # The generated block contains only sorted, unique DIRECT domain suffixes.
    # Its size is intentionally not fixed: upstream updates and audit removals
    # can legitimately add or remove entries on every run.
    def imported_domains(config: str) -> list[str]:
        block = config[config.index(START):config.index(END)]
        domains: list[str] = []
        for line in block.splitlines():
            if not line or line.startswith("#"):
                continue
            match line.split(","):
                case ["DOMAIN-SUFFIX", domain, "DIRECT"] if DOMAIN_RE.fullmatch(domain):
                    domains.append(domain)
                case _:
                    raise ValueError("Invalid or unexpected rule in the P6b section")
        if domains != sorted(set(domains)):
            raise ValueError("P6b rules must be sorted and unique")
        return domains

    original_domains = imported_domains(before)
    generated_domains = imported_domains(after)
    if original_domains and not generated_domains:
        raise ValueError("Refusing to erase a nonempty P6b domain import")


def load_cache() -> AuditRecords:
    if not CACHE.exists():
        return {}
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    if data.get("version") != CACHE_VERSION or not isinstance(data.get("domains"), dict):
        raise ValueError("Cache must use the current v1 format with fixed-date evidence")
    records = data["domains"]
    validate_cache_records(records)
    return records


def save_cache(records: AuditRecords) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps({"version": CACHE_VERSION, "domains": records},
                            ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    CACHE.write_text(serialized, encoding="utf-8", newline="\n")


def sync_upstream(config: str) -> tuple[str, str]:
    """Keep old config unchanged if upstream fetch fails; never import a partial list."""
    try:
        with urlopen(SOURCE_URL, timeout=60) as response:
            body = response.read()
        generated, stats = create_import(config, body)
        return generated, f"upstream synced; blob={stats['upstream_git_blob_sha']}"
    except (OSError, URLError, ValueError, UnicodeError) as exc:
        return config, f"upstream fetch/sync skipped: {str(exc)[:250]}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-checks", type=int, default=2000,
                        help="Max distinct registered roots per run (initial cache is batched)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()
    if args.max_checks < 1 or not 1 <= args.workers <= 8:
        parser.error("max-checks must be positive and workers between 1 and 8")

    today = utc_today()
    original_config = CONFIG.read_text(encoding="utf-8")
    config = original_config
    if args.no_sync:
        upstream_status = "upstream sync disabled"
    else:
        config, upstream_status = sync_upstream(config)
    print(upstream_status, flush=True)

    records = load_cache()
    roots, non_upstream = registration_roots(config)
    # Manually configured DIRECT roots cannot be starved by upstream DIRECT.
    pending = select_domain_checks(roots, non_upstream, records, today, args.max_checks)
    print(f"direct_registrable_roots={len(roots)} non_upstream_direct_roots={len(non_upstream)} "
          f"cached={len(roots & records.keys())} "
          f"scheduled_due={sum(root in records and due(records[root], today) for root in roots)} "
          f"new={len(roots - records.keys())} selected={len(pending)}", flush=True)

    if pending:
        try:
            bootstrap = load_bootstrap()
        except Exception as exc:
            print("IANA bootstrap unavailable; keeping existing domain rules:", exc, flush=True)
            bootstrap = None
        if bootstrap is not None:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(lookup, root, bootstrap, args.timeout): root for root in pending}
                for future in concurrent.futures.as_completed(futures):
                    root = futures[future]
                    try:
                        observation = future.result()
                    except Exception as exc:
                        observation = {"kind": "unknown", "source": type(exc).__name__}
                    records[root] = update_record(records.get(root), observation, today)

    final, removed = remove_invalid(config, records)
    final = compact_configuration(final)
    validate_sync_result(original_config, final, records)
    if final != original_config:
        CONFIG.write_text(final, encoding="utf-8")
    added_rules, removed_rules = write_change_log(original_config, final, records)
    save_cache(records)
    counts = {state: sum(v.get("status") == state for v in records.values())
              for state in ("active", "suspect", "invalid", "unknown")}
    print(f"added_rules={added_rules} removed_rules={removed_rules} invalid_rules_filtered={removed} cache={counts} remaining_unchecked="
          f"{sum(root not in records for root in roots)}", flush=True)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text("## Domain sync & registration audit\n\n"
                     f"- Date: {today}\n- {upstream_status}\n"
                     f"- Registrable DIRECT roots (all [Rule] groups): {len(roots)}\n"
                     f"- Non-upstream DIRECT roots: {len(non_upstream)}\n- Queried: "
                     f"{len(pending) if pending and bootstrap is not None else 0}\n"
                     f"- Rules added: {added_rules}\n"
                     f"- Rules removed: {removed_rules}\n"
                     f"- Change log: logs/changes.log (overwritten)\n"
                     f"- Cached states: {counts}\n"
                     f"- Not yet cached: {sum(root not in records for root in roots)}\n",
                     encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
