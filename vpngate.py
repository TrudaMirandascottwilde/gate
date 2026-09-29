import csv
import io
import requests

VPNGATE_API = "https://www.vpngate.net/api/iphone/"


def get_vpngate_nodes():
    response = requests.get(
        VPNGATE_API,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    response.raise_for_status()

    text = response.text

    # VPN Gate API 返回的是 CSV
    lines = text.splitlines()

    # 找到真正的 CSV 表头
    header_index = None

    for i, line in enumerate(lines):
        if line.startswith("#HostName"):
            header_index = i
            break

    if header_index is None:
        raise RuntimeError("没有找到 VPN Gate CSV 表头")

    # 表头
    header = lines[header_index].lstrip("#").split(",")

    # 数据从表头下一行开始
    csv_text = "\n".join(lines[header_index + 1:])

    reader = csv.DictReader(
        io.StringIO(csv_text),
        fieldnames=header
    )

    nodes = []

    for row in reader:
        try:
            hostname = row.get("HostName", "").strip()
            ip = row.get("IP", "").strip()
            country = row.get("CountryShort", "").strip()
            country_long = row.get("CountryLong", "").strip()

            if not hostname or not ip:
                continue

            nodes.append({
                "host": hostname,
                "ip": ip,
                "country": country,
                "country_long": country_long,
                "score": row.get("Score", "").strip(),
                "ping": row.get("Ping", "").strip(),
                "speed": row.get("Speed", "").strip(),
                "sessions": row.get("NumVpnSessions", "").strip(),
                "uptime": row.get("Uptime", "").strip(),
                "users": row.get("TotalUsers", "").strip(),
                "traffic": row.get("TotalTraffic", "").strip(),
                "log_type": row.get("LogType", "").strip(),
                "operator": row.get("Operator", "").strip(),
                "message": row.get("Message", "").strip(),
            })

        except Exception:
            continue

    return nodes


if __name__ == "__main__":
    nodes = get_vpngate_nodes()

    print(f"获取到 {len(nodes)} 个 VPN Gate 节点")

    for node in nodes:
        print(
            f"{node['country']} | "
            f"{node['country_long']} | "
            f"{node['host']} | "
            f"{node['ip']} | "
            f"Score={node['score']} | "
            f"Ping={node['ping']} | "
            f"Speed={node['speed']}"
        )
