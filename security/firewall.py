import ipaddress
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(filename="firewall.log", level=logging.INFO)

# Rule categories
WHITELIST = set()
BLACKLIST = set()
TRAFFIC_LOG = []
ANOMALY_DETECTED = []

# Configurable firewall parameters
MAX_REQUESTS_PER_MIN = 100  # Max allowed requests from an IP per minute
BLACKLIST_TIME = 60  # Time in minutes to block an IP
MONITOR_INTERVAL = timedelta(minutes=1)

# Anomaly thresholds
ANOMALY_THRESHOLD = 0.05  # 5% of total traffic considered anomalous

# Load initial whitelists and blacklists from files
def load_firewall_rules():
    try:
        with open("whitelist.json", "r") as f:
            data = json.load(f)
            for ip in data.get("whitelist", []):
                WHITELIST.add(ip)
        with open("blacklist.json", "r") as f:
            data = json.load(f)
            for ip in data.get("blacklist", []):
                BLACKLIST.add(ip)
    except FileNotFoundError:
        logging.info("No whitelist/blacklist file found. Starting with an empty rule set.")

# Save whitelist and blacklist updates to files
def save_firewall_rules():
    with open("whitelist.json", "w") as f:
        json.dump({"whitelist": list(WHITELIST)}, f, indent=2)
    with open("blacklist.json", "w") as f:
        json.dump({"blacklist": list(BLACKLIST)}, f, indent=2)

# Basic traffic logging
def log_traffic(ip, request_data):
    timestamp = datetime.now()
    TRAFFIC_LOG.append({"ip": ip, "request_data": request_data, "timestamp": timestamp})
    logging.info(f"Traffic logged: IP={ip}, Data={request_data}, Time={timestamp}")

# Add an IP to the blacklist
def blacklist_ip(ip):
    BLACKLIST.add(ip)
    save_firewall_rules()
    logging.warning(f"IP blacklisted: {ip}")

# Remove an IP from the blacklist after BLACKLIST_TIME
def remove_ip_from_blacklist(ip):
    if ip in BLACKLIST:
        BLACKLIST.remove(ip)
        save_firewall_rules()
        logging.info(f"IP removed from blacklist: {ip}")

# Whitelist IPs allowed to bypass firewall rules
def whitelist_ip(ip):
    WHITELIST.add(ip)
    save_firewall_rules()
    logging.info(f"IP whitelisted: {ip}")

# Check if IP is blacklisted
def is_blacklisted(ip):
    return ip in BLACKLIST

# Basic IP filtering based on whitelist and blacklist
def filter_traffic(ip, request_data):
    if ip in WHITELIST:
        logging.info(f"Traffic allowed for whitelisted IP: {ip}")
        return True
    if ip in BLACKLIST:
        logging.warning(f"Traffic blocked for blacklisted IP: {ip}")
        return False
    return True  # Default allow, further inspection needed

# Monitor request rates to detect potential DDoS attacks
def monitor_request_rate(ip):
    now = datetime.now()
    window_start = now - MONITOR_INTERVAL
    requests = [log for log in TRAFFIC_LOG if log["ip"] == ip and log["timestamp"] >= window_start]
    if len(requests) > MAX_REQUESTS_PER_MIN:
        blacklist_ip(ip)
        logging.warning(f"DDoS detected: IP={ip}, Requests={len(requests)}")

# Traffic anomaly detection (basic heuristic)
def detect_anomalies():
    total_traffic = len(TRAFFIC_LOG)
    if total_traffic == 0:
        return

    traffic_by_ip = {}
    for log in TRAFFIC_LOG:
        ip = log["ip"]
        traffic_by_ip[ip] = traffic_by_ip.get(ip, 0) + 1

    for ip, count in traffic_by_ip.items():
        if count / total_traffic > ANOMALY_THRESHOLD:
            ANOMALY_DETECTED.append(ip)
            logging.warning(f"Anomaly detected: IP={ip}, Traffic Proportion={count/total_traffic:.2%}")

# Check if an IP is part of known botnets (external services)
def check_known_botnets(ip):
    known_botnets = set()  # Set of botnet IPs from an external source
    if ip in known_botnets:
        blacklist_ip(ip)
        logging.warning(f"Botnet IP blocked: {ip}")
        return True
    return False

# Packet filtering for invalid or malformed requests
def packet_filter(request_data):
    try:
        data = json.loads(request_data)
        if "invalid_field" in data:
            return False
        return True
    except json.JSONDecodeError:
        logging.error("Malformed packet detected")
        return False

# Firewall decision-making logic
def firewall_decision(ip, request_data):
    if not filter_traffic(ip, request_data):
        return "Blocked"

    if not packet_filter(request_data):
        blacklist_ip(ip)
        return "Blocked"

    log_traffic(ip, request_data)
    monitor_request_rate(ip)

    if is_blacklisted(ip):
        return "Blocked"

    if check_known_botnets(ip):
        return "Blocked"

    detect_anomalies()
    return "Allowed"

# Simulate incoming traffic
def simulate_traffic(ip, request_data):
    decision = firewall_decision(ip, request_data)
    logging.info(f"Firewall decision for IP={ip}: {decision}")
    return decision

# Periodically remove expired blacklisted IPs (after BLACKLIST_TIME)
def clean_blacklist():
    expiration_time = datetime.now() - timedelta(minutes=BLACKLIST_TIME)
    expired_ips = [ip for ip in BLACKLIST if ip not in TRAFFIC_LOG or TRAFFIC_LOG[-1]["timestamp"] < expiration_time]

    for ip in expired_ips:
        remove_ip_from_blacklist(ip)

# Firewall configuration entry point
if __name__ == "__main__":
    load_firewall_rules()
    
    # Simulated traffic for firewall testing
    traffic_samples = [
        ("192.168.0.1", '{"user_id": "123", "action": "login"}'),
        ("10.0.0.5", '{"user_id": "456", "action": "purchase", "amount": "100"}'),
        ("172.16.0.3", '{"user_id": "789", "action": "invalid_field"}'),
        ("192.168.0.2", '{"user_id": "999", "action": "login"}')
    ]
    
    for ip, request in traffic_samples:
        simulate_traffic(ip, request)
    
    clean_blacklist()