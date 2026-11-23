# Static domain routing evidence

Static domain rules in the [profile](../../shadowrocket.conf) identify selected services for `DIRECT` or `PROXY` routing. These references are evidence for individual routing choices, **not** live domain lists.

## Service-specific domain families

| Service | Relevant suffixes or examples | Primary references |
| --- | --- | --- |
| Alibaba Cloud | `alicdn.com`, `tbcdn.cn`, `aliyuncs.com`, `alibabacloud.com` | [Alibaba Cloud network requirements](https://www.alibabacloud.com/help/en/management-console/configure-a-local-firewall-or-proxy-to-access-alibaba-cloud-services) |
| Tencent Cloud | `myqcloud.com`, `qcloud.com` and provider CDN endpoints | [Tencent Cloud COS](https://cloud.tencent.com/document/product/460/6937) |
| Azure global services | `azureedge.net`, `azurefd.net`, `msecnd.net`, `cloudapp.net` | [Microsoft domain inventory](https://learn.microsoft.com/en-us/azure/security/fundamentals/azure-domains) |
| Apple services | `icloud.com`, `cdn-apple.com`, `mzstatic.com`, `apple-dns.net` | [Apple enterprise networking](https://support.apple.com/en-us/101555) |
| Azure China | `chinacloudapi.cn`, `chinacloudapp.cn`, `azure.cn` | [Azure China](https://learn.microsoft.com/en-us/azure/china/concepts-service-availability) |
| AWS China | `amazonaws.com.cn`, `amazonaws.cn` | [AWS China endpoints](https://docs.amazonaws.cn/general/latest/gr/endpoints-Ningxia.html) |
| AutoNavi / Amap | `autonavi.com`, `amap.com`, `gaode.com`, `amapauto.com`, `opnavi.com` | [Amap developer portal](https://lbs.amap.com/), [Web Service API](https://lbs.amap.com/api/web-service/guide/autocomplete) |

Global AWS/Azure hostnames and international CDN services retain their separately defined `PROXY` handling. A China-specific service endpoint must not be used as evidence that the provider's entire global infrastructure should be `DIRECT`.

## AutoNavi routing details

The `autonavi.com` suffix includes hosts such as `shift.is.autonavi.com`, `direction2.is.autonavi.com`, and `mapdownload.autonavi.com`. The `opnavi.com` family includes `sg-restapi.opnavi.com`. The independent `autonav.com` marine-navigation brand is **not** AutoNavi.

References: [Amap service terms](https://lbs.amap.com/pages/terms), [AutoNavi network identification](https://www.netify.ai/resources/domains/autonavi.com), [Amap integration hostnames](https://docs.succbi.com/v5/devops/install/proxy-gaode), [AutoNav Marine](https://www.autonav.com/).

## Routing boundaries

- Shadowrocket matches requested hostnames; a customer's CNAME pointing at a CDN does not guarantee a matching provider-domain rule.
- Explicit blocks and international `PROXY` exceptions take precedence over the general `DIRECT` sections.
- Shared CDN infrastructure must not be classified solely by the company using it.
- Broad ASN and GeoIP fallbacks may produce different behavior from domain-name matching.

For inventories, see [enterprise domains](enterprise-domains.md), [global CDN](global-cdn.md), [TLDs](tld.md), [DNS](dns.md), and [HTTPDNS](httpdns.md).
