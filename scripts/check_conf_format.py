#!/usr/bin/env python3
"""Lightweight structural validation for the generated Shadowrocket profile.

This checks the profile's section layout and directive shapes; it is not a
full Shadowrocket parser or a substitute for testing on an actual device.
"""

import argparse
import ipaddress
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "shadowrocket.conf"
SECTIONS = ("[General]", "[Rule]", "[Host]", "[MITM]")
RULE_TYPES = frozenset({
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD", "DOMAIN-SET",
    "DOMAIN-KEYWORD", "DST-PORT", "IP-CIDR", "IP-CIDR6",
    "IP-ASN", "GEOIP", "FINAL",
})
ASSIGNMENT = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*\s*=\s*\S.*$")
DOMAIN_VALUE = re.compile(r"^[a-zA-Z0-9*_.-]+$")
MARKERS = ("# ── P6b:", "# ── P7:")


def validate_rule(line: str) -> str | None:
    fields = [field.strip() for field in line.split(",")]
    kind = fields[0]
    if kind not in RULE_TYPES:
        return f"unsupported rule type: {kind}"
    if kind == "FINAL":
        return None if len(fields) == 2 and fields[1] else "FINAL requires a policy"
    if len(fields) not in (3, 4) or not all(fields):
        return "rule requires type,target,policy[,option]"
    _, target, policy, *options = fields
    if not policy:
        return "missing rule policy"
    if options and (kind not in {"IP-CIDR", "IP-CIDR6"} or
                    options != ["no-resolve"]):
        return "unexpected rule option"
    if kind in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD",
                "DOMAIN-KEYWORD"} and not DOMAIN_VALUE.fullmatch(target):
        return "invalid domain target"
    if kind == "DOMAIN-SET" and not target.startswith(("https://", "http://")):
        return "invalid remote DOMAIN-SET URL"
    if kind in {"IP-CIDR", "IP-CIDR6"}:
        try:
            network = ipaddress.ip_network(target, strict=False)
        except ValueError:
            return "invalid IP network"
        if network.version != (4 if kind == "IP-CIDR" else 6):
            return "IP family does not match rule type"
    if kind == "IP-ASN" and (not target.isascii() or not target.isdecimal()
                             or int(target) <= 0):
        return "invalid IP-ASN number"
    if kind == "GEOIP" and not re.fullmatch(r"[A-Z]{2}", target):
        return "invalid GEOIP region"
    if kind == "DST-PORT":
        parts = target.split("-")
        if len(parts) not in (1, 2) or any(
            not part.isascii() or not part.isdecimal() or
            not 1 <= int(part) <= 65535 for part in parts
        ) or (len(parts) == 2 and int(parts[0]) > int(parts[1])):
            return "invalid port or port range"
    return None


def validate_profile(config: str) -> tuple[int, list[str]]:
    errors: list[str] = []
    found: list[str] = []
    section: str | None = None
    rule_count = 0
    final_rules = 0
    last_rule = ""
    marker_sections: dict[str, list[str | None]] = {key: [] for key in MARKERS}
    marker_lines: dict[str, list[int]] = {key: [] for key in MARKERS}

    for line_number, line in enumerate(config.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", ";")):
            for marker in MARKERS:
                if stripped.startswith(marker):
                    marker_sections[marker].append(section)
                    marker_lines[marker].append(line_number)
            continue
        if stripped.startswith("[") or stripped.endswith("]"):
            if stripped not in SECTIONS or stripped != line:
                errors.append(f"line {line_number}: unexpected section header")
                continue
            if stripped in found:
                errors.append(f"line {line_number}: duplicate section {stripped}")
            found.append(stripped)
            section = stripped
            continue
        if section is None:
            errors.append(f"line {line_number}: directive before first section")
        elif section == "[Rule]":
            rule_count += 1
            last_rule = line.split(",", 1)[0]
            error = validate_rule(line)
            if error:
                errors.append(f"line {line_number}: {error}")
            if line.startswith("FINAL,"):
                final_rules += 1
        elif section in {"[General]", "[Host]", "[MITM]"}:
            if not ASSIGNMENT.fullmatch(line):
                errors.append(f"line {line_number}: malformed assignment in {section}")

    if found != list(SECTIONS):
        errors.append(f"expected sections in order: {', '.join(SECTIONS)}")
    if not rule_count:
        errors.append("no [Rule] directives")
    if final_rules != 1 or last_rule != "FINAL":
        errors.append("[Rule] must end with exactly one FINAL policy")
    for marker in MARKERS:
        if len(marker_sections[marker]) != 1 or marker_sections[marker][0] != "[Rule]":
            errors.append(f"expected one {marker} boundary within [Rule]")
    if (all(len(marker_lines[marker]) == 1 for marker in MARKERS)
            and marker_lines[MARKERS[0]][0] >= marker_lines[MARKERS[1]][0]):
        errors.append("P6b boundary must precede P7")
    return rule_count, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        content = args.path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"conf_format=FAIL unable to read {args.path}: {exc}", file=sys.stderr)
        return 1
    rules, errors = validate_profile(content)
    if errors:
        for error in errors[:20]:
            print(f"conf_format=FAIL {error}", file=sys.stderr)
        if len(errors) > 20:
            print(f"... {len(errors) - 20} additional error(s)", file=sys.stderr)
        return 1
    print(f"conf_format=OK sections={len(SECTIONS)} rules={rules} file={args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
