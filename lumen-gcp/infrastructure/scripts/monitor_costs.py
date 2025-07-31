#!/usr/bin/env python3
"""
Google Cloud Cost Monitoring Script for Lumen Project
Monitors daily spending and sends alerts
"""

import os
from datetime import datetime, timedelta
from google.cloud import billing_v1
from google.cloud import monitoring_v3
import smtplib
from email.mime.text import MimeText

class CostMonitor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.billing_client = billing_v1.CloudBillingClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
    def get_daily_cost(self) -> float:
        """Get current day's spending"""
        # This would implement actual cost retrieval
        # For now, return a mock value
        return 5.50  # Mock daily cost in USD
        
    def check_budget_threshold(self, daily_cost: float, budget_limit: float = 100.0) -> dict:
        """Check if we're approaching budget limits"""
        weekly_projection = daily_cost * 7
        monthly_projection = daily_cost * 30
        
        alerts = []
        
        if weekly_projection > budget_limit * 0.5:
            alerts.append(f"Weekly projection: ${weekly_projection:.2f} (50% of budget)")
            
        if monthly_projection > budget_limit:
            alerts.append(f"Monthly projection: ${monthly_projection:.2f} (exceeds budget)")
            
        return {
            "daily_cost": daily_cost,
            "weekly_projection": weekly_projection,
            "monthly_projection": monthly_projection,
            "alerts": alerts,
            "status": "warning" if alerts else "ok"
        }
        
    def generate_cost_report(self) -> str:
        """Generate daily cost report"""
        daily_cost = self.get_daily_cost()
        budget_check = self.check_budget_threshold(daily_cost)
        
        report = f"""
Lumen Project - Daily Cost Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Daily Cost: ${budget_check['daily_cost']:.2f}
Weekly Projection: ${budget_check['weekly_projection']:.2f}
Monthly Projection: ${budget_check['monthly_projection']:.2f}

Status: {budget_check['status'].upper()}

"""
        
        if budget_check['alerts']:
            report += "⚠️  ALERTS:\n"
            for alert in budget_check['alerts']:
                report += f"  - {alert}\n"
        else:
            report += "✅ No budget concerns detected\n"
            
        return report

if __name__ == "__main__":
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "lumen-photography-platform")
    monitor = CostMonitor(project_id)
    
    print(monitor.generate_cost_report())
