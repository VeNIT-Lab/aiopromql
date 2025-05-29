# wait_for_prometheus.py
import time

import httpx

PROM_URL = "http://prometheus:9090"
TIMEOUT = 90  # seconds
QUERY = "up[1m]"


def wait_for_data():
    deadline = time.time() + TIMEOUT
    with httpx.Client(timeout=5) as client:
        while time.time() < deadline:
            try:
                response = client.get(f"{PROM_URL}/api/v1/query", params={"query": QUERY})
                response.raise_for_status()
                data = response.json()
                if data["status"] == "success" and data["data"]["result"]:
                    print("✅ Prometheus has 1m of scrape data.")
                    return
                else:
                    print("⏳ Waiting for Prometheus to collect data...")
            except httpx.HTTPError as e:
                print(f"⚠️ HTTP error: {e}")
            except Exception as e:
                print(f"⚠️ Other error: {e}")
            time.sleep(5)
    raise TimeoutError("❌ Timed out waiting for Prometheus to return up[1m] data.")


if __name__ == "__main__":
    wait_for_data()
