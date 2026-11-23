# TLD routing evidence

The profile has **45** explicit `DIRECT` TLD rules: 12 ASCII/brand TLDs, 27 IDN TLDs, four Hong Kong/Macao entries, and two separately selected Public Interest Registry (PIR) IDN exceptions.

Sources: [IANA Root Zone Database](https://www.iana.org/domains/root/db), [China domain registration framework](https://domain.miit.gov.cn/chinayu.jsp), and [CNNIC](https://www2.cnnic.cn/n4/2022/0722/c77-247.html). TLD registry jurisdiction is not evidence of the location or owner of an individual hosted service.

## ASCII and brand TLDs

| TLD | Registry or operator |
| --- | --- |
| `.cn` | China Internet Network Information Center |
| `.alibaba` | Alibaba Group Holding Limited |
| `.alipay` | Alibaba Group Holding Limited |
| `.taobao` | Alibaba Group Holding Limited |
| `.baidu` | Baidu, Inc. |
| `.sohu` | Sohu.com Limited |
| `.citic` | CITIC Group Corporation |
| `.ren` | ZDNS International Limited |
| `.wang` | Zodiac Wang Limited |
| `.top` | Hong Kong Zhongze International Limited |
| `.xin` | Elegant Leader Limited |
| `.xihuan` | Beijing Qihu Keji Co., Ltd. |

## Internationalized TLDs (ASCII/Punycode)

Use Punycode in hostname-matching rules instead of localized Unicode labels.

| Punycode TLD | Registry or operator |
| --- | --- |
| `.xn--fiqs8s` | CNNIC |
| `.xn--fiqz9s` | CNNIC |
| `.xn--55qx5d` | CNNIC |
| `.xn--io0a7i` | CNNIC |
| `.xn--zfr164b` | China Organizational Name Administration Center |
| `.xn--55qw42g` | China Organizational Name Administration Center |
| `.xn--ses554g` | KNET Co., Ltd |
| `.xn--fiq64b` | CITIC Group Corporation |
| `.xn--xhq521b` | Guangzhou YU Wei Information Technology |
| `.xn--1qqw23a` | Guangzhou YU Wei Information Technology |
| `.xn--vuq861b` | Beijing Tele-info Technology |
| `.xn--kput3i` | Beijing RITT-Net Technology Development |
| `.xn--3ds443g` | Beijing TLD Registry Technology |
| `.xn--fiq228c5hs` | Beijing TLD Registry Technology |
| `.xn--g2xx48c` | Nawang Heli(Xiamen) Network Service |
| `.xn--otu796d` | Jiang Yu Liang Cai Technology |
| `.xn--9krt00a` | Sina Corporation |
| `.xn--8y0a063a` | China Unicom |
| `.xn--czr694b` | Internet DotTrademark Organisation |
| `.xn--czru2d` | Zodiac Aquarius Limited |
| `.xn--hxt814e` | Zodiac Taurus Ltd. |
| `.xn--3bst00m` | Eagle Horizon Limited |
| `.xn--9et52u` | RISE VICTORY LIMITED |
| `.xn--6qq986b3xl` | Tycoon Treasure Limited |
| `.xn--rhqv96g` | Stable Tone Limited |
| `.xn--nyqy26a` | Stable Tone Limited |
| `.xn--imr513n` | Internet DotTrademark Organisation |

## Hong Kong and Macao

| TLD | Registry / region |
| --- | --- |
| `.hk` | Hong Kong |
| `.mo` | Macao |
| `.xn--j6w193g` | Hong Kong IDN |
| `.xn--mix891f` | Macao IDN |

## Explicit PIR exceptions

The following two IDN TLDs are included by routing preference even though they are administered by PIR rather than CNNIC:

- `.xn--nqv7f` — [IANA registry](https://www.iana.org/domains/root/db/xn--nqv7f.html)
- `.xn--nqv7fs00ema` — [IANA registry](https://www.iana.org/domains/root/db/xn--nqv7fs00ema.html)

These exceptions do not imply a general `.org` `DIRECT` rule. Neither `.com` nor other global TLDs are classified as domestic merely because a registry accepts registrations in China.

High-priority `REJECT-DROP` rules (including `gov.cn`), explicit `PROXY` exceptions, and encrypted-DNS blocks still apply before TLD-based routing.
