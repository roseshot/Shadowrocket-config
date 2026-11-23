# REDnote / Xiaohongshu domain blocking

The profile contains **44** domain-suffix blocks and **one** exact-host block for REDnote-related services. All use `REJECT-DROP`. This is intentional application-wide blocking; it is not a selective advertising filter.

## Evidence

- **First-party:** [Xiaohongshu terms](https://agree.xiaohongshu.com/h5/terms/ZXXY20220316001/-1), [first-party CDN-hosted document](https://dc.xhscdn.com/30306e29e9a06fd681ce9d9d04188a342fbe211e.pdf).
- **Independent network/product observations:** [Netify REDnote](https://www.netify.ai/resources/applications/rednote), [browser adapter](https://opencli.info/docs/adapters/browser/rednote.html).
- **Historical registration and community reports:** [registration record](https://www.51miit.com/details/539e92bbe4324ef3ba239b613aa199d8/), [Control D discussion](https://docs.controld.com/discuss/678b52149f7acd002add0202), [V2EX network observation](https://www.v2ex.com/t/1151745).

Historical registrations and community observations are weaker evidence and may be stale.

## P1b blocked domain inventory

| Category | Blocked `DOMAIN-SUFFIX` roots | Count |
| --- | --- | ---: |
| Core REDnote services | `xiaohongshu.com`, `xiaohongshu.cn`, `xiaohongshu.net`, `xiaohongshu.net.cn`, `xingin.cn`, `xingin.net`, `xn--1jqv64ax40a.com`, `rednote.com` | 8 |
| Media, CDN, and supporting services | `xhscdn.com`, `xhscdn.net`, `xhscdn.cn`, `xhsredcdn.com`, `xhsrcdn.com`, `rednotecdn.com`, `cdnxhs.com`, `xhsdns.com`, `xhsdns.net`, `xhsos.com`, `xhssys.cn`, `xhssys.com`, `xhssys.net` | 13 |
| Links and sharing | `xhslink.cn`, `xhslink.com`, `xhsurl.cn`, `xhsurl.com`, `rl.ink`, `redselect.cn`, `redselect.com.cn` | 7 |
| Historical brand and business registrations | `redelight.biz`, `redelight.cn`, `redelight.com.cn`, `redelight.info`, `redelight.net`, `yuukoo.biz`, `yuukoo.com.cn`, `yuukoo.info`, `yuukoo.net`, `yuukoo.red`, `iselect.red`, `aboutmgzn.com`, `batman.plus`, `xingludalogistics.com`, `hongyunlogistics.com` | 15 |
| Community-reported | `redbascket.com` | 1 |

Additional exact-match rule: `DOMAIN,xhslive-video.xhscnd.com,REJECT-DROP`. This is a single-host block; the shared parent `xhscnd.com` is not blocked wholesale.

## Operational impact

Domain suffixes cover each root and all its subdomains. Login, media delivery, APIs, and short links may fail. The listed domains take precedence over general `DIRECT` handling; they do **not** imply that shared Alibaba, Tencent, Cloudflare, or Akamai domains should also be blocked.

Unlisted domains, direct-IP traffic, and DNS aliases may behave differently. Verify actual outcomes through connection logs.
