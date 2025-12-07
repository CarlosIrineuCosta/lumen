#!/usr/bin/env python3
"""
Comprehensive Test Report Generator
Consolidates results from overnight testing, UI discovery, and performance metrics
into executive summary and detailed technical reports
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import glob
import re


@dataclass
class TestSummary:
    """Summary statistics for test execution"""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    execution_time: float = 0.0
    success_rate: float = 0.0


class TestReportGenerator:
    """Generates comprehensive test reports from multiple sources"""
    
    def __init__(self, project_root: str = "/home/cdc/Storage/NVMe/projects/lumen"):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test-reports"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def find_latest_reports(self) -> Dict[str, Optional[Path]]:
        """Find the most recent test reports"""
        reports = {
            "overnight": None,
            "ui_discovery": None,
            "junit_xml": [],
            "html_reports": []
        }
        
        if not self.reports_dir.exists():
            return reports
        
        # Find overnight test reports
        overnight_dirs = list(self.reports_dir.glob("overnight_*"))
        if overnight_dirs:
            latest_overnight = max(overnight_dirs, key=lambda x: x.stat().st_mtime)
            reports["overnight"] = latest_overnight
            
            # Find JUnit XML files in overnight directory
            reports["junit_xml"] = list(latest_overnight.glob("*_junit.xml"))
            reports["html_reports"] = list(latest_overnight.glob("*_report.html"))
        
        # Find UI discovery reports
        ui_dirs = list(self.reports_dir.glob("ui_discovery_*"))
        if ui_dirs:
            latest_ui = max(ui_dirs, key=lambda x: x.stat().st_mtime)
            reports["ui_discovery"] = latest_ui / "feature_discovery.json"
        
        return reports
    
    def parse_junit_xml(self, xml_file: Path) -> TestSummary:
        """Parse JUnit XML file to extract test statistics"""
        summary = TestSummary()
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite root elements
            if root.tag == "testsuites":
                for testsuite in root.findall("testsuite"):
                    summary.total_tests += int(testsuite.get("tests", 0))
                    summary.passed += int(testsuite.get("tests", 0)) - int(testsuite.get("failures", 0)) - int(testsuite.get("errors", 0)) - int(testsuite.get("skipped", 0))
                    summary.failed += int(testsuite.get("failures", 0))
                    summary.errors += int(testsuite.get("errors", 0))
                    summary.skipped += int(testsuite.get("skipped", 0))
                    summary.execution_time += float(testsuite.get("time", 0))
            elif root.tag == "testsuite":
                summary.total_tests = int(root.get("tests", 0))
                summary.failed = int(root.get("failures", 0))
                summary.errors = int(root.get("errors", 0))
                summary.skipped = int(root.get("skipped", 0))
                summary.passed = summary.total_tests - summary.failed - summary.errors - summary.skipped
                summary.execution_time = float(root.get("time", 0))
            
            if summary.total_tests > 0:
                summary.success_rate = (summary.passed / summary.total_tests) * 100
                
        except Exception as e:
            print(f"Warning: Could not parse {xml_file}: {e}")
        
        return summary
    
    def aggregate_junit_results(self, junit_files: List[Path]) -> Dict[str, TestSummary]:
        """Aggregate results from multiple JUnit XML files"""
        results = {}
        total_summary = TestSummary()
        
        for junit_file in junit_files:
            # Extract phase name from filename
            phase_name = junit_file.stem.replace("_junit", "")
            summary = self.parse_junit_xml(junit_file)
            results[phase_name] = summary
            
            # Aggregate totals
            total_summary.total_tests += summary.total_tests
            total_summary.passed += summary.passed
            total_summary.failed += summary.failed
            total_summary.errors += summary.errors
            total_summary.skipped += summary.skipped
            total_summary.execution_time += summary.execution_time
        
        if total_summary.total_tests > 0:
            total_summary.success_rate = (total_summary.passed / total_summary.total_tests) * 100
        
        results["TOTAL"] = total_summary
        return results
    
    def parse_overnight_summary(self, overnight_dir: Path) -> Dict[str, Any]:
        """Parse overnight test summary file"""
        summary_file = overnight_dir / "summary.txt"
        summary = {
            "found": summary_file.exists(),
            "execution_log": None,
            "key_metrics": {}
        }
        
        if summary_file.exists():
            try:
                content = summary_file.read_text()
                
                # Extract key metrics using regex
                patterns = {
                    "total_tests": r"Total Tests:\s*(\d+)",
                    "passed": r"Passed:\s*(\d+)",
                    "failed": r"Failed:\s*(\d+)",
                    "errors": r"Errors:\s*(\d+)", 
                    "skipped": r"Skipped:\s*(\d+)",
                    "success_rate": r"Success Rate:\s*([\d.]+)%",
                    "total_duration": r"Total Duration:\s*(\d+)s"
                }
                
                for metric, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        try:
                            summary["key_metrics"][metric] = float(match.group(1))
                        except ValueError:
                            summary["key_metrics"][metric] = match.group(1)
                
                summary["execution_log"] = content
                
            except Exception as e:
                print(f"Warning: Could not parse overnight summary: {e}")
        
        return summary
    
    def load_ui_discovery(self, ui_report_file: Path) -> Dict[str, Any]:
        """Load UI discovery report"""
        ui_data = {"found": ui_report_file.exists()}
        
        if ui_report_file.exists():
            try:
                with open(ui_report_file, 'r') as f:
                    ui_data.update(json.load(f))
            except Exception as e:
                print(f"Warning: Could not load UI discovery report: {e}")
        
        return ui_data
    
    def generate_executive_summary(self, 
                                   junit_results: Dict[str, TestSummary],
                                   overnight_summary: Dict[str, Any],
                                   ui_discovery: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        
        total_summary = junit_results.get("TOTAL", TestSummary())
        
        # Determine overall health
        if total_summary.success_rate >= 95:
            health_status = "EXCELLENT"
            health_color = "🟢"
        elif total_summary.success_rate >= 85:
            health_status = "GOOD"
            health_color = "🟡"
        elif total_summary.success_rate >= 70:
            health_status = "FAIR"
            health_color = "🟠"
        else:
            health_status = "NEEDS ATTENTION"
            health_color = "🔴"
        
        # UI implementation status
        ui_implementation = "N/A"
        if ui_discovery.get("found") and "discovery_summary" in ui_discovery:
            ui_impl_pct = ui_discovery["discovery_summary"].get("implementation_percentage", 0)
            ui_implementation = f"{ui_impl_pct}%"
        
        # Critical issues count
        critical_issues = 0
        if ui_discovery.get("found") and "missing_features_by_priority" in ui_discovery:
            critical_issues = len(ui_discovery["missing_features_by_priority"].get("critical", []))
        
        report = f"""
LUMEN PROJECT - TEST EXECUTION EXECUTIVE SUMMARY
===============================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

OVERALL PROJECT HEALTH: {health_status} {health_color}

KEY METRICS:
-----------
Backend Test Coverage:    {total_summary.success_rate:.1f}% ({total_summary.passed}/{total_summary.total_tests} tests passing)
UI Implementation:        {ui_implementation}
Critical Issues:          {critical_issues}
Test Execution Time:      {total_summary.execution_time:.0f} seconds ({total_summary.execution_time/60:.1f} minutes)

BACKEND TESTING RESULTS:
-----------------------
✓ Total Tests Executed:  {total_summary.total_tests}
✓ Tests Passed:          {total_summary.passed}
✗ Tests Failed:          {total_summary.failed}
⚠ Errors:                {total_summary.errors}
⏭ Skipped:               {total_summary.skipped}

"""
        
        # Add phase breakdown if available
        if len(junit_results) > 1:  # More than just TOTAL
            report += "TESTING PHASES:\n"
            report += "-" * 15 + "\n"
            
            for phase, summary in junit_results.items():
                if phase != "TOTAL":
                    status = "PASS" if summary.failed == 0 and summary.errors == 0 else "FAIL"
                    report += f"{phase.ljust(15)}: {status.ljust(4)} ({summary.passed}/{summary.total_tests})\n"
        
        # UI Discovery Summary
        if ui_discovery.get("found"):
            report += f"\nUI IMPLEMENTATION STATUS:\n"
            report += "-" * 25 + "\n"
            
            missing = ui_discovery.get("missing_features_by_priority", {})
            report += f"Critical Missing:  {len(missing.get('critical', []))}\n"
            report += f"High Priority:     {len(missing.get('high', []))}\n"
            report += f"Medium Priority:   {len(missing.get('medium', []))}\n"
            
            if missing.get('critical'):
                report += f"\nCRITICAL FEATURES NEEDED:\n"
                for feature in missing['critical'][:3]:  # Top 3
                    report += f"• {feature.get('description', 'Unknown feature')}\n"
        
        # Recommendations
        report += f"\nKEY RECOMMENDATIONS:\n"
        report += "-" * 20 + "\n"
        
        if total_summary.failed > 0:
            report += f"1. BACKEND: Fix {total_summary.failed} failing tests before production deployment\n"
        
        if total_summary.errors > 0:
            report += f"2. BACKEND: Resolve {total_summary.errors} test errors (likely infrastructure issues)\n"
        
        if critical_issues > 0:
            report += f"3. FRONTEND: Implement {critical_issues} critical UI features for basic functionality\n"
        
        if ui_discovery.get("found"):
            recommendations = ui_discovery.get("recommendations", [])[:3]
            for i, rec in enumerate(recommendations, start=4):
                report += f"{i}. UI: {rec}\n"
        
        report += f"\nREADY FOR PRODUCTION: {'YES' if total_summary.success_rate >= 95 and critical_issues == 0 else 'NO'}\n"
        
        if total_summary.success_rate < 95 or critical_issues > 0:
            report += f"BLOCKING ISSUES: {'Test failures' if total_summary.success_rate < 95 else ''}{' and ' if total_summary.success_rate < 95 and critical_issues > 0 else ''}{'Critical UI features missing' if critical_issues > 0 else ''}\n"
        
        return report
    
    def generate_detailed_report(self,
                                 junit_results: Dict[str, TestSummary],
                                 overnight_summary: Dict[str, Any],
                                 ui_discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed technical report"""
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "report_version": "1.0"
            },
            "backend_testing": {
                "summary": junit_results.get("TOTAL", TestSummary()).__dict__,
                "phase_breakdown": {k: v.__dict__ for k, v in junit_results.items() if k != "TOTAL"},
                "overnight_execution": overnight_summary
            },
            "ui_discovery": ui_discovery,
            "integration_status": {
                "backend_health": "healthy" if junit_results.get("TOTAL", TestSummary()).success_rate >= 85 else "unhealthy",
                "frontend_status": "implemented" if ui_discovery.get("discovery_summary", {}).get("implementation_percentage", 0) >= 50 else "partial",
                "authentication_ready": bool(ui_discovery.get("detailed_findings", {}).get("authentication", {}).get("login_button", {}).get("found")),
                "photo_features_ready": bool(ui_discovery.get("detailed_findings", {}).get("photo_features", {}).get("gallery", {}).get("found"))
            },
            "recommendations": {
                "immediate_actions": [],
                "short_term_goals": [],
                "long_term_improvements": []
            }
        }
        
        # Generate recommendations based on findings
        total_summary = junit_results.get("TOTAL", TestSummary())
        
        if total_summary.failed > 0:
            report["recommendations"]["immediate_actions"].append({
                "priority": "critical",
                "category": "backend",
                "action": f"Fix {total_summary.failed} failing backend tests",
                "impact": "Prevents production deployment"
            })
        
        if ui_discovery.get("found"):
            critical_features = ui_discovery.get("missing_features_by_priority", {}).get("critical", [])
            for feature in critical_features:
                report["recommendations"]["immediate_actions"].append({
                    "priority": "critical",
                    "category": "frontend",
                    "action": f"Implement {feature.get('feature', 'missing feature')}",
                    "impact": feature.get("description", "No description")
                })
        
        return report
    
    def save_reports(self, executive_summary: str, detailed_report: Dict[str, Any]):
        """Save both executive and detailed reports"""
        output_dir = self.reports_dir / f"consolidated_{self.timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save executive summary
        exec_file = output_dir / "executive_summary.txt"
        exec_file.write_text(executive_summary)
        
        # Save detailed report
        detail_file = output_dir / "detailed_report.json"
        with open(detail_file, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)
        
        # Create index file
        index_file = output_dir / "README.md"
        index_content = f"""# Test Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files in this report:

- `executive_summary.txt` - High-level summary for stakeholders
- `detailed_report.json` - Technical details and metrics
- `README.md` - This file

## Quick Access:

- **Backend Test Success Rate**: {detailed_report['backend_testing']['summary']['success_rate']:.1f}%
- **UI Implementation**: {detailed_report['ui_discovery'].get('discovery_summary', {}).get('implementation_percentage', 'N/A')}%
- **Critical Issues**: {len(detailed_report['recommendations']['immediate_actions'])}

## Next Steps:

Review executive_summary.txt for key findings and recommendations.
"""
        index_file.write_text(index_content)
        
        return output_dir
    
    def generate_comprehensive_report(self) -> Path:
        """Generate complete test report from all available sources"""
        print("Generating comprehensive test report...")
        print("=" * 50)
        
        # Find latest reports
        reports = self.find_latest_reports()
        
        print(f"Found reports:")
        print(f"  - Overnight tests: {'Yes' if reports['overnight'] else 'No'}")
        print(f"  - UI discovery:    {'Yes' if reports['ui_discovery'] and reports['ui_discovery'].exists() else 'No'}")
        print(f"  - JUnit XML files: {len(reports['junit_xml'])}")
        
        # Parse all data sources
        junit_results = {}
        if reports['junit_xml']:
            junit_results = self.aggregate_junit_results(reports['junit_xml'])
        
        overnight_summary = {}
        if reports['overnight']:
            overnight_summary = self.parse_overnight_summary(reports['overnight'])
        
        ui_discovery = {}
        if reports['ui_discovery'] and reports['ui_discovery'].exists():
            ui_discovery = self.load_ui_discovery(reports['ui_discovery'])
        
        # Generate reports
        print("Generating executive summary...")
        executive_summary = self.generate_executive_summary(junit_results, overnight_summary, ui_discovery)
        
        print("Generating detailed report...")
        detailed_report = self.generate_detailed_report(junit_results, overnight_summary, ui_discovery)
        
        # Save reports
        print("Saving reports...")
        output_dir = self.save_reports(executive_summary, detailed_report)
        
        print(f"\nReport generation complete!")
        print(f"Reports saved to: {output_dir}")
        
        return output_dir


def main():
    """Main report generation function"""
    print("Lumen Test Report Generator")
    print("=" * 50)
    
    generator = TestReportGenerator()
    
    try:
        output_dir = generator.generate_comprehensive_report()
        
        # Display executive summary
        exec_file = output_dir / "executive_summary.txt"
        if exec_file.exists():
            print("\n" + "=" * 60)
            print("EXECUTIVE SUMMARY")
            print("=" * 60)
            print(exec_file.read_text())
        
        print("\n" + "=" * 60)
        print(f"Complete reports available at: {output_dir}")
        print("Files generated:")
        for file in sorted(output_dir.glob("*")):
            print(f"  - {file.name}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)