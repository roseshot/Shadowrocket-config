# CDN routing evidence

The profile routes selected provider-controlled CDN, edge, and media-delivery suffixes through `DIRECT`. These are static hostname classifications; customer-owned hostnames, CNAME chains, and the geographic location of an edge node cannot be inferred reliably from a suffix alone.

The active configuration groups CDN rules by service category: cloud infrastructure, dedicated CDN, carrier delivery, and media/video delivery. This inventory instead groups sample suffixes by provider to make evidence review practical.

## Provider inventory

| Provider | Relevant hostnames or suffixes | Evidence |
| --- | --- | --- |
| CDNetworks / QUANTIL (Wangsu) | `cdnetworks.com`, `cdnetworks.net`, `cdngc.net`, `gccdn.net`, `cdnga.net`, `panthercdn.com`, `wcdnga.com`, `qtlcdn.com`, `qtlgslb.com`, `quantil.com`, `mwcloudcdn.com`, `mwcname.com`, `ourwebpic.com` | [CDNetworks](https://www.cdnetworks.com/news/cdnetworks-expands-network-capacity-4x-creates-global-cdn-giant/), [edge hostname docs](https://docs.cdnetworks.com/en/cdn/docs/portal/traffic-management/creating-edge-hostname), [QUANTIL API](https://docs.quantil.com/en/cdn/apidocs) |
| EdgeNext / ChinaCache international assets | `edgenext.com`, `glsb.cn` | [EdgeNext CDN](https://www.edgenext.com/docs/cdn/product-introduction/product-overview), [asset acquisition](https://www.datacenterdynamics.com/en/news/edgenext-acquires-chinacaches-international-cdn-operations/) |
| Alibaba Cloud CDN | `cdngslb.com`, `tbcache.com`, `kunlunca.com`, `kunluncan.com`, `kunlunar.com`, `alikunlun.net` | [Alibaba CDN](https://help.aliyun.com/zh/cdn/product-overview/terms), [CNAME setup](https://help.aliyun.com/zh/cdn/add-a-cname-record-for-a-domain-name), [CDN fingerprint](https://www.netify.ai/resources/domains/cdngslb.com) |
| Tencent Cloud / EdgeOne | `dnsv1.com`, `eo.dnse0.com`, `eo.dnse1.com`, `eo.dnse2.com`, `eo.dnse3.com`, `eo.dnse5.com`, `acc.edgeonedy1.com`, `acc.tyxcdn.com`, `tencent-cloud.net`, `tc.cdntip.com`, `spcdntip.com` | [Tencent CDN](https://cloud.tencent.com/document/product/228/43477), [EdgeOne](https://cloud.tencent.com/document/product/1552/70202) |
| Huawei Cloud CDN | `cdnhwc1.com`, `cdnhwc2.com`, `cdnhwc3.com`, `cdnhwcggk22.com` | [Huawei CDN CNAME](https://support.huaweicloud.com/cdn_faq/cdn_faq_0111.html) |
| Kingsoft Cloud | `ks-cdn.com`, `ks-cdn1.com`, `ksyuncdn.com` | [Kingsoft CDN](https://docs.ksyun.com/documents/40049) |
| Baidu Cloud | `bdydns.com`, `jomodns.com` | [Baidu CDN](https://intl.cloud.baidu.com/zh/doc/CDN/s/Ujwvydwl1-intl) |
| Qiniu | `qiniudns.com`, `qiniucdn.com`, `qiniudn.com`, `qnydns.com`, `qnssl.com`, `qbox.me`, `clouddn.com`, `cloudvdn.com` | [Qiniu CDN](https://developer.qiniu.com/fusion/3825/noun-explanation-fusion) |
| UpYun | `aicdn.com`, `upyun.com`, `upaiyun.com` | [UpYun edge hosts](https://help.upyun.com/knowledge-base/live-basic-config/) |
| BaishanCloud | `qingcdn.com`, `bsgslb.cn`, `bsclink.cn`, `trpcdn.net`, `baishan.com`, `baishancloud.com` | [BaishanCloud API](https://portal.baishancloud.com/track/document/api/1/1139) |
| China Telecom / CTYun | `ctdns.cn`, `ctyun.cn` | [CTYun](https://www.ctyun.cn/document/10007729/10335854) |
| NetEase | `163jiasu.com` | [CDN inventory](https://www.70ol.com/jingyan/260.html) |
| Dnion | `dnion.com`, `fastcdn.com`, `ewcache.com`, `flxdns.com`, `tlgslb.com` | [ProjectDiscovery provider list](https://github.com/projectdiscovery/cdncheck/blob/main/cmd/generate-index/provider.yaml) |
| VeryCDN | `verycdn.net` | [Provider directory](https://www.70ol.com/jingyan/260.html) |

Provider documentation is stronger evidence than third-party fingerprint or historical DNS datasets. Recheck weakly supported suffixes before adding broader rules.

## ByteDance media delivery exceptions

Media/resource domains such as `bytecdn.com`, `byteimg.com`, `bytetos.com`, `douyincdn.com`, `tiktokcdn.com`, and `feishucdn.com` are handled separately from general ByteDance business-domain blocking. The exact `cdn.volcengineapi.com` exception must precede broader blocking of `volcengineapi.com`.

Sources: [Volcano Engine CDN](https://docs.volcengine.com/docs/information-delivery-network/add-cdn-domain-add-a-domain-name?lang=zh), [BytePlus CDN](https://docs.byteplus.com/en/docs/byteplus-cdn/docs-add-your-domain-name), [CDN API](https://docs.volcengine.com/docs/information-delivery-network/check-domain-check-if-the-domain-name-meets-cdn-requirements?lang=en), and [blocked-domain inventory](drop-domains.md).

## Boundaries

- Higher-priority security blocks and international `PROXY` exceptions still apply.
- Global AWS (`cloudfront.net`) and global Azure (`azureedge.net`) are not reclassified as `DIRECT` merely because they operate points of presence in China.
- A hostname matching a CDN suffix is not proof that every request is CDN traffic. `DIRECT` can expose the client's network address to a provider in any country.
