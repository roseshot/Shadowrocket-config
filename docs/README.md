# Documentation

This directory describes the **current** configuration. The root [`shadowrocket.conf`](../shadowrocket.conf) is authoritative for active routing and response-rewrite rules.

## Operations

- [Domain synchronization and registration audit](domain-audit.md) — scheduled workflow, cache, safeguards, and local commands.
- [YouTube response rewriting](youtube-body-rewrite.md) — match scope, JSON filtering, verification, and troubleshooting.

## Rule-source evidence

| Area | Reference |
| --- | --- |
| Routing domains, China-specific cloud services, and AutoNavi | [Domain routing](sources/domain.md) |
| Corporate and application domains | [Enterprise domains](sources/enterprise-domains.md) |
| CDN providers and media delivery | [Global CDN](sources/global-cdn.md) |
| Origin network identification | [ASN](sources/asn.md) |
| Top-level domains and IDNs | [TLD](sources/tld.md) |
| Public DNS and encrypted DNS endpoints | [DNS](sources/dns.md) |
| Application HTTPDNS endpoints | [HTTPDNS](sources/httpdns.md) |
| HTTPS inspection exceptions | [MITM](sources/mitm.md) |
| Explicit application and SDK blocking | [Blocked domains](sources/drop-domains.md) |
| REDnote domain blocking | [REDnote domains](sources/xiaohongshu-domains.md) |
| YouTube/Google advertising hostnames | [YouTube ads](sources/youtube-ads.md) |

Evidence links document how a rule was selected; they are **not** additional runtime subscriptions. Listings can become stale and do not establish domain ownership, routing behavior, or live device compatibility. Check the current profile before editing a rule.
