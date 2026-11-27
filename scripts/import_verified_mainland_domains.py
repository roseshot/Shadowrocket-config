#!/usr/bin/env python3
"""Import explicitly reviewed mainland-enterprise domain evidence, fail closed."""
import argparse
import ipaddress
import json
import re
from collections import Counter
from datetime import date
from fnmatch import fnmatchcase
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from check_conf_format import validate_profile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket.conf"
REGISTRY = ROOT / "data/mainland-company-domains.json"
PROTECTED = {"REJECT-DROP", "REJECT", "PROXY"}
LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
ICP = re.compile(r"[\u4e00-\u9fff]ICP(?:备|证)[0-9]{5,}(?:号)?(?:-[0-9]+)?(?:号)?", re.I)

def normalized(value):
    if not isinstance(value, str):
        raise ValueError("Expected a hostname")
    name = value.strip().rstrip(".").lower().encode("idna").decode("ascii")
    if len(name) > 253 or "." not in name or not all(
        LABEL.fullmatch(part) for part in name.split(".")
    ) or name.split(".")[-1].isdigit():
        raise ValueError(f"Invalid hostname: {value}")
    try:
        ipaddress.ip_address(name)
    except ValueError:
        return name
    raise ValueError("IP addresses not accepted")

def secure_url(value):
    if not isinstance(value, str):
        return False
    u = urlsplit(value)
    return u.scheme == "https" and bool(u.hostname) and not u.username and not u.password

def reviewed(registry):
    if registry.get("schema_version") != 1:
        raise ValueError("Unknown registry schema")
    companies = {c["name"]: c for c in registry["companies"]}
    if len(companies) != len(registry["companies"]):
        raise ValueError("Duplicate company")
    domains = set()
    for row in registry["approved_domains"]:
        name = normalized(row["domain"])
        company = companies.get(row["company"])
        if not company or company.get("status") != "approved":
            raise ValueError(f"Unapproved company: {name}")
        if row.get("operator") != company["name"]:
            raise ValueError(f"Operator mismatch: {name}")
        if company.get("registration_region") != "CN-mainland" or company.get("control_region") != "CN-mainland":
            raise ValueError(f"Company ownership not approved: {name}")
        if row.get("icp_status") != "active" or not ICP.fullmatch(row.get("icp_number", "")):
            raise ValueError(f"Missing active ICP evidence: {name}")
        for evidence in (company.get("registration_evidence"), company.get("control_evidence"), row.get("icp_evidence")):
            if not secure_url(evidence):
                raise ValueError(f"Missing evidence URL: {name}")
        for record in (company, row):
            if not isinstance(record.get("reviewer"), str) or not record["reviewer"].strip():
                raise ValueError(f"Missing reviewer: {name}")
            age = (date.today() - date.fromisoformat(record["reviewed_on"])).days
            if not 0 <= age <= 90:
                raise ValueError(f"Review not current: {name}")
        if name in domains:
            raise ValueError(f"Duplicate reviewed hostname: {name}")
        domains.add(name)
    return domains

def remote_domains(url):
    if not secure_url(url):
        raise ValueError("Unsupported protected remote list")
    req = Request(url, headers={"User-Agent": "ShadowrocketConfigReview/1.0"})
    with urlopen(req, timeout=60) as response:
        if urlsplit(response.geturl()).hostname != urlsplit(url).hostname:
            raise ValueError("Unexpected remote-list redirect")
        raw = response.read(20_000_001)
    if len(raw) > 20_000_000:
        raise ValueError("Remote list too large")
    domains = set()
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        domains.add(normalized(line.removeprefix("*.").removeprefix(".")))
    if not domains:
        raise ValueError("Empty protected remote list")
    return domains

def merge(before, candidates):
    _, errors = validate_profile(before)
    if errors:
        raise ValueError(f"Existing profile invalid: {errors[:5]}")
    if not candidates:
        return before, Counter()
    lines = before.splitlines(keepends=True)
    index = next(i for i, line in enumerate(lines) if line.startswith("# ── P6b:"))
    if not lines[index + 1].startswith("# ── P7:"):
        raise ValueError("Retired upstream block must remain empty")
    rules = []
    remote = set()
    in_rules = False
    for line in lines:
        line = line.strip()
        if line == "[Rule]":
            in_rules = True
            continue
        if line.startswith("["):
            in_rules = False
        if not in_rules or line.startswith("#"):
            continue
        fields = line.split(",")
        if len(fields) < 3:
            continue
        kind, target, policy = fields[:3]
        if kind == "DOMAIN-SET" and policy in PROTECTED:
            remote.update(remote_domains(target))
        elif kind in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD"}:
            rules.append((kind, target.lower(), policy))
    def match(name, kind, target):
        if kind == "DOMAIN":
            return name == target
        if kind == "DOMAIN-SUFFIX":
            return name == target or name.endswith("." + target)
        if kind == "DOMAIN-KEYWORD":
            return target in name
        return fnmatchcase(name, target)
    counts = Counter()
    added = []
    for name in sorted(candidates):
        parts = name.split(".")
        matches = {policy for kind, target, policy in rules if match(name, kind, target)}
        if matches & PROTECTED or any(".".join(parts[i:]) in remote for i in range(len(parts))):
            counts["protected"] += 1
        elif "DIRECT" in matches:
            counts["already_covered"] += 1
        else:
            # Exact host only; approval of one host does not approve all subdomains.
            added.append(f"DOMAIN,{name},DIRECT\n")
            counts["added"] += 1
    after = "".join(lines[:index] + added + lines[index:])
    _, errors = validate_profile(after)
    if errors:
        raise ValueError(f"Generated profile invalid: {errors[:5]}")
    return after, counts

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    candidates = reviewed(registry)
    before = CONFIG.read_text(encoding="utf-8")
    after, counts = merge(before, candidates)
    print(f"companies={len(registry['companies'])} approved_hosts={len(candidates)} results={dict(counts)}")
    if args.write and before != after:
        CONFIG.write_text(after, encoding="utf-8", newline="\n")

if __name__ == "__main__":
    main()
