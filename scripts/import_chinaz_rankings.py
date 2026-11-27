#!/usr/bin/env python3
"""One-off, append-only ChinaZ overall ranking import. Fail closed on incomplete crawl."""
import argparse
from collections import Counter
from fnmatch import fnmatchcase
from html.parser import HTMLParser
import ipaddress
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

BASE = "https://top.chinaz.com/all/"
AGENT = "ShadowrocketConfigChinaZImport/1.0"
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket.conf"
MARK = "# ── P6b:"
PROTECTED = {"REJECT-DROP", "REJECT", "PROXY"}
LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")

def domain(value):
    try:
        value = value.strip().rstrip(".").lower().encode("idna").decode("ascii")
    except UnicodeError:
        return None
    if len(value) > 253 or "." not in value or not all(
        LABEL.fullmatch(part) for part in value.split(".")
    ) or value.split(".")[-1].isdigit():
        return None
    try:
        ipaddress.ip_address(value)
        return None
    except ValueError:
        return value

def get(url):
    req = Request(url, headers={"User-Agent": AGENT, "Accept": "text/html,text/plain,*/*"})
    with urlopen(req, timeout=25) as response:
        if urlsplit(response.geturl()).hostname != urlsplit(url).hostname:
            raise RuntimeError("Unexpected redirect")
        data = response.read(20_000_001)
        if len(data) > 20_000_000:
            raise RuntimeError("Oversized response")
        return data.decode(response.headers.get_content_charset() or "utf-8")

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.heading = False
        self.span = False
        self.parts = []
        self.domains = []
        self.links = set()
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self.heading = True
        if tag == "span" and self.heading:
            self.span = True
            self.parts = []
        if tag == "a":
            href = dict(attrs).get("href", "")
            url = urlsplit(urljoin(BASE, href))
            match = re.fullmatch(r"/all/index_(\d+)\.html", url.path)
            if url.hostname == "top.chinaz.com" and match:
                self.links.add(int(match[1]))

    def handle_data(self, data):
        self.text.append(data)
        if self.span:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.span:
            value = domain("".join(self.parts))
            if value:
                self.domains.append(value)
            self.span = False
        if tag == "h3":
            self.heading = self.span = False

    @property
    def date(self):
        match = re.search(r"更新\s*[:：]\s*(\d{4}-\d{2}-\d{2})", "".join(self.text))
        if not match:
            raise RuntimeError("Ranking update date absent")
        return match[1]

def crawl():
    robots = RobotFileParser()
    robots.set_url("https://top.chinaz.com/robots.txt")
    try:
        robots.parse(get(robots.url).splitlines())
    except HTTPError as exc:
        if exc.code not in (404, 410):
            raise
        robots.parse([])
    delay = max(2, robots.crawl_delay(AGENT) or 0)
    next_request = 0.0
    def page(n):
        nonlocal next_request
        url = BASE + ("index.html" if n == 1 else f"index_{n}.html")
        if not robots.can_fetch(AGENT, url):
            raise RuntimeError(f"robots.txt disallows {url}")
        time.sleep(max(0, next_request - time.monotonic()))
        result = Page(get(url))
        next_request = time.monotonic() + delay
        return result
    first = page(1)
    total = max(first.links, default=0)
    if total < 2 or len(first.domains) != 30:
        raise RuntimeError("Could not establish full ranking pagination")
    stamp = first.date
    all_domains = set()
    fingerprints = set()
    entries = 0
    for n in range(1, total + 1):
        p = first if n == 1 else page(n)
        count = len(p.domains)
        if p.date != stamp or max(p.links, default=0) != total:
            raise RuntimeError(f"Ranking changed during crawl at page {n}; rerun")
        if not 1 <= count <= 30 or (n < total and count != 30):
            raise RuntimeError(f"Unexpected row count at page {n}: {count}")
        fingerprint = tuple(p.domains)
        if fingerprint in fingerprints:
            raise RuntimeError(f"Duplicate ranking page {n}")
        fingerprints.add(fingerprint)
        all_domains.update(p.domains)
        entries += count
        if n % 100 == 0 or n == total:
            print(f"pages={n}/{total} entries={entries} unique={len(all_domains)}", flush=True)
    print(f"snapshot={stamp} pages={total} entries={entries}", flush=True)
    return all_domains

def suffixes(d):
    parts = d.split(".")
    return (".".join(parts[i:]) for i in range(len(parts)))

def merge(before, candidates):
    rules = before.splitlines()
    if sum(x.startswith(MARK) for x in rules) != 1:
        raise RuntimeError("Expected exactly one P6b marker")
    index = next(i for i, x in enumerate(rules) if x.startswith(MARK))
    if not rules[index+1].startswith("# ── P7:"):
        raise RuntimeError("Old upstream block must remain empty")
    exact, suffix, wildcard, keyword = {}, {}, [], []
    remote = set()
    for line in rules:
        fields = line.split(",")
        if len(fields) < 3:
            continue
        kind, target, policy = fields[:3]
        target = target.lower() if kind != "DOMAIN-SET" else target
        if kind == "DOMAIN":
            exact.setdefault(target, policy)
        elif kind == "DOMAIN-SUFFIX":
            suffix.setdefault(target, policy)
        elif kind == "DOMAIN-WILDCARD":
            wildcard.append((target, policy))
        elif kind == "DOMAIN-KEYWORD":
            keyword.append((target, policy))
        elif kind == "DOMAIN-SET" and policy in PROTECTED:
            if urlsplit(target).scheme != "https":
                raise RuntimeError("Unsupported protected remote list URL")
            count = 0
            for raw in get(target).splitlines():
                raw = raw.strip()
                if not raw or raw.startswith(("#", "!")):
                    continue
                raw = raw.removeprefix("*.").removeprefix(".")
                value = domain(raw)
                if not value:
                    raise RuntimeError("Unrecognized protected remote list entry")
                remote.add(value)
                count += 1
            if not count:
                raise RuntimeError("Empty protected remote list")
    counts = Counter()
    accepted = set()
    for candidate in sorted(candidates, key=lambda d: (d.count("."), d)):
        parents = tuple(suffixes(candidate))
        matches = {exact.get(candidate)} | {suffix.get(p) for p in parents}
        matches.update(policy for pattern, policy in wildcard if fnmatchcase(candidate, pattern))
        matches.update(policy for pattern, policy in keyword if pattern in candidate)
        if matches & PROTECTED or remote.intersection(parents):
            counts["protected"] += 1
        elif "DIRECT" in matches or accepted.intersection(parents):
            counts["already_covered"] += 1
        else:
            accepted.add(candidate)
    counts["added"] = len(accepted)
    print(f"unique_candidates={len(candidates)} results={dict(counts)}", flush=True)
    # Only insert before the empty former import marker; never alter a prior rule.
    lines = before.splitlines(keepends=True)
    return "".join(lines[:index] + [f"DOMAIN-SUFFIX,{d},DIRECT\n" for d in sorted(accepted)] + lines[index:])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    before = CONFIG.read_text(encoding="utf-8")
    candidates = crawl()
    after = merge(before, candidates)
    from check_conf_format import validate_profile
    count, errors = validate_profile(after)
    if errors:
        raise RuntimeError(f"Invalid output: {errors[:10]}")
    print(f"validated_rules={count}", flush=True)
    if args.write:
        CONFIG.write_text(after, encoding="utf-8", newline="\n")

if __name__ == "__main__":
    main()
