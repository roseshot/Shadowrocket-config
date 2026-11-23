# YouTube advertising-host evidence

The profile blocks **18** static advertising domain suffixes and **one** wildcard domain with `REJECT-DROP`. This list targets hostnames commonly associated with YouTube and Google advertising infrastructure; it is not a guarantee of ad-free video playback.

## Blocked hostnames

- `ads.youtube.com`
- `ad.youtube.com`
- `doubleclick.net`
- `doubleclick.com`
- `googlesyndication.com`
- `googletagservices.com`
- `googleadservices.com`
- `googleads.com`
- `2mdn.net`
- `2mdnsys.com`
- `admob.com`
- `doubleclickads.net`
- `doubleclickbygoogle.com`
- `doubleclick-cn.net`
- `googleadservices-cn.com`
- `googlesyndication-cn.com`
- `googletagservices-cn.com`
- `googleadsserving.cn`
- `adservice.google.*`

The wildcard entry uses a `DOMAIN-WILDCARD` rule. The other entries use `DOMAIN-SUFFIX`, which covers each domain and its subdomains.

## Sources and limitations

- [Community DNS list](https://github.com/froggeric/DNS-blocklists/blob/main/NoYouTubeAdsDNS)
- [AdGuard: why YouTube ads are difficult to block with DNS](https://adguard.com/en/support/adguard-mini-android/about/about_the_settings/video_browser/youtube_hard_to_block.html)
- [uBlock Origin filters](https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters.txt)
- [uBlock Origin Quick Fixes](https://github.com/uBlockOrigin/uAssets/blob/master/filters/quick-fixes.txt)

Do not block all of `youtube.com`, `googlevideo.com`, `youtubei.googleapis.com`, or `ytimg.com`: normal video playback shares those services. Google Ads administration and unrelated sites can also be affected by broad advertising-host blocks.

DNS-level host blocking does not reliably remove advertisements embedded in YouTube video streams. Verify behavior on an actual device.
