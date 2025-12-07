#!/usr/bin/env python3
"""
Parallel Agent Coordinator - Orchestrates multiple GLM agents
Manages task delegation, conflict detection, and result coordination
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = PROJECT_ROOT / ".agents"
QUEUE_DIR = AGENTS_DIR / "queue"
OUTPUT_DIR = AGENTS_DIR / "output"
COORDINATED_DIR = AGENTS_DIR / "coordinated"
GLM_WORKER = PROJECT_ROOT / "scripts" / "agents" / "glm_worker.py"


class TaskCoordinator:
    def __init__(self):
        self.task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = OUTPUT_DIR / self.task_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_request(self, request_text):
        """Parse user request into tasks

        Format: action "description" file1 file2 AND action "description" file3
        Example: review "security issues" auth.py AND test auth.py AND docs
        """
        tasks = []
        task_id = 1

        # Split by AND
        parts = request_text.split(" AND ")

        for part in parts:
            part = part.strip()
            words = part.split()

            if not words:
                continue

            task_type = words[0].lower()

            # Extract description (quoted) and files
            description = ""
            files = []
            in_quotes = False
            quote_content = []

            for word in words[1:]:
                if word.startswith('"'):
                    in_quotes = True
                    quote_content = [word[1:]]
                elif word.endswith('"'):
                    quote_content.append(word[:-1])
                    description = " ".join(quote_content)
                    in_quotes = False
                    quote_content = []
                elif in_quotes:
                    quote_content.append(word)
                else:
                    # It's a file
                    files.append(word)

            # If no explicit description, use task type
            if not description:
                description = f"{task_type} task"

            tasks.append({
                "id": task_id,
                "type": task_type,
                "description": description,
                "files": files
            })
            task_id += 1

        return tasks

    def create_manifest(self, tasks):
        """Create task manifest with file locks"""
        # Collect all files being worked on
        locked_files = set()
        for task in tasks:
            locked_files.update(task["files"])

        manifest = {
            "task_id": self.task_id,
            "created_at": datetime.now().isoformat(),
            "tasks": tasks,
            "locked_files": list(locked_files),
            "status": "running"
        }

        manifest_file = QUEUE_DIR / f"task_{self.task_id}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest_file

    def spawn_workers(self, tasks):
        """Spawn GLM workers in parallel"""
        processes = []

        for task in tasks:
            cmd = [
                sys.executable,
                str(GLM_WORKER),
                str(task["id"]),
                task["type"],
                str(self.output_dir),
                task["description"]
            ]
            cmd.extend(task["files"])

            # Spawn in background with nohup
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            processes.append({
                "task_id": task["id"],
                "type": task["type"],
                "proc": proc
            })

        return processes

    def wait_for_completion(self, tasks, timeout=300):
        """Wait for all tasks to complete"""
        start_time = time.time()

        while True:
            # Check if all tasks have .done markers
            all_done = True
            for task in tasks:
                marker_file = self.output_dir / f"{task['id']}.done"
                if not marker_file.exists():
                    all_done = False
                    break

            if all_done:
                return True

            # Check timeout
            if time.time() - start_time > timeout:
                return False

            time.sleep(2)

    def detect_conflicts(self, tasks):
        """Detect conflicts in task outputs"""
        file_edits = defaultdict(list)

        for task in tasks:
            for file_path in task["files"]:
                file_edits[file_path].append(task)

        conflicts = []
        for file_path, task_list in file_edits.items():
            # Conflict if multiple tasks want to edit same file
            if len(task_list) > 1:
                edit_tasks = [t for t in task_list if t["type"] in ["review"]]
                if len(edit_tasks) > 1:
                    conflicts.append({
                        "file": file_path,
                        "tasks": [t["id"] for t in edit_tasks]
                    })

        return conflicts

    def categorize_changes(self, tasks):
        """Categorize changes as safe or risky"""
        safe_changes = []
        risky_changes = []

        for task in tasks:
            output_file = self.output_dir / f"{task['id']}_{task['type']}.{'py' if task['type'] == 'test' else 'md'}"

            if not output_file.exists():
                continue

            change = {
                "task_id": task["id"],
                "type": task["type"],
                "description": task["description"],
                "files": task["files"],
                "output": str(output_file)
            }

            # Safe: tests, docs
            if task["type"] in ["test", "docs", "search"]:
                safe_changes.append(change)
            # Risky: code reviews (actual code changes)
            else:
                risky_changes.append(change)

        return safe_changes, risky_changes

    def generate_proposal(self, tasks, conflicts):
        """Generate unified proposal for Claude Code"""
        safe_changes, risky_changes = self.categorize_changes(tasks)

        proposal = {
            "task_id": self.task_id,
            "completed_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "safe_changes": safe_changes,
            "risky_changes": risky_changes,
            "conflicts": conflicts,
            "output_dir": str(self.output_dir)
        }

        proposal_file = COORDINATED_DIR / f"proposal_{self.task_id}.json"
        with open(proposal_file, 'w') as f:
            json.dump(proposal, f, indent=2)

        return proposal_file


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: parallel_coordinator.py <request>")
        print('Example: parallel_coordinator.py \'review "security" auth.py AND test auth.py\'')
        sys.exit(1)

    request_text = " ".join(sys.argv[1:])

    coordinator = TaskCoordinator()

    # Parse request
    tasks = coordinator.parse_request(request_text)
    if not tasks:
        print("ERROR: No valid tasks parsed from request")
        sys.exit(1)

    print(f"Parsed {len(tasks)} tasks:", file=sys.stderr)
    for task in tasks:
        print(f"  - Task {task['id']}: {task['type']} - {task['description']}", file=sys.stderr)

    # Create manifest
    manifest_file = coordinator.create_manifest(tasks)
    print(f"Created manifest: {manifest_file}", file=sys.stderr)

    # Spawn workers
    print("Spawning GLM workers...", file=sys.stderr)
    processes = coordinator.spawn_workers(tasks)

    # Wait for completion
    print("Waiting for completion (timeout: 5 minutes)...", file=sys.stderr)
    success = coordinator.wait_for_completion(tasks, timeout=300)

    if not success:
        print("ERROR: Timeout waiting for tasks to complete", file=sys.stderr)
        sys.exit(1)

    print("All tasks completed!", file=sys.stderr)

    # Detect conflicts
    conflicts = coordinator.detect_conflicts(tasks)
    if conflicts:
        print(f"WARNING: Detected {len(conflicts)} conflicts", file=sys.stderr)

    # Generate proposal
    proposal_file = coordinator.generate_proposal(tasks, conflicts)
    print(f"Generated proposal: {proposal_file}", file=sys.stderr)

    # Output proposal path for slash command to read
    print(str(proposal_file))

    return 0


if __name__ == "__main__":
    sys.exit(main())
