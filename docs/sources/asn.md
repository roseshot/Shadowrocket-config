# ASN routing evidence

The profile uses static `IP-ASN` rules for selected provider-operated networks. The inventory below contains **59 ASNs** in 18 provider groups. These are origin-network classifications, not a geographic IP list or a dynamic subscription.

| Network | Origin ASNs | Evidence |
| --- | --- | --- |
| China Telecom / China Unicom / China Mobile / CERNET (existing) | 4134, 4837, 9808, 4812, 4808, 56040, 56041, 56046, 4538 | [Network directory](https://peer.as/networks/CN?lang=en) |
| China Telecom / CN2 / CTGNet | 4809, 23764, 63527 | [PeeringDB](https://www.peeringdb.com/asn/23764) |
| China Unicom / CUG | 9929, 10099, 132101 | [PeeringDB](https://www.peeringdb.com/org/10083) |
| China Mobile / CMI and overseas networks | 9231, 58453, 58807, 136750, 132389, 209141, 268862, 139619, 141419, 328787, 272151, 149967, 270215 | [PeeringDB](https://www.peeringdb.com/org/5459) |
| Alibaba Cloud / Taobao CDN | 37963, 45102, 24429, 134963 | [Provider inventory](https://www.iplocate.io/data/hosting-providers/alibabacloud) |
| Tencent Cloud / EdgeOne | 45090, 132203, 132591, 133478, 139341 | [PeeringDB](https://www.peeringdb.com/asn/139341) |
| Baidu | 38365, 55967 | [Network inventory](https://ip.network/company/baidu-ip-ranges-list) |
| UCloud | 59077, 135377, 139327 | [BGP.tools](https://bgp.tools/as/139327) |
| ByteDance / TikTok / Volcano Engine / BytePlus | 137718, 138699, 396986, 150436 | [PeeringDB](https://www.peeringdb.com/net/19428) |
| Huawei Cloud | 55990, 136907, 63727 | [PeeringDB](https://www.peeringdb.com/org/31897) |
| Kingsoft Cloud | 59019, 137280 | [BGP.tools](https://bgp.tools/as/137280) |
| QingCloud | 59078 | [APNIC RDAP](https://rdap.apnic.net/autnum/59078) |
| JD.com | 137753 | [Hurricane Electric](https://bgp.he.net/AS137753) |
| NetEase | 137263 | [PeeringDB](https://www.peeringdb.com/asn/137263) |
| Bilibili | 140633 | [PeeringDB](https://www.peeringdb.com/asn/140633) |
| iQIYI | 133865 | [PeeringDB](https://www.peeringdb.com/asn/133865) |
| Xiaomi | 63855, 63915 | [Netify](https://www.netify.ai/resources/networks/xiaomi) |
| Sina | 37936 | [BGP.tools](https://bgp.tools/as/37936) |

## Maintenance rules

- Confirm the current BGP origin and network operator through RDAP, PeeringDB, and independent route observations before changing a rule.
- Do not add customers, peers, transit providers, or every member of an AS-SET merely because they are associated with a selected provider.
- A shared ASN can also carry third-party customer traffic. Its use does not prove ownership of every destination.
- ASN routing applies regardless of the destination country's GeoIP classification. `DIRECT` can expose the originating connection address to overseas destinations.
- Explicit higher-priority `REJECT-DROP` and `PROXY` rules must remain intact.

Update the [main profile](../../shadowrocket.conf) and this evidence inventory together. Verify actual behavior on a device.
