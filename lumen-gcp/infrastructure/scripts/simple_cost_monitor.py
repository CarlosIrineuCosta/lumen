#!/usr/bin/env python3
"""
Simple Google Cloud Cost Monitoring for Lumen Project
Monitors project resources and estimates costs
"""

import os
import subprocess
import json
from datetime import datetime

class SimpleCostMonitor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        
    def get_project_resources(self):
        """Get current project resources using gcloud CLI"""
        try:
            # Use the installed Google Cloud SDK
            gcloud_path = "/home/cdc/projects/wasenet/lumen-gcp/backend/google-cloud-sdk/bin"
            
            # Get Cloud Storage usage
            storage_cmd = f"{gcloud_path}/gsutil du -s gs://lumen-photos-20250731"
            storage_result = subprocess.run(storage_cmd.split(), 
                                          capture_output=True, text=True)
            
            storage_size = 0
            if storage_result.returncode == 0:
                # Parse storage size (first number in bytes)
                storage_size = int(storage_result.stdout.split()[0]) if storage_result.stdout.strip() else 0
            
            # Get active services
            services_cmd = f"{gcloud_path}/gcloud services list --enabled --project={self.project_id} --format=json"
            services_result = subprocess.run(services_cmd.split(), 
                                           capture_output=True, text=True)
            
            services = []
            if services_result.returncode == 0:
                try:
                    services_data = json.loads(services_result.stdout)
                    services = [s['config']['name'] for s in services_data]
                except json.JSONDecodeError:
                    services = ["Unable to parse services"]
            
            return {
                "storage_bytes": storage_size,
                "storage_mb": storage_size / (1024 * 1024),
                "storage_gb": storage_size / (1024 * 1024 * 1024),
                "active_services": services[:10]  # Limit to first 10
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def estimate_daily_cost(self, resources: dict) -> dict:
        """Estimate daily costs based on resources"""
        
        # Rough cost estimates (USD)
        costs = {
            "cloud_storage": 0.0,
            "firebase_auth": 0.0,
            "cloud_run": 0.0,  # Not deployed yet
            "networking": 0.05,  # Base networking
            "total": 0.0
        }
        
        if "storage_gb" in resources:
            # Cloud Storage: ~$0.020 per GB per month
            monthly_storage = resources["storage_gb"] * 0.020
            costs["cloud_storage"] = monthly_storage / 30  # Daily
        
        # Firebase Auth: Free tier (up to 10k users)
        costs["firebase_auth"] = 0.0
        
        # Calculate total
        costs["total"] = sum(v for k, v in costs.items() if k != "total")
        
        return costs
    
    def generate_report(self) -> str:
        """Generate cost monitoring report"""
        resources = self.get_project_resources()
        
        report = f"""
Lumen Project - Simple Cost Monitor
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {self.project_id}

=== RESOURCES ===
"""
        
        if "error" in resources:
            report += f"Error getting resources: {resources['error']}\n"
        else:
            report += f"Cloud Storage: {resources['storage_mb']:.2f} MB ({resources['storage_gb']:.4f} GB)\n"
            report += f"Active Services: {len(resources['active_services'])}\n"
            
            # Show some services
            if resources['active_services']:
                report += "Key Services:\n"
                for service in resources['active_services'][:5]:
                    service_name = service.split('.')[-2] if '.' in service else service
                    report += f"  - {service_name}\n"
        
        # Cost estimates
        if "error" not in resources:
            costs = self.estimate_daily_cost(resources)
            
            report += f"""
=== ESTIMATED DAILY COSTS ===
Cloud Storage: ${costs['cloud_storage']:.4f}
Firebase Auth: ${costs['firebase_auth']:.4f}
Cloud Run: ${costs['cloud_run']:.4f} (not deployed)
Networking: ${costs['networking']:.4f}
------------------------
Total Daily: ${costs['total']:.4f}
Monthly Est: ${costs['total'] * 30:.2f}

=== BUDGET STATUS ===
Target: $3-7/day
Current: ${costs['total']:.4f}/day
Status: {'✅ WITHIN BUDGET' if costs['total'] <= 7 else '⚠️  OVER BUDGET'}
"""
        
        return report

if __name__ == "__main__":
    project_id = "lumen-photo-app-20250731"
    monitor = SimpleCostMonitor(project_id)
    print(monitor.generate_report())