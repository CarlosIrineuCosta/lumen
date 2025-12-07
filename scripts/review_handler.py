#!/usr/bin/env python3
"""
Review Handler - Core review logic processor for the /review command
Integrates with AI agents to perform comprehensive project analysis
"""

import os
import sys
import json
import ast
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse


@dataclass
class ReviewResult:
    """Structure for review findings"""
    category: str
    severity: str  # critical, high, medium, low
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None


class DocumentationAnalyzer:
    """Analyzes MD documentation and compares with actual code"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs = {}
        self.code_structure = {}

    def scan_documentation(self) -> Dict[str, Any]:
        """Scan all MD files to extract project information"""
        docs_info = {
            'project_purpose': '',
            'api_endpoints': [],
            'architecture': {},
            'installation': {},
            'configuration': {},
            'files_found': []
        }

        # Find all MD files
        for md_file in self.project_root.rglob('*.md'):
            if '.git' in str(md_file) or '.claude' in str(md_file):
                continue

            docs_info['files_found'].append(str(md_file.relative_to(self.project_root)))

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract project purpose from README or main docs
                if 'readme' in md_file.name.lower() or 'main' in md_file.name.lower():
                    docs_info['project_purpose'] = self._extract_purpose(content)

                # Extract API documentation
                if 'api' in md_file.name.lower() or 'endpoint' in content.lower():
                    docs_info['api_endpoints'].extend(self._extract_api_endpoints(content))

                # Extract architecture information
                if 'architect' in md_file.name.lower() or 'structure' in content.lower():
                    docs_info['architecture'].update(self._extract_architecture(content))

                # Extract installation instructions
                if 'install' in content.lower() or 'setup' in content.lower():
                    docs_info['installation'].update(self._extract_installation(content))

                # Extract configuration requirements
                if 'config' in content.lower() or 'env' in content.lower():
                    docs_info['configuration'].update(self._extract_configuration(content))

            except Exception as e:
                print(f"Error reading {md_file}: {e}")

        return docs_info

    def _extract_purpose(self, content: str) -> str:
        """Extract project purpose from documentation"""
        lines = content.split('\n')
        purpose = ""

        # Look for first paragraph after main title
        for i, line in enumerate(lines):
            if line.startswith('# ') and i > 0:
                # Found a main heading, get next non-empty paragraph
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        purpose = lines[j].strip()
                        if j + 1 < len(lines) and lines[j + 1].strip() and not lines[j + 1].startswith('#'):
                            purpose += " " + lines[j + 1].strip()
                        break
                break

        return purpose

    def _extract_api_endpoints(self, content: str) -> List[Dict]:
        """Extract API endpoint documentation"""
        endpoints = []

        # Look for patterns like GET /api/users, POST /api/data, etc.
        endpoint_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]+)'
        matches = re.findall(endpoint_pattern, content, re.IGNORECASE)

        for method, path in matches:
            endpoints.append({
                'method': method.upper(),
                'path': path,
                'documented': True
            })

        return endpoints

    def _extract_architecture(self, content: str) -> Dict:
        """Extract architecture information"""
        arch = {
            'modules': [],
            'patterns': [],
            'components': []
        }

        # Look for module mentions
        module_pattern = r'(?:module|component|service):\s*([^\s\n]+)'
        matches = re.findall(module_pattern, content, re.IGNORECASE)
        arch['modules'] = list(set(matches))

        # Look for pattern mentions
        patterns = ['MVC', 'REST', 'GraphQL', 'Microservices', 'Monolith', 'Serverless']
        for pattern in patterns:
            if pattern.lower() in content.lower():
                arch['patterns'].append(pattern)

        return arch

    def _extract_installation(self, content: str) -> Dict:
        """Extract installation requirements"""
        install = {
            'python_version': None,
            'dependencies': [],
            'commands': []
        }

        # Look for Python version requirements
        version_pattern = r'python\s*(\d+\.\d+)'
        match = re.search(version_pattern, content, re.IGNORECASE)
        if match:
            install['python_version'] = match.group(1)

        # Look for pip install commands
        pip_pattern = r'pip\s+install\s+([^\s\n]+)'
        matches = re.findall(pip_pattern, content)
        install['dependencies'] = matches

        # Look for installation commands
        command_pattern = r'```bash\n(.*?)(?=```|```$)'
        matches = re.findall(command_pattern, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split('\n')
            install['commands'].extend([line.strip() for line in lines if line.strip()])

        return install

    def _extract_configuration(self, content: str) -> Dict:
        """Extract configuration requirements"""
        config = {
            'env_vars': [],
            'databases': [],
            'services': []
        }

        # Look for environment variable patterns
        env_pattern = r'([A-Z_]+)\s*[:=]\s*(\S+)'
        matches = re.findall(env_pattern, content)
        config['env_vars'] = [var for var, _ in matches]

        # Look for database mentions
        databases = ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlite']
        for db in databases:
            if db.lower() in content.lower():
                config['databases'].append(db)

        return config

    def analyze_code_structure(self) -> Dict[str, Any]:
        """Analyze actual code implementation"""
        code_info = {
            'modules': [],
            'api_endpoints': [],
            'imports': set(),
            'config_usage': [],
            'frameworks': []
        }

        # Scan Python files
        for py_file in self.project_root.rglob('*.py'):
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse AST
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, py_file, code_info)
                except SyntaxError:
                    pass

                # Look for API endpoints
                code_info['api_endpoints'].extend(self._find_api_endpoints(content, str(py_file)))

                # Extract imports
                code_info['imports'].update(self._extract_imports(content))

                # Find config usage
                code_info['config_usage'].extend(self._find_config_usage(content))

            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        # Convert imports set to list
        code_info['imports'] = list(code_info['imports'])

        return code_info

    def _analyze_ast(self, tree: ast.AST, file_path: Path, code_info: Dict):
        """Analyze Python AST for structure"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                code_info['modules'].append({
                    'type': 'class',
                    'name': node.name,
                    'file': str(file_path.relative_to(self.project_root))
                })
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    code_info['modules'].append({
                        'type': 'function',
                        'name': node.name,
                        'file': str(file_path.relative_to(self.project_root))
                    })

    def _find_api_endpoints(self, content: str, file_path: str) -> List[Dict]:
        """Find API endpoints in code"""
        endpoints = []

        # Look for Flask routes
        flask_pattern = r'@app\.(?:route|get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(flask_pattern, content)
        for path in matches:
            endpoints.append({
                'path': path,
                'file': file_path,
                'framework': 'Flask'
            })

        # Look for FastAPI endpoints
        fastapi_pattern = r'@(?:app|router)\.(?:get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(fastapi_pattern, content)
        for path in matches:
            endpoints.append({
                'path': path,
                'file': file_path,
                'framework': 'FastAPI'
            })

        return endpoints

    def _extract_imports(self, content: str) -> List[str]:
        """Extract all imports from code"""
        imports = []

        # Regular imports
        import_pattern = r'^import\s+([^\s\n]+)'
        matches = re.findall(import_pattern, content, re.MULTILINE)
        imports.extend(matches)

        # From imports
        from_pattern = r'^from\s+([^\s]+)\s+import'
        matches = re.findall(from_pattern, content, re.MULTILINE)
        imports.extend(matches)

        return imports

    def _find_config_usage(self, content: str) -> List[str]:
        """Find configuration variable usage"""
        config_usage = []

        # Look for os.environ.get
        env_pattern = r'os\.environ\.get\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(env_pattern, content)
        config_usage.extend(matches)

        # Look for os.getenv
        getenv_pattern = r'os\.getenv\([\'"]([^\'"]+)[\'"]'
        matches = re.findall(getenv_pattern, content)
        config_usage.extend(matches)

        return config_usage

    def compare_docs_vs_code(self, docs_info: Dict, code_info: Dict) -> List[ReviewResult]:
        """Compare documentation with actual code"""
        results = []

        # Compare API endpoints
        doc_endpoints = {ep['path'] for ep in docs_info['api_endpoints']}
        code_endpoints = {ep['path'] for ep in code_info['api_endpoints']}

        # Documented but not implemented
        for endpoint in doc_endpoints - code_endpoints:
            results.append(ReviewResult(
                category='Documentation',
                severity='high',
                description=f'API endpoint {endpoint} documented but not found in code',
                recommendation='Implement the endpoint or update documentation'
            ))

        # Implemented but not documented
        for endpoint in code_endpoints - doc_endpoints:
            results.append(ReviewResult(
                category='Documentation',
                severity='medium',
                description=f'API endpoint {endpoint} implemented but not documented',
                file_path=next((ep['file'] for ep in code_info['api_endpoints'] if ep['path'] == endpoint), None),
                recommendation='Add documentation for this endpoint'
            ))

        # Compare architecture
        if docs_info['architecture']['modules']:
            doc_modules = set(docs_info['architecture']['modules'])
            code_modules = {m['name'] for m in code_info['modules'] if m['type'] == 'class'}

            for module in doc_modules - code_modules:
                results.append(ReviewResult(
                    category='Architecture',
                    severity='medium',
                    description=f'Module {module} documented but not found in code',
                    recommendation='Implement the module or update architecture docs'
                ))

        return results


class ConfigValidator:
    """Validates configuration consistency"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def validate_requirements(self) -> List[ReviewResult]:
        """Check requirements.txt vs actual imports"""
        results = []

        # Read requirements.txt if exists
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            return results

        with open(req_file, 'r') as f:
            required_deps = set()
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    dep = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    required_deps.add(dep.lower())

        # Get all imports from code
        code_imports = set()
        for py_file in self.project_root.rglob('*.py'):
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract imports
                imports = re.findall(r'^import\s+([^\s\n]+)', content, re.MULTILINE)
                from_imports = re.findall(r'^from\s+([^\s]+)\s+import', content, re.MULTILINE)

                for imp in imports:
                    parts = imp.split('.')
                    if parts[0] and parts[0] != 'os' and parts[0] != 'sys':
                        code_imports.add(parts[0].lower())

                for imp in from_imports:
                    parts = imp.split('.')
                    if parts[0] and parts[0] != 'os' and parts[0] != 'sys':
                        code_imports.add(parts[0].lower())

            except Exception:
                pass

        # Check for unused dependencies
        for dep in required_deps - code_imports:
            results.append(ReviewResult(
                category='Configuration',
                severity='medium',
                description=f'Dependency {dep} listed in requirements.txt but not used in code',
                file_path='requirements.txt',
                recommendation='Remove unused dependency or verify it\'s needed'
            ))

        # Check for missing dependencies
        for imp in code_imports - required_deps:
            # Skip standard library modules
            if imp not in ['os', 'sys', 'json', 'datetime', 're', 'pathlib', 'typing', 'ast']:
                results.append(ReviewResult(
                    category='Configuration',
                    severity='high',
                    description=f'Package {imp} used in code but not in requirements.txt',
                    recommendation='Add to requirements.txt with appropriate version'
                ))

        return results

    def validate_env_file(self) -> List[ReviewResult]:
        """Check .env.example vs actual usage"""
        results = []

        # Read .env.example if exists
        env_example = self.project_root / '.env.example'
        if not env_example.exists():
            return results

        with open(env_example, 'r') as f:
            example_vars = set()
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var = line.split('=')[0].strip()
                    example_vars.add(var)

        # Get all env variable usage in code
        used_vars = set()
        for py_file in self.project_root.rglob('*.py'):
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find os.environ.get usage
                vars = re.findall(r'os\.environ\.get\([\'"]([^\'"]+)[\'"]', content)
                used_vars.update(vars)

                # Find os.getenv usage
                vars = re.findall(r'os\.getenv\([\'"]([^\'"]+)[\'"]', content)
                used_vars.update(vars)

            except Exception:
                pass

        # Check for unused env vars
        for var in example_vars - used_vars:
            results.append(ReviewResult(
                category='Configuration',
                severity='low',
                description=f'Environment variable {var} defined but not used in code',
                file_path='.env.example',
                recommendation='Remove if not needed or add usage'
            ))

        # Check for missing env vars
        for var in used_vars - example_vars:
            results.append(ReviewResult(
                category='Configuration',
                severity='high',
                description=f'Environment variable {var} used in code but not defined in .env.example',
                recommendation='Add to .env.example with description'
            ))

        return results


class TaskTracker:
    """Validates tasks_*.md against project state"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def find_tasks_file(self) -> Optional[Path]:
        """Find the most recent tasks_*.md file"""
        tasks_files = list(self.project_root.glob('tasks_*.md'))
        if tasks_files:
            # Sort by date in filename
            tasks_files.sort(key=lambda x: x.name, reverse=True)
            return tasks_files[0]
        return None

    def validate_tasks(self, tasks_file: Path) -> List[ReviewResult]:
        """Validate tasks against actual project state"""
        results = []

        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract completed tasks
        completed_tasks = []
        pending_tasks = []

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                current_section = line
            elif line.startswith('- [x]') or line.startswith('- [✓]'):
                completed_tasks.append(line)
            elif line.startswith('- [ ]') or line.startswith('- [o]'):
                pending_tasks.append(line)

        # Check completed tasks against actual implementation
        for task in completed_tasks:
            task_lower = task.lower()

            # Look for implementation evidence
            implemented = False
            if 'test' in task_lower:
                # Check if tests exist
                if any(self.project_root.rglob('test_*.py')) or any(self.project_root.rglob('*_test.py')):
                    implemented = True
            elif 'api' in task_lower:
                # Check if API endpoints exist
                for py_file in self.project_root.rglob('*.py'):
                    if '@app.' in py_file.read_text() or '@router.' in py_file.read_text():
                        implemented = True
                        break
            elif 'model' in task_lower or 'database' in task_lower:
                # Check if models exist
                for py_file in self.project_root.rglob('*.py'):
                    if 'class Model' in py_file.read_text() or 'SQLAlchemy' in py_file.read_text():
                        implemented = True
                        break

            if not implemented:
                results.append(ReviewResult(
                    category='Tasks',
                    severity='medium',
                    description=f'Task marked complete but implementation not found: {task}',
                    file_path=str(tasks_file),
                    recommendation='Verify task completion or update status'
                ))

        return results


class ReportGenerator:
    """Generates comprehensive review reports"""

    def __init__(self, project_root: str):
        self.project_root = project_root

    def generate_report(self, results: List[ReviewResult], docs_info: Dict, code_info: Dict) -> str:
        """Generate a comprehensive review report"""
        report_lines = []

        # Header
        report_lines.append(f"# Project Review Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Executive Summary
        report_lines.append("# Executive Summary")
        critical_count = len([r for r in results if r.severity == 'critical'])
        high_count = len([r for r in results if r.severity == 'high'])
        medium_count = len([r for r in results if r.severity == 'medium'])
        low_count = len([r for r in results if r.severity == 'low'])

        report_lines.append(f"Found {len(results)} issues: {critical_count} critical, {high_count} high, {medium_count} medium, {low_count} low")
        report_lines.append("")

        # Project Purpose
        report_lines.append("# A) Project Purpose")
        if docs_info.get('project_purpose'):
            report_lines.append(docs_info['project_purpose'])
        else:
            report_lines.append("Project purpose not clearly defined in documentation")
        report_lines.append("")

        # Current Implementation Status
        report_lines.append("# B) Current Implementation Status")
        report_lines.append(f"- Modules/Classes found: {len([m for m in code_info['modules'] if m['type'] == 'class'])}")
        report_lines.append(f"- Functions found: {len([m for m in code_info['modules'] if m['type'] == 'function'])}")
        report_lines.append(f"- API endpoints implemented: {len(code_info['api_endpoints'])}")
        report_lines.append(f"- Documentation files: {len(docs_info['files_found'])}")
        report_lines.append("")

        # Issues by Category
        report_lines.append("# C) Documentation vs Code Divergences")
        doc_issues = [r for r in results if r.category == 'Documentation']
        if doc_issues:
            for issue in sorted(doc_issues, key=lambda x: x.severity):
                report_lines.append(f"- **{issue.severity.upper()}**: {issue.description}")
                if issue.file_path:
                    report_lines.append(f"  - File: {issue.file_path}")
                if issue.recommendation:
                    report_lines.append(f"  - Recommendation: {issue.recommendation}")
                report_lines.append("")
        else:
            report_lines.append("No documentation issues found")
        report_lines.append("")

        # Configuration Analysis
        report_lines.append("# D) Configuration Analysis")
        config_issues = [r for r in results if r.category == 'Configuration']
        if config_issues:
            for issue in sorted(config_issues, key=lambda x: x.severity):
                report_lines.append(f"- **{issue.severity.upper()}**: {issue.description}")
                if issue.file_path:
                    report_lines.append(f"  - File: {issue.file_path}")
                if issue.recommendation:
                    report_lines.append(f"  - Recommendation: {issue.recommendation}")
                report_lines.append("")
        else:
            report_lines.append("No configuration issues found")
        report_lines.append("")

        # Tasks Compliance (if applicable)
        task_issues = [r for r in results if r.category == 'Tasks']
        if task_issues:
            report_lines.append("# E) Tasks Compliance")
            for issue in task_issues:
                report_lines.append(f"- **{issue.severity.upper()}**: {issue.description}")
                if issue.recommendation:
                    report_lines.append(f"  - Recommendation: {issue.recommendation}")
                report_lines.append("")

        # Recommendations
        report_lines.append("# Recommendations")
        report_lines.append("")

        # Prioritized recommendations
        critical_issues = [r for r in results if r.severity == 'critical']
        high_issues = [r for r in results if r.severity == 'high']

        if critical_issues:
            report_lines.append("## Immediate Action Required")
            for issue in critical_issues:
                if issue.recommendation:
                    report_lines.append(f"- {issue.recommendation}")
            report_lines.append("")

        if high_issues:
            report_lines.append("# High Priority")
            for issue in high_issues:
                if issue.recommendation:
                    report_lines.append(f"- {issue.recommendation}")
            report_lines.append("")

        # General recommendations
        report_lines.append("# General Improvements")
        report_lines.append("- Keep documentation updated with code changes")
        report_lines.append("- Run regular reviews to catch inconsistencies early")
        report_lines.append("- Use automated tools to validate dependencies")
        report_lines.append("- Consider adding pre-commit hooks for documentation checks")
        report_lines.append("")

        return '\n'.join(report_lines)

    def save_report(self, report: str, output_path: Optional[str] = None) -> str:
        """Save report to file"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.project_root, f'review_report_{timestamp}.md')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_path


def main():
    """Main audit handler entry point"""
    parser = argparse.ArgumentParser(description='Audit Handler - Comprehensive project analysis')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--scope', choices=['all', 'docs', 'code', 'config', 'tasks'], default='all',
                       help='Audit scope')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--format', choices=['md', 'json'], default='md', help='Output format')

    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)

    # Initialize analyzers
    doc_analyzer = DocumentationAnalyzer(project_root)
    config_validator = ConfigValidator(project_root)
    task_tracker = TaskTracker(project_root)
    report_generator = ReportGenerator(project_root)

    all_results = []
    docs_info = {}
    code_info = {}

    print("Starting comprehensive project audit...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}

        # Submit analysis tasks
        if args.scope in ['all', 'docs', 'code']:
            futures['docs'] = executor.submit(doc_analyzer.scan_documentation)
            futures['code'] = executor.submit(doc_analyzer.analyze_code_structure)

        if args.scope in ['all', 'config']:
            futures['requirements'] = executor.submit(config_validator.validate_requirements)
            futures['env'] = executor.submit(config_validator.validate_env_file)

        # Collect results
        for task, future in futures.items():
            try:
                result = future.result(timeout=60)
                if task == 'docs':
                    docs_info = result
                elif task == 'code':
                    code_info = result
                elif task == 'requirements':
                    all_results.extend(result)
                elif task == 'env':
                    all_results.extend(result)
            except Exception as e:
                print(f"Error in {task}: {e}")

    # Compare docs vs code
    if args.scope in ['all', 'docs', 'code'] and docs_info and code_info:
        comparison_results = doc_analyzer.compare_docs_vs_code(docs_info, code_info)
        all_results.extend(comparison_results)

    # Check tasks file
    if args.scope == 'all':
        tasks_file = task_tracker.find_tasks_file()
        if tasks_file:
            print(f"Found tasks file: {tasks_file}")
            task_results = task_tracker.validate_tasks(tasks_file)
            all_results.extend(task_results)

    # Generate report
    if args.format == 'md':
        report = report_generator.generate_report(all_results, docs_info, code_info)
        output_path = report_generator.save_report(report, args.output)
    else:
        # JSON format
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'results': [
                {
                    'category': r.category,
                    'severity': r.severity,
                    'description': r.description,
                    'file_path': r.file_path,
                    'line_number': r.line_number,
                    'recommendation': r.recommendation
                }
                for r in all_results
            ],
            'docs_info': docs_info,
            'code_info': code_info
        }

        if not args.output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f'review_report_{timestamp}.json'

        with open(args.output, 'w') as f:
            json.dump(json_data, f, indent=2)
        output_path = args.output

    print(f"\nAudit complete! Report saved to: {output_path}")
    print(f"\nSummary: {len(all_results)} issues found")
    for severity in ['critical', 'high', 'medium', 'low']:
        count = len([r for r in all_results if r.severity == severity])
        if count > 0:
            print(f"  {severity}: {count}")

    return 0


if __name__ == '__main__':
    sys.exit(main())