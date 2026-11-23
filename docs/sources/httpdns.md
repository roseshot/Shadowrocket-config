# HTTPDNS endpoint evidence

The profile uses `REJECT-DROP` for selected application HTTPDNS resolver addresses and hostnames associated with Alibaba Cloud, Tencent Cloud, Baidu, and Volcano Engine. The referenced official endpoints are not additional runtime subscriptions.

## Provider endpoints

| Provider | Hostnames or published endpoints | References |
| --- | --- | --- |
| Alibaba Cloud | `resolvers-cn.httpdns.aliyuncs.com`, `resolvers-hk.httpdns.aliyuncs.com`, `resolvers-sg.httpdns.aliyuncs.com`, `resolvers-us.httpdns.aliyuncs.com`, `resolvers-de.httpdns.aliyuncs.com`, `resolvers.httpdns.aliyuncs.com` | [Alibaba HTTPDNS](https://help.aliyun.com/zh/document_detail/2868011.html), [global bootstrap IPs](https://www.alibabacloud.com/help/en/httpdns/latest/httpdns-start-ip) |
| Tencent Cloud | `119.29.29.98`, `119.29.29.99`; historical backup examples `119.28.28.98`, `119.28.28.99` | [Enterprise HTTPDNS](https://cloud.tencent.com/document/product/379/95497), [failover examples](https://cloud.tencent.com/document/product/379/116336) |
| Baidu Cloud | `180.76.76.200`, `httpdns.baidubce.com` | [Baidu HTTPDNS specification](https://bce-cdn.bj.bcebos.com/p3m/pdf/bce-doc/online/HTTPDNS/HTTPDNS.pdf?timeStamp=1623110400100) |
| Volcano Engine | `httpdns.volcengineapi.com` | [Volcano HTTPDNS](https://docs.volcengine.com/docs/traffic-route-dns-suite/http-api-integration-solution-overview?lang=zh) |

## IPv4 range policy

Documented resolver IPs are expanded into `/24` blocking prefixes:

| Provider | IPv4 prefixes |
| --- | --- |
| Alibaba Cloud | `203.107.1.0/24`, `203.119.238.0/24`, `106.11.25.0/24`, `59.82.99.0/24`, `47.56.234.0/24`, `47.56.119.0/24`, `161.117.200.0/24`, `47.74.222.0/24`, `47.246.131.0/24`, `47.89.80.0/24`, `47.246.146.0/24` |
| Tencent Cloud | `119.29.29.0/24`, `119.28.28.0/24` |
| Baidu Cloud | `180.76.76.0/24` |

The Alibaba HTTPDNS IPv6 entries use exact `/128` matches rather than broad IPv6 prefixes. The profile also uses vendor-specific wildcard hostnames such as `httpdns*.baidubce.com` and `httpdns*.volcengineapi.com`.

**Important:** A `/24` blocks **256 IP addresses**, most of which may not be verified HTTPDNS servers. Backup addresses and SDK-selected endpoints can change. This inventory does not guarantee coverage of dynamically allocated resolvers or application traffic outside Shadowrocket.

Other public resolver evidence is documented in [Public DNS](dns.md). Validate current hostnames and ranges against the active [profile](../../shadowrocket.conf).
