# HTTPS inspection exceptions

The profile enables Shadowrocket HTTPS inspection for selected traffic while excluding service domains where interception is unnecessary or likely to break authentication and system services. The authoritative exclusions are in [`[MITM]`](../../shadowrocket.conf).

## Apple service exclusions

Apple documents SSL inspection limitations and required hostnames in [Apple products on enterprise networks](https://support.apple.com/en-us/101555). The profile excludes both roots and subdomains for service families including:

- `-apple.com` and `-*.apple.com`
- `-apple.com.cn` and `-*.apple.com.cn`
- `-apple.cn` and `-*.apple.cn`
- `-apple` and `-*.apple`
- `-icloud.com` and `-*.icloud.com`
- `-icloud.com.cn` and `-*.icloud.com.cn`
- `-icloud-content.com` and `-*.icloud-content.com`
- `-cdn-apple.com` and `-*.cdn-apple.com`
- `-aaplimg.com` and `-*.aaplimg.com`
- `-mzstatic.com` and `-*.mzstatic.com`
- `-apple-dns.net` and `-*.apple-dns.net`
- `-apple-cloudkit.com` and `-*.apple-cloudkit.com`
- `-apple-livephotoskit.com` and `-*.apple-livephotoskit.com`
- `-apzones.com` and `-*.apzones.com`
- `-itunes.com` and `-*.itunes.com`
- `-me.com` and `-*.me.com`
- `-mac.com` and `-*.mac.com`
- `-mobileme.com` and `-*.mobileme.com`
- `-apple.news` and `-*.apple.news`
- `-apple-mapkit.com` and `-*.apple-mapkit.com`
- `-applecare.com` and `-*.applecare.com`
- `-appleid.com` and `-*.appleid.com`
- `-appstore.com` and `-*.appstore.com`
- `-appleschoolcontent.com` and `-*.appleschoolcontent.com`
- `-axm-usercontent-apple.com` and `-*.axm-usercontent-apple.com`

Exact third-party edge-host exclusions include `apple-relay.cloudflare.com`, `apple-relay.fastly-edge.com`, `cp4.cloudflare.com`, and `appldnld.apple.com.edgesuite.net`. Shared CDN parent domains are not globally excluded.

## OpenAI and ChatGPT exclusions

The profile excludes the root and subdomains of `openai.com`, `chatgpt.com`, `oaistatic.com`, `oaiusercontent.com`, and `oaistatsig.com`, plus the exact hostname `cdn.openaimerge.com`. It routes the corresponding services through explicit `PROXY` rules.

Reference: [OpenAI network recommendations](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps).

Do not exclude entire shared third-party infrastructure domains (for example, all Cloudflare, Stripe, or WorkOS hosts) without a service-specific reason.

## Risks

- HTTPS inspection requires local CA trust and can fail on certificate-pinned applications. It may expose sensitive content to software on the device.
- A wildcard hostname rule cannot guarantee decryption of every app or transport.
- MITM exclusions and routing policy are **independent**: excluding TLS inspection does not imply `DIRECT`.
- YouTube JSON filtering requires supported, decrypted JSON; see [Response rewriting](../youtube-body-rewrite.md).
