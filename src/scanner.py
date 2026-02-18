import threading
import concurrent.futures
from network_utils import smart_ping, get_last_working_hop, get_father_port_status

class ProScanner:
    def __init__(self, db):
        self.db = db
        self.scanned = set()
        self.scan_lock = threading.Lock()
        self.stats = {"UP": 0, "DOWN": 0}

    def scan_node(self, device_id):
        # Prevent Loop/Double Scan
        with self.scan_lock:
            if device_id in self.scanned: return
            self.scanned.add(device_id)

        device = self.db.get_device(device_id)
        if not device: return

        print(f"[*] Checking: {device['name']} ({device['ip']})...")

        if smart_ping(device['ip']):
            self.db.update_status(device_id, "UP")
            self.stats["UP"] += 1
            
            # PARALLEL CHILD SCAN
            children = self.db.get_children(device_id)
            if children:
                # Spawn threads for children (Max 10 concurrent threads)
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    executor.map(self.scan_node, children)
        else:
            self.db.update_status(device_id, "DOWN")
            self.stats["DOWN"] += 1
            # Run diagnostic in BACKGROUND thread (Don't block main scan)
            threading.Thread(target=self.run_diagnostic, args=(device,)).start()

    def run_diagnostic(self, device):
        print(f"🚨 ALERT: {device['name']} is DOWN. Tracing...")
        father_ip = get_last_working_hop(device['ip'])
        ssh_data = "N/A"
        
        if father_ip:
            ssh_data = get_father_port_status(father_ip)
            
        self.send_notification(device, father_ip, ssh_data)

    def send_notification(self, device, father_ip, ssh_output):
        print(f"\n{'='*50}")
        print(f"🛑 CRITICAL FAILURE: {device['name']}")
        print(f"📍 IP: {device['ip']} | MAC: {device['mac']}")
        print(f"🔗 LAST REACHABLE HOP: {father_ip}")
        print(f"📋 FATHER PORT STATUS:\n{ssh_output}")
        print(f"{'='*50}\n")