#!/usr/bin/env python3
"""
Review Integration Library - Wrapper functions for agent coordination
Integrates with the existing agent-system for comprehensive reviews
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests


class AgentCoordinator:
    """Coordinates review tasks with the agent-system"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agent_system_path = self.project_root / 'agent-system'
        self.config_path = self.agent_system_path / 'config'

    def spawn_review_agents(self, review_type: str = 'comprehensive') -> Dict[str, Any]:
        """Spawn multiple agents for parallel review analysis"""

        # Define agent tasks based on review type
        agent_tasks = {
            'documentation': {
                'task': 'Analyze all MD documentation files',
                'focus': ['README.md', 'docs/', 'api docs', 'architecture'],
                'output': 'documentation_analysis.json'
            },
            'code_structure': {
                'task': 'Analyze code structure and implementation',
                'focus': ['Python files', 'module structure', 'patterns'],
                'output': 'code_structure_analysis.json'
            },
            'configuration': {
                'task': 'Validate configuration consistency',
                'focus': ['requirements.txt', '.env', 'config files'],
                'output': 'configuration_analysis.json'
            },
            'api_validation': {
                'task': 'Validate API documentation vs implementation',
                'focus': ['endpoints', 'routes', 'API specs'],
                'output': 'api_validation.json'
            }
        }

        # Adjust tasks based on review type
        if review_type == 'quick':
            agent_tasks = {
                'documentation': agent_tasks['documentation'],
                'configuration': agent_tasks['configuration']
            }
        elif review_type == 'security':
            agent_tasks = {
                'security': {
                    'task': 'Perform security vulnerability analysis',
                    'focus': ['dependencies', 'auth mechanisms', 'input validation'],
                    'output': 'security_analysis.json'
                }
            }

        return agent_tasks

    def run_agent_task(self, task_name: str, task_config: Dict) -> Dict[str, Any]:
        """Run a single agent task"""

        # Prepare task command
        task_script = self.agent_system_path / 'scripts' / 'run_agent_task.py'

        if not task_script.exists():
            # Fallback to ai-agent.sh
            task_script = self.agent_system_path / 'ai-agent.sh'

        cmd = [
            str(task_script),
            '--task', task_config['task'],
            '--focus', ','.join(task_config['focus']),
            '--output', task_config['output'],
            '--project-root', str(self.project_root)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                # Try to load JSON output
                output_file = self.project_root / task_config['output']
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        return json.load(f)

            # Return stdout as fallback
            return {
                'agent': task_name,
                'status': 'completed',
                'output': result.stdout,
                'errors': result.stderr if result.stderr else None
            }

        except subprocess.TimeoutExpired:
            return {
                'agent': task_name,
                'status': 'timeout',
                'error': 'Task timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'agent': task_name,
                'status': 'error',
                'error': str(e)
            }

    def aggregate_results(self, agent_results: List[Dict]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""

        aggregated = {
            'summary': {
                'total_agents': len(agent_results),
                'successful_agents': 0,
                'failed_agents': 0,
                'issues_found': 0
            },
            'findings': [],
            'recommendations': []
        }

        for result in agent_results:
            if result.get('status') == 'completed':
                aggregated['summary']['successful_agents'] += 1

                # Extract findings
                if 'findings' in result:
                    aggregated['findings'].extend(result['findings'])
                    aggregated['summary']['issues_found'] += len(result['findings'])

                # Extract recommendations
                if 'recommendations' in result:
                    aggregated['recommendations'].extend(result['recommendations'])
            else:
                aggregated['summary']['failed_agents'] += 1
                aggregated['findings'].append({
                    'severity': 'high',
                    'category': 'Agent Error',
                    'description': f"Agent {result.get('agent', 'unknown')} failed: {result.get('error', 'Unknown error')}"
                })

        return aggregated

    def update_session_state(self, review_results: Dict[str, Any]):
        """Update session state with review results"""

        session_file = self.project_root / '.claude' / 'state' / 'session_state.json'

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except:
            session_data = {}

        # Add review results to session
        session_data['last_review'] = {
            'timestamp': datetime.now().isoformat(),
            'summary': review_results.get('summary', {}),
            'issues_count': len(review_results.get('findings', []))
        }

        # Add pending reviews if any
        if review_results.get('summary', {}).get('failed_agents', 0) > 0:
            if 'pending_reviews' not in session_data:
                session_data['pending_reviews'] = []
            session_data['pending_reviews'].append({
                'type': 'failed_agents',
                'timestamp': datetime.now().isoformat(),
                'details': review_results['summary']
            })

        # Save updated session
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)


class ReviewHooks:
    """Manages pre and post review hooks"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.hooks_dir = self.project_root / '.claude' / 'hooks'

    def trigger_pre_review_hooks(self, review_config: Dict) -> bool:
        """Trigger pre-review hooks"""

        pre_review_hook = self.hooks_dir / 'pre-review.py'

        if pre_review_hook.exists():
            try:
                cmd = ['python3', str(pre_review_hook), json.dumps(review_config)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
            except Exception as e:
                print(f"Pre-review hook failed: {e}")
                return False

        return True

    def trigger_post_review_hooks(self, review_results: Dict):
        """Trigger post-review hooks"""

        post_review_hook = self.hooks_dir / 'post-review.py'

        if post_review_hook.exists():
            try:
                cmd = ['python3', str(post_review_hook), json.dumps(review_results)]
                subprocess.run(cmd, capture_output=True, text=True)
            except Exception as e:
                print(f"Post-review hook failed: {e}")


class ReviewTemplates:
    """Manages review templates and output formats"""

    @staticmethod
    def get_markdown_template() -> str:
        """Get markdown report template"""
        return """# {title}

**Date:** {date}
**Review Type:** {review_type}
**Reviewers:** {reviewers}

# Executive Summary

{summary}

# Findings

{findings}

# Recommendations

{recommendations}

# Next Steps

{next_steps}
"""

    @staticmethod
    def format_finding(finding: Dict) -> str:
        """Format a single finding for markdown output"""
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵'
        }

        emoji = severity_emoji.get(finding.get('severity', 'low'), '🔵')

        formatted = f"{emoji} **{finding.get('severity', 'low').upper()}** - {finding.get('category', 'Unknown')}\n"
        formatted += f"   {finding.get('description', 'No description')}\n"

        if finding.get('file_path'):
            formatted += f"   *File:* `{finding.get('file_path')}`\n"

        if finding.get('line_number'):
            formatted += f"   *Line:* {finding.get('line_number')}\n"

        if finding.get('recommendation'):
            formatted += f"   *Recommendation:* {finding.get('recommendation')}\n"

        return formatted + "\n"

    @staticmethod
    def generate_html_summary(findings: List[Dict]) -> str:
        """Generate HTML summary of findings"""

        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for finding in findings:
            severity = finding.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        html = """
        <div class="review-summary">
            <h3>Issue Summary</h3>
            <div class="severity-stats">
                <span class="critical">🔴 Critical: {critical}</span>
                <span class="high">🟠 High: {high}</span>
                <span class="medium">🟡 Medium: {medium}</span>
                <span class="low">🔵 Low: {low}</span>
            </div>
        </div>
        """.format(**severity_counts)

        return html


def run_parallel_review(project_root: str, review_type: str = 'comprehensive') -> Dict[str, Any]:
    """Run a parallel review using multiple agents"""

    coordinator = AgentCoordinator(project_root)
    hooks = ReviewHooks(project_root)

    # Prepare review config
    review_config = {
        'type': review_type,
        'timestamp': datetime.now().isoformat(),
        'project_root': project_root
    }

    # Trigger pre-review hooks
    if not hooks.trigger_pre_review_hooks(review_config):
        print("Pre-review hooks failed, proceeding anyway...")

    # Spawn agent tasks
    agent_tasks = coordinator.spawn_review_agents(review_type)

    # Run agents in parallel
    agent_results = []
    for task_name, task_config in agent_tasks.items():
        print(f"Starting agent: {task_name}")
        result = coordinator.run_agent_task(task_name, task_config)
        agent_results.append(result)
        print(f"Agent {task_name} completed")

    # Aggregate results
    aggregated = coordinator.aggregate_results(agent_results)

    # Update session state
    coordinator.update_session_state(aggregated)

    # Trigger post-review hooks
    hooks.trigger_post_review_hooks(aggregated)

    return aggregated


def generate_review_report(aggregated_results: Dict, project_root: str,
                          output_format: str = 'md') -> str:
    """Generate a final review report from aggregated results"""

    templates = ReviewTemplates()

    if output_format == 'md':
        # Generate markdown report
        title = f"Comprehensive Project Review - {datetime.now().strftime('%Y-%m-%d')}"
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        review_type = aggregated_results.get('review_type', 'comprehensive')
        reviewers = "Automated Review System"

        # Summary
        summary = f"""This review analyzed the project using {aggregated_results['summary']['total_agents']} automated agents.
- Successful analyses: {aggregated_results['summary']['successful_agents']}
- Issues identified: {aggregated_results['summary']['issues_found']}
"""

        # Findings
        findings_sections = ""
        if aggregated_results.get('findings'):
            findings_sections = "\n".join([
                templates.format_finding(f)
                for f in aggregated_results['findings']
            ])
        else:
            findings_sections = "No issues found. Great job!"

        # Recommendations
        recommendations = "\n".join([
            f"- {rec}" for rec in aggregated_results.get('recommendations', [])
        ])

        # Next steps
        next_steps = """
1. Review critical and high severity issues
2. Create tickets for necessary fixes
3. Update documentation where needed
4. Schedule follow-up review
"""

        report = templates.get_markdown_template().format(
            title=title,
            date=date,
            review_type=review_type,
            reviewers=reviewers,
            summary=summary,
            findings=findings_sections,
            recommendations=recommendations,
            next_steps=next_steps
        )

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = Path(project_root) / f'review_report_{timestamp}.md'
        with open(report_path, 'w') as f:
            f.write(report)

        return str(report_path)

    else:
        # JSON format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = Path(project_root) / f'review_report_{timestamp}.json'

        with open(report_path, 'w') as f:
            json.dump(aggregated_results, f, indent=2)

        return str(report_path)


if __name__ == '__main__':
    # Example usage
    import sys

    project_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    review_type = sys.argv[2] if len(sys.argv) > 2 else 'comprehensive'

    print(f"Starting {review_type} review of {project_root}")

    # Run parallel review
    results = run_parallel_review(project_root, review_type)

    # Generate report
    report_path = generate_review_report(results, project_root)

    print(f"Review complete! Report saved to: {report_path}")