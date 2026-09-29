import requests

VPNGATE_API = "https://www.vpngate.net/api/iphone/"

def get_vpngate_nodes():
    response = requests.get(VPNGATE_API, timeout=30)
    response.raise_for_status()

    lines = response.text.splitlines()
    nodes = []

    for line in lines:
        if not line or line.startswith("*") or line.startswith("#"):
            continue

        parts = line.split(",")

        if len(parts) < 15:
            continue

        try:
            nodes.append({
                "host": parts[1],
                "ip": parts[3],
                "country": parts[6],
                "country_long": parts[5],
                "port": 443,
            })
        except Exception:
            continue

    return nodes


if __name__ == "__main__":
    nodes = get_vpngate_nodes()
    print(f"获取到 {len(nodes)} 个 VPN Gate 节点")

    for node in nodes:
        print(node)
