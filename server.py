from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uvicorn
import json
from datetime import datetime
import os

app = FastAPI(title="System Information API", 
              description="API for receiving system information from clients")

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

class SystemInfo(BaseModel):
    """Model for system information received from clients"""
    timestamp: str
    hostname: str
    ip_address: str
    mac_address: str
    os_info: Dict[str, Any]
    memory_info: Dict[str, Any]
    disk_info: Dict[str, Any]
    cpu_info: Dict[str, Any]

@app.post("/api/system-info")
async def receive_system_info(system_info: SystemInfo):
    """Endpoint to receive system information from clients"""
    try:
        # Create a unique filename based on hostname and timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{system_info.hostname}_{current_time}.json"
        
        # Save the received data to a file
        with open(filename, "w") as f:
            json.dump(system_info.dict(), f, indent=4)
        
        return {"status": "success", "message": "System information received and saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/api/system-info/{hostname}")
async def get_system_info(hostname: str):
    """Endpoint to retrieve the latest system information for a specific hostname"""
    try:
        # List all files for the specified hostname
        files = [f for f in os.listdir("data") if f.startswith(hostname + "_")]
        
        if not files:
            raise HTTPException(status_code=404, detail=f"No data found for hostname: {hostname}")
        
        # Get the most recent file
        latest_file = max(files)
        
        # Read and return the data
        with open(f"data/{latest_file}", "r") as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

@app.get("/api/hosts")
async def get_all_hosts():
    """Endpoint to list all hostnames that have submitted system information"""
    try:
        # Extract unique hostnames from filenames
        files = os.listdir("data")
        hostnames = set()
        
        for file in files:
            # Extract hostname from filename (format: hostname_timestamp.json)
            if "_" in file and file.endswith(".json"):
                hostname = file.split("_")[0]
                hostnames.add(hostname)
        
        return {"hosts": list(hostnames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hosts: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
