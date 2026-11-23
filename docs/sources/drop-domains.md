# Blocked application and SDK domains

This document records **77** explicit `DOMAIN-SUFFIX,...,REJECT-DROP` entries from the application's high-priority block section. Suffix blocking affects whole domains and their subdomains, including legitimate application, login, content, cloud, and messaging services. These rules are not limited to advertising or tracking hosts.

## Rule inventory

```ini
# Umeng / CNZZ analytics (4)
DOMAIN-SUFFIX,umeng.com,REJECT-DROP
DOMAIN-SUFFIX,umengcloud.com,REJECT-DROP
DOMAIN-SUFFIX,um0.cn,REJECT-DROP
DOMAIN-SUFFIX,cnzz.com,REJECT-DROP

# UC Browser / Shenma / Quark (5)
DOMAIN-SUFFIX,uc.cn,REJECT-DROP
DOMAIN-SUFFIX,ucweb.com,REJECT-DROP
DOMAIN-SUFFIX,uczzd.cn,REJECT-DROP
DOMAIN-SUFFIX,sm.cn,REJECT-DROP
DOMAIN-SUFFIX,quark.cn,REJECT-DROP

# MobTech / MobPush (1)
DOMAIN-SUFFIX,mob.com,REJECT-DROP

# JPush (4)
DOMAIN-SUFFIX,jpush.cn,REJECT-DROP
DOMAIN-SUFFIX,jpush.io,REJECT-DROP
DOMAIN-SUFFIX,jiguang.cn,REJECT-DROP
DOMAIN-SUFFIX,jpush-ipv6.cn,REJECT-DROP

# ByteDance applications and content services (28)
DOMAIN-SUFFIX,bytedance.com,REJECT-DROP
DOMAIN-SUFFIX,bytedanceapi.com,REJECT-DROP
DOMAIN-SUFFIX,snssdk.com,REJECT-DROP
DOMAIN-SUFFIX,isnssdk.com,REJECT-DROP
DOMAIN-SUFFIX,sgsnssdk.com,REJECT-DROP
DOMAIN-SUFFIX,douyin.com,REJECT-DROP
DOMAIN-SUFFIX,toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,toutiaopage.com,REJECT-DROP
DOMAIN-SUFFIX,toutiaoapi.com,REJECT-DROP
DOMAIN-SUFFIX,toutiaocloud.com,REJECT-DROP
DOMAIN-SUFFIX,ixigua.com,REJECT-DROP
DOMAIN-SUFFIX,xiguaapp.cn,REJECT-DROP
DOMAIN-SUFFIX,pipix.com,REJECT-DROP
DOMAIN-SUFFIX,dongchedi.com,REJECT-DROP
DOMAIN-SUFFIX,doubao.com,REJECT-DROP
DOMAIN-SUFFIX,coze.cn,REJECT-DROP
DOMAIN-SUFFIX,fanqienovel.com,REJECT-DROP
DOMAIN-SUFFIX,huoshan.com,REJECT-DROP
DOMAIN-SUFFIX,huoshanzhibo.com,REJECT-DROP
DOMAIN-SUFFIX,feiliao.com,REJECT-DROP
DOMAIN-SUFFIX,amemv.com,REJECT-DROP
DOMAIN-SUFFIX,iesdouyin.com,REJECT-DROP
DOMAIN-SUFFIX,douyinpay.com,REJECT-DROP
DOMAIN-SUFFIX,baike.com,REJECT-DROP
DOMAIN-SUFFIX,wukong.com,REJECT-DROP
DOMAIN-SUFFIX,tiktok.com,REJECT-DROP
DOMAIN-SUFFIX,capcut.com,REJECT-DROP
DOMAIN-SUFFIX,lemon8-app.com,REJECT-DROP

# ByteDance data and SDK services (13)
DOMAIN-SUFFIX,bytegoofy.com,REJECT-DROP
DOMAIN-SUFFIX,bytetcc.com,REJECT-DROP
DOMAIN-SUFFIX,bytescm.com,REJECT-DROP
DOMAIN-SUFFIX,bytedns.net,REJECT-DROP
DOMAIN-SUFFIX,bytednsdoc.com,REJECT-DROP
DOMAIN-SUFFIX,douyinliving.com,REJECT-DROP
DOMAIN-SUFFIX,zjurl.cn,REJECT-DROP
DOMAIN-SUFFIX,zijieapi.com,REJECT-DROP
DOMAIN-SUFFIX,ibytedapm.com,REJECT-DROP
DOMAIN-SUFFIX,oceanengine.com,REJECT-DROP
DOMAIN-SUFFIX,chengzijianzhan.com,REJECT-DROP
DOMAIN-SUFFIX,dcarapi.com,REJECT-DROP
DOMAIN-SUFFIX,xiaoxiaapi.com,REJECT-DROP

# ByteDance enterprise and infrastructure (13)
DOMAIN-SUFFIX,feishu.cn,REJECT-DROP
DOMAIN-SUFFIX,feishu.net,REJECT-DROP
DOMAIN-SUFFIX,feishupkg.com,REJECT-DROP
DOMAIN-SUFFIX,okr.com,REJECT-DROP
DOMAIN-SUFFIX,volcengine.com,REJECT-DROP
DOMAIN-SUFFIX,volcengineapi.com,REJECT-DROP
DOMAIN-SUFFIX,volces.com,REJECT-DROP
DOMAIN-SUFFIX,bytedns2.com,REJECT-DROP
DOMAIN-SUFFIX,bytevcloudapi.com,REJECT-DROP
DOMAIN-SUFFIX,byteoversea.com,REJECT-DROP
DOMAIN-SUFFIX,byteoversea.net,REJECT-DROP
DOMAIN-SUFFIX,ttoversea.net,REJECT-DROP
DOMAIN-SUFFIX,musical.ly,REJECT-DROP

# ByteDance advertising networks (9)
DOMAIN-SUFFIX,pangolin-sdk-toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,pangolin-sdk-toutiao1.com,REJECT-DROP
DOMAIN-SUFFIX,pangolin-dsp-toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,pglstatp-sdk-toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,pglstatp-snssdk-toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,pglstatp-toutiao.com,REJECT-DROP
DOMAIN-SUFFIX,pglstatp-toutiao-b.com,REJECT-DROP
DOMAIN-SUFFIX,byteadverts.com,REJECT-DROP
DOMAIN-SUFFIX,shoppingads.cn,REJECT-DROP
```

## Sources

- [Umeng service terms](https://www.umeng.com/terms)
- [JPush documentation](https://docs.jiguang.cn/jpush)
- [MobTech MobPush](https://www.mob.com/mobService/mobpush)
- [Domain-list community: ByteDance](https://github.com/v2ray/domain-list-community/blob/master/data/bytedance)
- [Domain-list community: TikTok](https://github.com/v2ray/domain-list-community/blob/master/data/tiktok)
- [ByteDance products](https://www.bytedance.com/products-services)

These sources support classification but do not confirm the current owner or purpose of every hostname. A blocked suffix may affect unrelated or retired services.

## Routing interactions

Media/CDN suffixes such as `byteimg.com`, `bytecdn.com`, `bytetos.com`, `douyincdn.com`, `tiktokcdn.com`, and `feishucdn.com` are not part of this block inventory. They follow separate media-delivery policy; see [CDN evidence](global-cdn.md). The exact `cdn.volcengineapi.com` `DIRECT` exception precedes the broader `volcengineapi.com` block.

If an affected app fails, check the connection log and narrow or remove the minimum relevant suffix rule. Do not broadly allow shared CDN infrastructure as a workaround.
