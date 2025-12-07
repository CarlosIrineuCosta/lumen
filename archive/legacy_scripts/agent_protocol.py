#!/usr/bin/env python3
"""
Agent Communication Protocol - JSON-first structured responses
Run directly in Claude Code, no WSL required
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentRole(Enum):
    """Define agent roles in the system"""
    CLAUDE = "claude-code"
    GEMINI = "gemini-cli"
    CODEX = "codex-cli"
    HUMAN = "human"

class MessageType(Enum):
    """Types of messages agents can exchange"""
    TASK = "task"
    VERIFICATION = "verification"
    REVIEW = "review"
    COMPLETION = "completion"
    ERROR = "error"
    STATUS = "status"
    PLAN = "plan"

class AgentProtocol:
    """Main protocol handler for agent communication"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.postbox_dir = self.project_root / ".postbox"
        self.agents_dir = self.project_root / ".agents"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.postbox_dir.mkdir(exist_ok=True)
        self.agents_dir.mkdir(exist_ok=True)
        (self.agents_dir / "messages").mkdir(exist_ok=True)
        
    def create_message(self, 
                      from_agent: AgentRole,
                      to_agent: AgentRole,
                      message_type: MessageType,
                      content: Dict[str, Any]) -> Dict:
        """Create a structured message between agents"""
        
        message = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "timestamp": datetime.now().isoformat(),
            "from": from_agent.value,
            "to": to_agent.value,
            "type": message_type.value,
            "content": content,
            "status": "pending"
        }
        
        # Save message to file
        message_file = self.agents_dir / "messages" / f"{message['id']}.json"
        with open(message_file, 'w') as f:
            json.dump(message, f, indent=2)
            
        return message
    
    def create_verification_request(self, files: List[str]) -> Dict:
        """Create a verification request for changed files"""
        
        verification = {
            "files": files,
            "timestamp": datetime.now().isoformat(),
            "checks": ["syntax", "style", "security", "performance"],
            "results": {}
        }
        
        msg = self.create_message(
            from_agent=AgentRole.CLAUDE,
            to_agent=AgentRole.GEMINI,
            message_type=MessageType.VERIFICATION,
            content=verification
        )
        
        # Add to postbox for visibility
        with open(self.postbox_dir / "todo.md", 'a') as f:
            f.write(f"\n- [ ] Verify files: {', '.join(files)}\n")
        
        return msg
    
    def generate_summary(self) -> Dict:
        """Generate a summary of current project status"""
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {
                "open": 0,
                "in_progress": 0,
                "completed": 0
            },
            "recent_files": [],
            "issues": []
        }
        
        # Count tasks from todo.md
        todo_file = self.postbox_dir / "todo.md"
        if todo_file.exists():
            with open(todo_file, 'r') as f:
                content = f.read()
                summary["tasks"]["open"] = content.count("- [ ]")
                summary["tasks"]["in_progress"] = content.count("- [~]")
        
        # Count completed from completed.md
        completed_file = self.postbox_dir / "completed.md"
        if completed_file.exists():
            with open(completed_file, 'r') as f:
                content = f.read()
                summary["tasks"]["completed"] = content.count("- [x]")
        
        # Get recent messages
        messages_dir = self.agents_dir / "messages"
        if messages_dir.exists():
            messages = sorted(messages_dir.glob("*.json"), 
                            key=lambda x: x.stat().st_mtime, 
                            reverse=True)[:5]
            
            for msg_file in messages:
                try:
                    with open(msg_file, 'r') as f:
                        msg = json.load(f)
                        if msg.get("type") == "verification":
                            summary["recent_files"].extend(msg["content"].get("files", []))
                except:
                    pass
        
        return summary

def main():
    """CLI interface for the protocol"""
    
    if len(sys.argv) < 2:
        print("Usage: agent_protocol.py <command> [options]")
        print("Commands:")
        print("  verify <file1> [file2...] - Request verification")
        print("  summary - Generate project summary")
        print("  init - Initialize directory structure")
        sys.exit(1)
    
    protocol = AgentProtocol()
    command = sys.argv[1]
    
    if command == "init":
        print("Initializing agent structure...")
        protocol.ensure_directories()
        
        # Create postbox files if they don't exist
        for filename in ["todo.md", "completed.md", "issues.md"]:
            filepath = protocol.postbox_dir / filename
            if not filepath.exists():
                filepath.touch()
                print(f"Created: {filepath}")
        
        print("✓ Agent structure initialized")
    
    elif command == "verify":
        if len(sys.argv) < 3:
            print("Usage: agent_protocol.py verify <file1> [file2...]")
            sys.exit(1)
        
        files = sys.argv[2:]
        result = protocol.create_verification_request(files)
        print(json.dumps(result, indent=2))
        print(f"\n✓ Verification request created for {len(files)} files")
    
    elif command == "summary":
        result = protocol.generate_summary()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()