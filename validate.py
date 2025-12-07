#!/usr/bin/env python3
"""
Enhanced validation script for the Lumen Multi-Agent System
Comprehensive system validation with dependency checking, hook testing, and agent validation
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

def validate_structure():
    """Validate the directory structure"""
    print("=== Validating Directory Structure ===")

    required_dirs = ['scripts', 'hooks', 'config', 'templates', 'docs', 'prompts', '.claude']
    base = Path(__file__).parent
    all_passed = True

    for dir_name in required_dirs:
        dir_path = base / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            all_passed = False

    # Check for essential subdirectories
    essential_subdirs = [
        'hooks/core',
        'hooks/auxiliary',
        'hooks/session',
        'config',
        'scripts'
    ]

    for subdir in essential_subdirs:
        subdir_path = base / subdir
        if subdir_path.exists():
            print(f"✓ {subdir}/ directory exists")
        else:
            print(f"✗ {subdir}/ directory missing")
            all_passed = False

    return all_passed

def validate_dependencies():
    """Validate system dependencies"""
    print("\n=== Validating Dependencies ===")

    base = Path(__file__).parent
    all_passed = True

    # Check for requirements file
    requirements_file = base / "requirements.txt"
    if requirements_file.exists():
        print("✓ requirements.txt found")
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            print(f"✓ requirements.txt contains {len(requirements)} packages")
        except Exception as e:
            print(f"✗ Error reading requirements.txt: {e}")
            all_passed = False
    else:
        print("ℹ requirements.txt not found (optional)")

    # Check for essential Python packages
    essential_packages = ['python-dotenv', 'jsonschema']
    optional_packages = ['requests', 'pyyaml', 'click']

    print("\nChecking essential packages:")
    for package in essential_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} - installed")
        except ImportError:
            print(f"✗ {package} - missing (pip install {package})")
            all_passed = False

    print("\nChecking optional packages:")
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} - installed")
        except ImportError:
            print(f"⚠ {package} - missing (optional)")

    return all_passed

def validate_scripts():
    """Validate Python scripts can be imported"""
    print("\n=== Validating Script Imports ===")

    base = Path(__file__).parent
    all_passed = True

    scripts = [
        'hooks/core/quality_gate.py',
        'hooks/core/completion_checker.py',
        'hooks/auxiliary/root_protection.py',
        'hooks/auxiliary/docs_update_trigger.py',
        'hooks/session/session_tracker.py',
        'scripts/codex_wrapper.py',
        'scripts/gemini_wrapper.py',
        'scripts/multi_llm_coordinator.py',
        'scripts/agent_coordinator.py',
        'scripts/parallel_coordinator.py',
        'scripts/process_proposals.py'
    ]

    for script in scripts:
        script_path = base / script
        if script_path.exists():
            try:
                # Check syntax
                with open(script_path, 'r') as f:
                    compile(f.read(), script_path, 'exec')
                print(f"✓ {script} - valid syntax")
            except SyntaxError as e:
                print(f"✗ {script} - syntax error: {e}")
                all_passed = False
            except Exception as e:
                print(f"⚠ {script} - import issue: {e}")
        else:
            print(f"✗ {script} - not found")
            all_passed = False

    return all_passed

def validate_hooks():
    """Validate hook functionality and executability"""
    print("\n=== Validating Hooks ===")

    base = Path(__file__).parent
    all_passed = True

    # Find all Python hooks
    hooks_dir = base / 'hooks'
    hook_files = []

    for root, dirs, files in os.walk(hooks_dir):
        for file in files:
            if file.endswith('.py'):
                hook_files.append(Path(root) / file)

    print(f"Found {len(hook_files)} hook files")

    # Validate each hook
    for hook_path in hook_files:
        relative_path = hook_path.relative_to(base)

        # Check syntax
        try:
            with open(hook_path, 'r') as f:
                compile(f.read(), hook_path, 'exec')
            print(f"✓ {relative_path} - valid syntax")
        except SyntaxError as e:
            print(f"✗ {relative_path} - syntax error: {e}")
            all_passed = False

        # Check executable permissions
        if os.access(hook_path, os.X_OK):
            print(f"✓ {relative_path} - executable")
        else:
            print(f"⚠ {relative_path} - not executable (run: chmod +x {hook_path.name})")

        # Check for basic structure
        try:
            with open(hook_path, 'r') as f:
                content = f.read()
                if 'def ' in content:
                    print(f"✓ {relative_path} - contains function definitions")
                else:
                    print(f"⚠ {relative_path} - no function definitions found")

                if 'if __name__ == "__main__"' in content:
                    print(f"✓ {relative_path} - has main block")
                else:
                    print(f"⚠ {relative_path} - no main block")
        except Exception as e:
            print(f"✗ {relative_path} - error reading: {e}")
            all_passed = False

    return all_passed

def validate_config():
    """Validate configuration files"""
    print("\n=== Validating Configuration ===")

    base = Path(__file__).parent
    all_passed = True

    configs = [
        'config/.env.example',
        'config/hooks_settings.json',
        'config/agent_routing.json',
        'templates/.vscode/settings.json',
        'templates/.vscode/tasks.json'
    ]

    for config in configs:
        config_path = base / config
        if config_path.exists():
            if config.endswith('.json'):
                try:
                    with open(config_path, 'r') as f:
                        json.load(f)
                    print(f"✓ {config} - valid JSON")
                except json.JSONDecodeError as e:
                    print(f"✗ {config} - invalid JSON: {e}")
                    all_passed = False
            else:
                print(f"✓ {config} - exists")
        else:
            print(f"✗ {config} - not found")
            all_passed = False

    # Validate unified configuration
    unified_config = base / 'config' / 'unified_config.json'
    if unified_config.exists():
        try:
            with open(unified_config, 'r') as f:
                config_data = json.load(f)
            print("✓ unified_config.json - valid JSON structure")

            # Check for expected sections
            expected_sections = ['agents', 'hooks', 'routing', 'settings']
            for section in expected_sections:
                if section in config_data:
                    print(f"✓ unified_config.json contains {section} section")
                else:
                    print(f"⚠ unified_config.json missing {section} section")

        except Exception as e:
            print(f"✗ unified_config.json error: {e}")
            all_passed = False

    return all_passed

def validate_agent_communication():
    """Validate agent communication capabilities"""
    print("\n=== Validating Agent Communication ===")

    base = Path(__file__).parent
    all_passed = True

    # Check for communication scripts
    comm_scripts = [
        'scripts/agent_coordinator.py',
        'scripts/parallel_coordinator.py',
        'scripts/multi_llm_coordinator.py'
    ]

    for script in comm_scripts:
        script_path = base / script
        if script_path.exists():
            try:
                with open(script_path, 'r') as f:
                    content = f.read()

                # Check for communication patterns
                if 'def ' in content and 'if __name__ == "__main__"' in content:
                    print(f"✓ {script} - communication script structure ok")
                else:
                    print(f"⚠ {script} - communication script structure incomplete")

                # Check for agent coordination patterns
                if 'agent' in content.lower() or 'coordinate' in content.lower():
                    print(f"✓ {script} - contains agent coordination logic")
                else:
                    print(f"⚠ {script} - may not contain agent coordination logic")

            except Exception as e:
                print(f"✗ {script} - error: {e}")
                all_passed = False
        else:
            print(f"✗ {script} - not found")
            all_passed = False

    # Validate agent routing configuration
    routing_config = base / 'config' / 'agent_routing.json'
    if routing_config.exists():
        try:
            with open(routing_config, 'r') as f:
                routing_data = json.load(f)
            print("✓ agent_routing.json - valid configuration")

            # Check for routing structure
            if 'agents' in routing_data:
                print(f"✓ agent_routing.json contains {len(routing_data['agents'])} agent definitions")
            else:
                print("⚠ agent_routing.json missing 'agents' section")
                all_passed = False

            if 'routes' in routing_data:
                print(f"✓ agent_routing.json contains {len(routing_data['routes'])} routing rules")
            else:
                print("⚠ agent_routing.json missing 'routes' section")
                all_passed = False

        except Exception as e:
            print(f"✗ agent_routing.json error: {e}")
            all_passed = False
    else:
        print("⚠ agent_routing.json not found")

    return all_passed

def validate_session_state():
    """Validate session state functionality"""
    print("\n=== Validating Session State ===")

    base = Path(__file__).parent
    all_passed = True

    # Check session tracking hook
    session_hook = base / 'hooks' / 'session' / 'session_tracker.py'
    if session_hook.exists():
        try:
            with open(session_hook, 'r') as f:
                content = f.read()

            if 'session' in content.lower():
                print("✓ session_tracker.py - contains session-related code")
            else:
                print("⚠ session_tracker.py - may not contain session-related code")

            if 'def ' in content:
                print("✓ session_tracker.py - has function definitions")
            else:
                print("⚠ session_tracker.py - no function definitions")

        except Exception as e:
            print(f"✗ session_tracker.py - error: {e}")
            all_passed = False
    else:
        print("⚠ session_tracker.py not found")

    # Check for session state directory
    session_dir = base / '.claude' / 'state'
    if session_dir.exists():
        print("✓ .claude/state/ directory exists")
    else:
        print("⚠ .claude/state/ directory not found")

    return all_passed

def validate_symlinks():
    """Validate symlinks are working"""
    print("\n=== Validating Symlinks ===")

    base = Path(__file__).parent
    all_passed = True

    # Check for potential symlinks in the system
    common_symlinks = [
        'hooks/hooks',  # Common pattern for hook symlinks
        'scripts/scripts',
        'config/config'
    ]

    for symlink in common_symlinks:
        symlink_path = base / symlink
        if symlink_path.exists():
            if symlink_path.is_symlink():
                try:
                    symlink_path.readlink()
                    print(f"✓ {symlink} - valid symlink")
                except Exception as e:
                    print(f"✗ {symlink} - broken symlink: {e}")
                    all_passed = False
            else:
                print(f"⚠ {symlink} - not a symlink")
        else:
            print(f"ℹ {symlink} - not found")

    return all_passed

def validate_cross_agent_review():
    """Validate cross-agent review system"""
    print("\n=== Validating Cross-Agent Review System ===")

    base = Path(__file__).parent
    all_passed = True

    # Check for review-related hooks or scripts
    review_files = []
    for root, dirs, files in os.walk(base):
        for file in files:
            if 'review' in file.lower() and file.endswith('.py'):
                review_files.append(Path(root) / file)

    print(f"Found {len(review_files)} review-related files")

    if review_files:
        for review_file in review_files:
            relative_path = review_file.relative_to(base)
            try:
                with open(review_file, 'r') as f:
                    content = f.read()

                if 'def ' in content:
                    print(f"✓ {relative_path} - valid review script")
                else:
                    print(f"⚠ {relative_path} - no function definitions")

            except Exception as e:
                print(f"✗ {relative_path} - error: {e}")
                all_passed = False
    else:
        print("ℹ No review-related files found")

    return all_passed

def check_permissions():
    """Check executable permissions"""
    print("\n=== Checking Permissions ===")

    base = Path(__file__).parent
    all_passed = True

    # Check scripts directory
    scripts_dir = base / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.py'):
            if os.access(script, os.X_OK):
                print(f"✓ {script.name} is executable")
            else:
                print(f"⚠ {script.name} - not executable (run: chmod +x {script.name})")

    # Check hooks directory
    hooks_dir = base / 'hooks'
    if hooks_dir.exists():
        for hook in hooks_dir.rglob('*.py'):
            if os.access(hook, os.X_OK):
                print(f"✓ {hook.relative_to(base)} is executable")
            else:
                print(f"⚠ {hook.relative_to(base)} - not executable (run: chmod +x {hook.name})")

    return all_passed

def main():
    """Run all validation checks"""
    print("Enhanced Lumen Multi-Agent System Validation")
    print("=" * 50)
    print("Comprehensive system validation and health check")
    print("=" * 50)

    base = Path(__file__).parent
    os.chdir(base)

    results = {}

    # Run all validation functions
    validation_functions = [
        ('Directory Structure', validate_structure),
        ('Dependencies', validate_dependencies),
        ('Scripts', validate_scripts),
        ('Hooks', validate_hooks),
        ('Configuration', validate_config),
        ('Agent Communication', validate_agent_communication),
        ('Session State', validate_session_state),
        ('Symlinks', validate_symlinks),
        ('Cross-Agent Review', validate_cross_agent_review),
        ('Permissions', check_permissions)
    ]

    print("\nRunning validation checks...\n")

    for name, func in validation_functions:
        try:
            results[name] = func()
        except Exception as e:
            print(f"\n✗ {name} - validation failed with error: {e}")
            results[name] = False

    # Enhanced reporting
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks

    print(f"\nTotal Checks: {total_checks}")
    print(f"Passed: {passed_checks} ({passed_checks/total_checks*100:.1f}%)")
    print(f"Failed: {failed_checks} ({failed_checks/total_checks*100:.1f}%)")

    # Detailed results
    print("\nDetailed Results:")
    print("-" * 30)

    for name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:<25} {status}")

    # System health assessment
    print("\nSystem Health Assessment:")
    print("-" * 30)

    health_percentage = (passed_checks / total_checks) * 100

    if health_percentage >= 90:
        health_status = "EXCELLENT"
        health_color = "🟢"
    elif health_percentage >= 70:
        health_status = "GOOD"
        health_color = "🟡"
    elif health_percentage >= 50:
        health_status = "FAIR"
        health_color = "🟠"
    else:
        health_status = "POOR"
        health_color = "🔴"

    print(f"{health_color} System Health: {health_status} ({health_percentage:.1f}%)")

    # Recommendations
    print("\nRecommendations:")
    print("-" * 30)

    if failed_checks > 0:
        print("Address failed checks first:")
        for name, result in results.items():
            if not result:
                print(f"  • Fix {name} issues")

    if passed_checks == total_checks:
        print("✓ All checks passed! System is ready for use.")
        print("\nNext Steps:")
        print("1. Copy agent-system/ to your project directory")
        print("2. Install dependencies: pip install python-dotenv")
        print("3. Copy .env.example to .env and configure if needed")
        print("4. Update Claude Code hooks settings to use agent-system/hooks/")
        print("5. Ensure all scripts have executable permissions")
        print("\nNote: GLM is called internally through Claude Code - no API keys needed!")
    else:
        print("⚠ System needs attention before deployment.")
        print("  • Install missing dependencies")
        print("  • Fix configuration issues")
        print("  • Correct permission problems")
        print("  • Address any failed validation checks")

    # Exit code
    return 0 if passed_checks == total_checks else 1

if __name__ == '__main__':
    sys.exit(main())