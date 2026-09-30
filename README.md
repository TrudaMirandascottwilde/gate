# VPN Gate SSTP 节点 → edgetunnel 链式代理

自动抓取 [VPN Gate](https://www.vpngate.net/) 的 SSTP 家宽/机房节点，检测可用后按国家分组，生成可直接粘贴进 edgetunnel 后台的链式代理清单，**每 30 分钟自动更新一次**。

> 一句话：你只需要定期打开一个固定 URL，全选复制，粘进 edgetunnel 后台，就能用上几十个按国家分类的 SSTP 家宽节点。

---

## 一、这是什么 / 解决什么问题

VPN Gate 的 SSTP 节点每 30 分钟就会换一批，手动一个个测试、筛选、填进 edgetunnel 太痛苦。

这个仓库把整条流水线自动化了：

1. 抓取 VPN Gate 原始节点（官方 CSV，失败自动回退镜像）
2. 只保留 SSTP（TCP）节点，按 host+port+协议 去重
3. 并发调用检测 Worker（Cloudflare）逐个检测可用性
4. 保留成功节点 → 按国家分组 → 住宅优先、延迟升序
5. 生成固定 URL 的清单文件，走 GitHub Pages 发布

---

## 二、产物（固定 URL，随 30 分钟流水线自动刷新）

| 文件 | URL | 用途 |
| :--- | :--- | :--- |
| **hosts.txt** | https://jerylihub.github.io/gate/hosts.txt | ✅ **核心**：直接粘贴进 edgetunnel 后台 |
| chains.txt | https://jerylihub.github.io/gate/chains.txt | 备注片段，备用参考 |
| data.json | https://jerylihub.github.io/gate/data.json | 原始检测数据 |
| index.html | https://jerylihub.github.io/gate/ | 网页展示 |

> ⚠️ sub.txt 是早期实验产物，**请勿使用**（链式代理需由 edgetunnel 服务端生成，不应手动拼 vless 链接）。

---

## 三、使用教程（给别人看这段就够）

### 前置条件
- 已部署 edgetunnel（Cloudflare Worker），并绑定了自己的域名
- 一个客户端：v2rayN / Clash Verge / v2rayNG 等

### 步骤（约 1 分钟）

1. 打开 https://jerylihub.github.io/gate/hosts.txt
2. 浏览器里 Ctrl+A 全选 → Ctrl+C 复制
3. 进 edgetunnel 后台（你的域名后面加 /admin），找到「**自定义优选IP**」文本框
4. 把光标移到现有内容的**末尾**，Ctrl+V 粘贴
5. 点保存（右下角提示「**自定义IP已保存**」即成功）
6. 在客户端里更新/刷新订阅（订阅地址就是 edgetunnel 后台给你的那个）
7. 测延迟，选一个节点用

### 每 30 分钟更新一次
节点每 30 分钟换一批，想换新节点时：**重新打开 hosts.txt → 全选复制 → 覆盖粘贴**即可。名字（日本-01、韩国-01…）保持不变，只是背后的节点地址换了。

---

## 四、如何更换优选域名（重点）

入口地址用的是「**优选域名**」——它决定客户端连 Cloudflare 用哪个 IP、稳不稳。域名被墙或延迟高，可用节点就少。

### 在哪个文件、哪一行改
- 文件：**vpngate.py**
- 位置：**约第 455 行**，EDGE_HOSTS = [ ... ]

### 改法

1. 用测速工具（如 bestcf）测一批 Cloudflare 优选域名，得到延迟低、**实际能连通**的域名
2. 打开 vpngate.py，找到 EDGE_HOSTS
3. 把 os.environ.get("EDGE_HOSTS", "..." ) 里的域名列表，换成你自己测出来的（逗号分隔，格式 域名:443）
4. 提交推送（git add vpngate.py && git commit && git push）
5. 等下一次自动运行（最多 30 分钟），或到 GitHub 仓库 Actions 手动点一次 Run workflow

### 示例（当前就是 7 个实测可用域名）

```python
EDGE_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "EDGE_HOSTS",
        "saas.072159.xyz:443,hzytjy.cn:443,ali.nonull.pp.ua:443,"
        "auto.dolby.dpdns.org:443,cdn.cnno.de:443,saas.sin.fan:443,"
        "cf.777791.xyz:443",
    ).split(",")
    if h.strip()
]
```

### 技巧
- **只留实测能通的域名**：bestcf 里延迟低 ≠ 一定能通，挑「延迟低 + 实际连接成功」的
- 数量建议 **5～10 个**：太少单域名负担重，太多容易混进被墙的域名拖累可用率
- 换完域名后，hosts.txt 里的入口会自动跟着变，你重新粘一次即可

---

## 五、其他配置（都在 vpngate.py 里）

| 常量 | 约位置 | 说明 |
| :--- | :--- | :--- |
| EDGE_HOSTS | 455 行 | ✅ 入口优选域名（换域名改这里） |
| EDT_DOMAIN | 515 行 | 你的 edgetunnel 域名 |
| EDT_UUID | 514 行 | 你的 edgetunnel UUID |
| WORKER_CHECK_URL | 54 行 | 检测 Worker 地址 |
| COUNTRY_ZH | 78 行 | 国家中文名映射 |

---

## 六、常见问题

### 只有几个节点能连
入口优选域名大部分被墙。用 bestcf 重新测速，把 EDGE_HOSTS 换成实测能通的域名（见「四」）。

### 全部 -1
检查：edgetunnel 是否部署好、域名是否解析到 Cloudflare、UUID 是否正确、传输协议是否对得上（默认按 ws/TLS 生成）。

### 30 分钟没更新
到 GitHub 仓库 Actions 页看最近一次运行是否成功、cron 是否还在（.github/workflows/check.yml）。

### 想告诉别人怎么用
把「三、使用教程」那段发给他即可，核心就一句：**打开 hosts.txt 全选复制，粘进 edgetunnel 后台「自定义优选IP」框，保存，刷新订阅**。

---

*流水线：GitHub Actions（每 30 分钟 cron） → vpngate.py → 检测 Worker → GitHub Pages*

