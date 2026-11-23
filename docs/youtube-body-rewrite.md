# YouTube JSON response rewriting

The profile uses Shadowrocket's native `[Body Rewrite]` `http-response-jq` directive to remove known advertising fields from supported YouTube Innertube **JSON responses**. The active regular expression and jq program are maintained exclusively in [`shadowrocket.conf`](../shadowrocket.conf); this document does not duplicate them.

## Scope

The URL matcher covers selected `/youtubei/v1/` endpoints (`player`, `player/ad_break`, `get_watch`, `next`, `browse`, `search`, `resolve_url`, and `reel/reel_watch_sequence`) on YouTube-owned API hosts. It does not match general `googlevideo.com` video streams or arbitrary YouTube web pages.

The jq expression recursively removes `adPlacements`, `adSlots`, `playerAds`, and `adBreakHeartbeatParams`. It also removes array entries with explicit ad-renderer markers and marked Shorts ads. Other JSON data, including `streamingData`, `videoDetails`, and captions, is preserved.

## Device verification

- Enable configuration mode and HTTPS inspection for the relevant YouTube hosts.
- Install and explicitly trust the Shadowrocket local CA on the device.
- Verify playback and the targeted YouTube API responses on the device. The lightweight configuration format checker verifies directive shape only; it does not execute or validate the jq program.

## Limitations and recovery

The rule only operates on traffic that Shadowrocket can decrypt and parse as JSON. Certificate pinning, protobuf/binary responses, new API structures, and embedded video advertising can bypass it. A configuration format check is **not** proof of ad removal in every iOS YouTube version.

If playback or recommendations break, disable the single `http-response-jq` rule and retest. Do not block `youtubei.googleapis.com` or `googlevideo.com` wholesale to compensate.

Reference implementations: [uBlock Origin filters](https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters.txt), [Quick Fixes](https://github.com/uBlockOrigin/uAssets/blob/master/filters/quick-fixes.txt), [Shadowrocket configuration examples](https://github.com/LOWERTOP/Shadowrocket/wiki). See [YouTube advertising sources](sources/youtube-ads.md) for hostname blocking.
