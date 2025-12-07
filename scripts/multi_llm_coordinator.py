#!/usr/bin/env python3
"""
Multi-LLM Coordinator - Routes tasks to appropriate LLMs based on content and context
Supports GLM, Codex, Gemini, and OpenCode
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Import wrappers
sys.path.insert(0, str(Path(__file__).parent))
try:
    from glm_worker import call_glm as call_glm_func
except ImportError:
    call_glm_func = None

try:
    from codex_wrapper import call_codex
except ImportError:
    call_codex = None

try:
    from gemini_wrapper import call_gemini
except ImportError:
    call_gemini = None

def analyze_task_requirements(task_description, context_files=None):
    """
    Analyze task to determine which LLM(s) should handle it
    """
    if context_files is None:
        context_files = []

    # Calculate context size
    total_size = 0
    for file_path in context_files:
        try:
            total_size += Path(file_path).stat().st_size
        except:
            pass

    # Convert to approximate tokens (1 token ≈ 4 characters)
    estimated_tokens = total_size // 4

    # Analyze task keywords
    task_lower = task_description.lower()

    # Decision matrix
    needs = {
        'glm': False,
        'codex': False,
        'gemini': False,
        'opencode': False
    }

    # GLM: Testing, documentation, implementation
    glm_keywords = ['test', 'testing', 'pytest', 'documentation', 'docs',
                   'implement', 'create component', 'refactor', 'quality assurance']
    needs['glm'] = any(kw in task_lower for kw in glm_keywords)

    # Codex: Security, performance, code review
    codex_keywords = ['security', 'review', 'audit', 'performance', 'optimize',
                     'vulnerability', 'backend', 'infrastructure']
    needs['codex'] = any(kw in task_lower for kw in codex_keywords)

    # Gemini: Large context (>100k tokens)
    needs['gemini'] = estimated_tokens > 100000

    # OpenCode: Additional analysis, backup
    opencode_keywords = ['analyze', 'research', 'investigate', 'explore']
    needs['opencode'] = any(kw in task_lower for kw in opencode_keywords)

    return needs, estimated_tokens

def route_and_execute(task_description, context_files=None, parallel=False):
    """
    Route task to appropriate LLMs and execute
    """
    needs, token_count = analyze_task_requirements(task_description, context_files)

    print(f"\n=== Task Analysis ===", file=sys.stderr)
    print(f"Description: {task_description[:100]}...", file=sys.stderr)
    print(f"Context files: {len(context_files) if context_files else 0}", file=sys.stderr)
    print(f"Estimated tokens: ~{token_count//1000}k", file=sys.stderr)
    print(f"LLM assignments:", file=sys.stderr)

    results = {}

    # Determine execution order
    execution_plan = []

    # Gemini first for large context (if needed)
    if needs['gemini']:
        execution_plan.append(('gemini', 'Large context analysis'))

    # Codex for security/review
    if needs['codex']:
        execution_plan.append(('codex', 'Security and performance review'))

    # GLM for implementation
    if needs['glm']:
        execution_plan.append(('glm', 'Implementation and testing'))

    # OpenCode for additional analysis
    if needs['opencode']:
        execution_plan.append(('opencode', 'Additional analysis'))

    # Execute plan
    for llm, purpose in execution_plan:
        print(f"  - {llm.upper()}: {purpose}", file=sys.stderr)

        if llm == 'glm' and call_glm_func:
            # GLM worker has different interface
            result = call_glm_func(task_description, context_files)
            results['glm'] = result

        elif llm == 'codex' and call_codex:
            result = call_codex(task_description, context_files)
            results['codex'] = result

        elif llm == 'gemini' and call_gemini:
            result = call_gemini(task_description, context_files)
            results['gemini'] = result

        elif llm == 'opencode':
            # OpenCode would be implemented similarly
            results['opencode'] = {
                'success': False,
                'error': 'OpenCode wrapper not yet implemented',
                'output': '',
                'command': 'opencode'
            }

        else:
            results[llm] = {
                'success': False,
                'error': f'{llm} wrapper not available',
                'output': '',
                'command': llm
            }

    return results

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python multi_llm_coordinator.py --task 'description' [--files file1.py,file2.js] [--parallel]")
        sys.exit(1)

    task = ""
    files = []
    parallel = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--task' and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--files' and i + 1 < len(sys.argv):
            files = sys.argv[i + 1].split(',')
            i += 2
        elif sys.argv[i] == '--parallel':
            parallel = True
            i += 1
        else:
            i += 1

    if not task:
        print("Error: --task is required")
        sys.exit(1)

    results = route_and_execute(task, files, parallel)

    # Print results
    print("\n=== Results ===")
    for llm, result in results.items():
        print(f"\n--- {llm.upper()} ---")
        if result['success']:
            print(result['output'])
        else:
            print(f"Error: {result['error']}")

    # Summary
    print("\n=== Summary ===")
    successful = sum(1 for r in results.values() if r['success'])
    print(f"Tasks completed: {successful}/{len(results)}")

if __name__ == '__main__':
    main()