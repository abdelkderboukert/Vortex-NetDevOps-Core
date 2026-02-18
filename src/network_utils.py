import subprocess
import socket
import re
import time
import random
from netmiko import ConnectHandler
from pythonping import ping

# 1. SMART PING (Handles ICMP blocks)
def smart_ping(ip):
    # Try ICMP first
    try:
        response = ping(ip, count=1, timeout=0.5)
        if response.success(): return True
    except: pass
    
    # Fallback: Check TCP Port 22 (SSH)
    try:
        with socket.create_connection((ip, 22), timeout=1):
            return True
    except:
        return False

# 2. DIAGNOSTIC TRACEROUTE
def get_last_working_hop(target_ip):
    try:
        # Use 'tracert' for Windows, 'traceroute' for Linux
        cmd = ["tracert", "-d", "-h", "10", target_ip] 
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        ips = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
        return ips[-2] if len(ips) > 1 else None
    except:
        return None

# 3. SSH INSPECTION
def get_father_port_status(ip):
    # Random delay to prevent CoPP (Control Plane Policing) blocks
    time.sleep(random.uniform(0.5, 2.0))
    
    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': 'admin',
        'password': 'password123',
        'fast_cli': True,
        'conn_timeout': 10
    }
    try:
        with ConnectHandler(**device) as ssh:
            return ssh.send_command("show ip int brief | exclude unassigned")
    except Exception as e:
        return f"SSH Error: {str(e)}"