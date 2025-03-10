import platform
import socket
import uuid
import psutil
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("client.log"), logging.StreamHandler()]
)
logger = logging.getLogger("SystemInfoClient")

def get_system_info():
    """Collect system information."""
    try:
        # Get hostname
        hostname = socket.gethostname()
        
        # Get IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        
        # Get MAC address
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                              for elements in range(0, 48, 8)][::-1])
        
        # Get OS information
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        # Get memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent_used": memory.percent
        }
        
        # Get disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent_used": disk.percent
        }
        
        # Get CPU information
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1)
        }
        
        # Compile all information
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "hostname": hostname,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "os_info": os_info,
            "memory_info": memory_info,
            "disk_info": disk_info,
            "cpu_info": cpu_info
        }
        
        return system_info
    except Exception as e:
        logger.error(f"Error collecting system information: {e}")
        return {"error": str(e)}

def send_system_info(server_url):
    """Send system information to the server."""
    try:
        system_info = get_system_info()
        response = requests.post(
            f"{server_url}/api/system-info",
            json=system_info,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info("Successfully sent system information to server")
            return True
        else:
            logger.error(f"Failed to send system information. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending system information: {e}")
        return False

if __name__ == "__main__":
    # Configure the server URL
    SERVER_URL = "http://localhost:8000"  # Change this to your server address
    
    # Send system information
    success = send_system_info(SERVER_URL)
    
    if success:
        print("System information sent successfully!")
    else:
        print("Failed to send system information. Check logs for details.")
