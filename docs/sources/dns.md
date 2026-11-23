# Public DNS blocking evidence

Selected public DNS, DoH, and DoT endpoints are blocked by static `REJECT-DROP` rules. This inventory documents the endpoint evidence; actual resolver selection is defined in the profile's `[General]` section.

| Provider | Known resolver hosts or IPs | Sources |
| --- | --- | --- |
| Alibaba Cloud AliDNS | `223.5.5.5`, `223.6.6.6`, `2400:3200::1`, `2400:3200:baba::1`, `dns.alidns.com` | [Alibaba Cloud](https://help.aliyun.com/zh/dns/free-service-disclaimer), [AdGuard](https://adguard-dns.io/kb/general/dns-providers/) |
| Tencent DNSPod | `119.29.29.29`, `1.12.12.12`, `120.53.53.53`, `doh.pub`, `dot.pub`, `dns.pub` | [Tencent Cloud](https://cloud.tencent.com/document/product/302/110786), [DNSPod notice](https://docs.dnspod.cn/notices/mian-fei-ban-dot-dohbu-zai-gong-kai-ipjie-ru-de-gong-gao/) |
| 360 Safe DNS | `101.226.4.6`, `218.30.118.6`, `123.125.81.6`, `140.207.198.6`, `101.198.198.198`, `101.198.199.200` | [360 Safe DNS](https://sdns.360.net/dnsPublic.html) |
| 114DNS | `114.114.114.114`, `114.114.115.115` | [114DNS](https://www.114dns.com/faq.html) |
| ByteDance public DNS | `180.184.1.1`, `180.184.2.2` | [AdGuard](https://adguard-dns.io/kb/general/dns-providers/) |
| OneDNS | `onedns.net`; documented public and family resolver endpoints | [OneDNS](https://www.onedns.net/), [AdGuard](https://adguard-dns.io/kb/general/dns-providers/) |

## Selected blocked ranges

| Provider | IPv4 CIDR prefixes |
| --- | --- |
| Alibaba Cloud | `223.5.5.0/24`, `223.6.6.0/24` |
| DNSPod | `1.12.12.0/24`, `120.53.53.0/24` |
| 360 Safe DNS | `101.226.4.0/24`, `218.30.118.0/24`, `123.125.81.0/24`, `140.207.198.0/24`, `101.198.198.0/24`, `101.198.199.0/24` |
| 114DNS | `114.114.114.0/24`, `114.114.115.0/24` |
| ByteDance | `180.184.1.0/24`, `180.184.2.0/24` |
| OneDNS | `117.50.10.0/24`, `52.80.52.0/24`, `117.50.22.0/24`, `52.80.66.0/24`, `117.50.60.0/24`, `52.80.60.0/24`, `117.50.11.0/24` |

Additional exact IPv6 endpoints include `2400:3200::1`, `2400:3200:baba::1`, `2402:4e00::`, `2402:4e00:1::`, `2400:7fc0:849e:200::8`, `2404:c2c0:85d8:901::8`, `2400:7fc0:849e:200::4`, and `2404:c2c0:85d8:901::4`.

Selected hostname suffixes include `doh.pub`, `dot.pub`, `dns.pub`, `dns.alidns.com`, `doh.360.cn`, `dot.360.cn`, and `onedns.net`. A blocked suffix can affect non-resolver services on the same domain.

## Scope and risks

IPv4 `/24` rules block **all 256 addresses** in each prefix, including addresses not independently confirmed to be resolvers. Resolver endpoints change; this list does not guarantee prevention of DNS leaks, application-specific HTTPDNS, or traffic outside Shadowrocket.

For application-specific resolvers, see [HTTPDNS](httpdns.md). Verify built-in DNS routing against the current profile and real device logs rather than relying on historical configuration choices.
