import schedule
import time
from database import NetworkDB
from scanner import ProScanner

# CONFIGURATION
DB = NetworkDB()
ROOT_ROUTER_IDS = [1, 2, 3, 4, 5]  # The IDs of your 5 Core Routers

def job():
    print(f"\n>>> 🕒 STARTING NETWORK SCAN: {time.ctime()}")
    scanner = ProScanner(DB)
    
    # Start scanning from all 5 routers simultaneously
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(scanner.scan_node, ROOT_ROUTER_IDS)
        
    print(f">>> ✅ SCAN COMPLETE. Stats: UP={scanner.stats['UP']} | DOWN={scanner.stats['DOWN']}")

if __name__ == "__main__":
    # Run once immediately to test
    job()
    
    # Schedule every 5 minutes
    schedule.every(5).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)