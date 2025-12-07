#!/usr/bin/env python3
"""
Process Agent Proposals - Helper for Claude Code
Reads all proposals and formats them for easy review
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
COORDINATED_DIR = PROJECT_ROOT / ".agents" / "coordinated"


def read_proposal(proposal_file):
    """Read and parse proposal JSON"""
    with open(proposal_file, 'r') as f:
        return json.load(f)


def format_proposal_summary(proposal):
    """Format proposal for human review"""
    task_id = proposal.get("task_id", "unknown")
    completed = proposal.get("completed_at", "")
    safe = proposal.get("safe_changes", [])
    risky = proposal.get("risky_changes", [])
    conflicts = proposal.get("conflicts", [])

    summary = []
    summary.append(f"\n## Proposal {task_id}")
    summary.append(f"Completed: {completed}")
    summary.append(f"Total tasks: {proposal.get('total_tasks', 0)}")

    if conflicts:
        summary.append(f"\n### CONFLICTS DETECTED: {len(conflicts)}")
        for conflict in conflicts:
            summary.append(f"  - File: {conflict['file']}")
            summary.append(f"    Tasks: {conflict['tasks']}")

    if safe:
        summary.append(f"\n### Safe Changes (auto-apply):")
        for change in safe:
            summary.append(f"  - [{change['type']}] {change['description']}")
            summary.append(f"    Files: {', '.join(change['files'])}")
            summary.append(f"    Output: {change['output']}")

    if risky:
        summary.append(f"\n### Risky Changes (need approval):")
        for change in risky:
            summary.append(f"  - [{change['type']}] {change['description']}")
            summary.append(f"    Files: {', '.join(change['files'])}")
            summary.append(f"    Output: {change['output']}")

    summary.append(f"\nOutput directory: {proposal.get('output_dir', '')}")

    return "\n".join(summary)


def list_proposals(since_timestamp=None):
    """List all proposals, optionally filtered by timestamp"""
    if not COORDINATED_DIR.exists():
        print("No proposals directory found")
        return []

    proposals = list(COORDINATED_DIR.glob("proposal_*.json"))

    if since_timestamp:
        # Filter by timestamp
        proposals = [p for p in proposals if p.stem.split('_', 1)[1] >= since_timestamp]

    # Sort by timestamp (newest first)
    proposals.sort(reverse=True)

    return proposals


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            # List all proposals
            proposals = list_proposals()
            print(f"\nFound {len(proposals)} proposals:\n")
            for p in proposals[:10]:  # Show last 10
                print(f"  - {p.name}")

        elif command == "summary":
            # Show summary of all proposals
            since = sys.argv[2] if len(sys.argv) > 2 else None
            proposals = list_proposals(since)

            print(f"\n{'='*60}")
            print(f"  AGENT PROPOSALS SUMMARY")
            print(f"{'='*60}")

            for proposal_file in proposals:
                proposal = read_proposal(proposal_file)
                print(format_proposal_summary(proposal))
                print(f"\n{'-'*60}")

        elif command == "show":
            # Show specific proposal
            if len(sys.argv) < 3:
                print("Usage: process_proposals.py show <task_id>")
                sys.exit(1)

            task_id = sys.argv[2]
            proposal_file = COORDINATED_DIR / f"proposal_{task_id}.json"

            if not proposal_file.exists():
                print(f"Proposal not found: {proposal_file}")
                sys.exit(1)

            proposal = read_proposal(proposal_file)
            print(format_proposal_summary(proposal))

            # Also show the actual review content
            for change in proposal.get("risky_changes", []) + proposal.get("safe_changes", []):
                output_file = Path(change["output"])
                if output_file.exists():
                    print(f"\n{'='*60}")
                    print(f"Content: {output_file}")
                    print(f"{'='*60}\n")
                    with open(output_file, 'r') as f:
                        print(f.read())

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    else:
        print_usage()


def print_usage():
    print("""
Agent Proposal Processor

Usage:
  process_proposals.py list                    - List all proposals
  process_proposals.py summary [timestamp]     - Show summary of proposals
  process_proposals.py show <task_id>         - Show specific proposal with content

Examples:
  process_proposals.py list
  process_proposals.py summary 20251001
  process_proposals.py show 20251001_001309
""")


if __name__ == "__main__":
    main()
