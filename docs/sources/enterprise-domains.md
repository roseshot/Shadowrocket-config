# Enterprise domain routing evidence

This inventory documents selected corporate and brand-domain suffixes used for `DIRECT` routing. It is **not** an ownership registry or an assertion that every service operated by a company is hosted in China. Explicit `REJECT-DROP` and international `PROXY` rules take priority; for example, REDnote domains are currently blocked and therefore excluded from this `DIRECT` inventory.

## Internet platforms and e-commerce

| Brand / organization | Relevant domain suffixes |
| --- | --- |
| Pinduoduo / Temu | `pinduoduo.com`, `yangkeduo.com`, `temu.com` |
| Meituan / Dianping | `meituan.com`, `meituan.net`, `dianping.com` |
| Kuaishou / Kwai | `kuaishou.com`, `kwai.com` |
| DiDi | `didiglobal.com` |
| Trip.com Group | `ctrip.com`, `trip.com`, `qunar.com` |
| Tencent Music | `kugou.com` |
| Beike / Lianjia | `ke.com`, `lianjia.com` |
| BOSS Zhipin | `zhipin.com`, `kanzhun.com` |
| Dewu | `dewu.com` |
| Mango TV | `mgtv.com` |
| Zhihu | `zhihu.com`, `zhimg.com` |
| Sogou | `sogou.com` |
| 58.com / Ganji | `58.com`, `ganji.com` |
| Vipshop | `vip.com` |
| Alibaba international / Ant Group | `aliexpress.com`, `lazada.com`, `fliggy.com`, `oceanbase.com`, `antgroup.com` |
| Sohu | `sohu.com` |
| 360 | `360.com`, `so.com` |
| CSDN | `csdn.net` |
| DeepSeek | `deepseek.com` |

## Banking and financial services

| Brand / organization | Relevant domain suffixes |
| --- | --- |
| ICBC | `icbc.com` |
| Agricultural Bank of China | `abchina.com` |
| China Construction Bank | `ccb.com` |
| Bank of Communications | `bankcomm.com` |
| Postal Savings Bank of China | `psbc.com` |
| China Merchants Bank | `cmbchina.com` |
| China CITIC Bank | `citicbank.com` |
| Ping An | `pingan.com` |
| UnionPay | `unionpay.com`, `unionpayintl.com` |
| WeBank | `webank.com` |

## Large state-owned enterprises

| Brand / organization | Relevant domain suffixes |
| --- | --- |
| China Aerospace Science and Technology Corporation | `spacechina.com` |
| COMAC | `comac.cc` |
| COSCO Shipping | `coscoshipping.com` |
| Sinopharm | `sinopharm.com` |
| COFCO | `cofco.com` |
| CITIC Group | `citic.com` |
| China Energy Investment | `ceic.com` |
| China Datang | `china-cdt.com` |
| Sinochem | `sinochem.com` |
| Sinopec Group | `sinopecgroup.com` |
| CSCEC | `cscec.com` |
| CNOOC | `cnoocltd.com` |
| Air China | `airchina.com` |
| China Eastern Airlines | `ceair.com` |
| China Southern Airlines | `csair.com` |

## Manufacturing, mobility, and gaming

| Brand / organization | Relevant domain suffixes |
| --- | --- |
| BYD | `byd.com`, `bydglobal.com` |
| Geely | `geely.com` |
| NIO | `nio.com` |
| XPeng | `xpeng.com` |
| Li Auto | `li.auto`, `lixiang.com` |
| Leapmotor | `leapmotor.com` |
| CATL | `catl.com` |
| Zeekr | `zeekrgroup.com`, `zeekrglobal.com` |
| GWM | `gwm-global.com` |
| Lenovo | `lenovo.com` |
| ZTE | `zte.com` |
| OPPO | `oppo.com` |
| vivo | `vivo.com` |
| realme | `realme.com` |
| OnePlus | `oneplus.com` |
| Honor | `honor.com` |
| Haier | `haier.com` |
| Hisense | `hisense.com` |
| TCL | `tcl.com` |
| Midea | `midea.com` |
| Gree | `gree.com` |
| DJI | `dji.com` |
| Anker | `anker.com` |
| Ecovacs | `ecovacs.com` |
| Roborock | `roborock.com` |
| miHoYo / HoYoverse | `mihoyo.com`, `hoyoverse.com`, `hoyolab.com` |

## Evidence and maintenance

Check operator websites, registry data, and DNS behavior before expanding a brand suffix. Source references include [China's state-owned enterprise directory](https://wap.sasac.gov.cn/n2588045/n27271785/n27271792/c14159097/content.html), [Trip.com Group brands](https://group.trip.com/brands?locale=en-US), [Kwai](https://www.kwai.com/aboutus), [COMAC](https://www.comac.cc/), [BYD](https://www.bydglobal.com/), [Lenovo](https://www.lenovo.com/us/en/about/), and [CATL](https://www.catl.com/).

Do not add shared global CDN suffixes such as `cloudfront.net`, `azureedge.net`, `cloudflare.net`, or `akamaized.net` merely because one customer belongs to a listed organization. The active profile defines the actual route decisions.
