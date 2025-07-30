"""Claude sessions module for listing and filtering conversation sessions."""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table


class Session:
    """Represents a Claude conversation session."""

    def __init__(
        self,
        session_id: str,
        project_name: str | None = None,
        last_activity: datetime | None = None,
    ):
        self.session_id = session_id
        self.project_name = project_name or "Unknown"
        self.last_activity = last_activity
        self.message_count = 0

    def update_activity(self, timestamp: datetime) -> None:
        """Update the last activity timestamp if newer."""
        if self.last_activity is None or timestamp > self.last_activity:
            self.last_activity = timestamp
        self.message_count += 1

    @property
    def last_activity_str(self) -> str:
        """Format last activity as readable string."""
        if self.last_activity is None:
            return "Unknown"
        return self.last_activity.strftime("%Y-%m-%d %H:%M:%S")


def extract_project_name_from_path(path: str | None) -> str | None:
    """Extract project name from file path or working directory."""
    if not path:
        return None

    try:
        path_obj = Path(path)
    except (OSError, ValueError):
        # Handle cases where path is too long or invalid
        return None

    # Look for common project indicators
    # Check if it's a git repo or has obvious project structure
    try:
        parts = path_obj.parts
    except (OSError, ValueError):
        return None

    # Try to find the project root by looking for git directories
    for i in range(len(parts) - 1, -1, -1):
        try:
            potential_root = Path(*parts[: i + 1])
            if (potential_root / ".git").exists():
                return potential_root.name
        except (OSError, ValueError):
            # Skip if path is too long or invalid
            continue

    # Otherwise, try to guess from path structure
    # Skip common parent directories
    skip_dirs = {"home", "Users", "projects", "workspace", "code", "repos", "src"}

    for part in reversed(parts):
        if part not in skip_dirs and not part.startswith("."):
            return part

    return None


def load_sessions(project_filter: str | None = None, days: int | None = None) -> list[Session]:
    """Load all sessions from Claude JSONL files.

    Args:
        project_filter: Filter sessions by project name
        days: Only include sessions from the last N days
    """
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return []

    # Calculate cutoff date if days is specified
    cutoff_date = None
    if days is not None:
        cutoff_date = datetime.now() - timedelta(days=days)

    sessions = {}
    jsonl_files = list(claude_dir.rglob("*.jsonl"))

    for file_path in jsonl_files:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract session/conversation ID
                # Try different possible field names
                session_id = None
                if "conversationId" in data:
                    session_id = data["conversationId"]
                elif "sessionId" in data:
                    session_id = data["sessionId"]
                elif "conversation_id" in data:
                    session_id = data["conversation_id"]
                elif "session_id" in data:
                    session_id = data["session_id"]
                elif "message" in data and "conversationId" in data["message"]:
                    session_id = data["message"]["conversationId"]
                elif "message" in data and "conversation_id" in data["message"]:
                    session_id = data["message"]["conversation_id"]

                if not session_id:
                    continue

                # Extract timestamp
                timestamp = None
                if "timestamp" in data:
                    try:
                        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                    except ValueError:
                        continue

                # Extract project name from various possible sources
                project_name = None

                # Try to get from explicit project field
                if "project" in data:
                    project_name = data["project"]
                elif "projectName" in data:
                    project_name = data["projectName"]
                elif "project_name" in data:
                    project_name = data["project_name"]

                # Try to extract from file paths in the conversation
                if not project_name and "message" in data:
                    message = data["message"]
                    # Check for file paths in content
                    if "content" in message:
                        content = message["content"]

                        # Handle list content (e.g., tool results)
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and "content" in item:
                                    content = str(item["content"])
                                    break
                            else:
                                content = str(content)
                        else:
                            content = str(content)

                        # Look for file paths
                        if "/" in content:
                            # First split by newlines to handle multi-line file lists
                            lines = content.split("\n")
                            for line in lines:
                                # Skip lines that are too long (likely not real paths)
                                if len(line) > 500:
                                    continue
                                # Then split by spaces within each line
                                words = line.split()
                                for word in words:
                                    # Basic heuristics for file paths
                                    if "/" in word and 5 < len(word) < 300:
                                        # Clean up the word (remove trailing punctuation)
                                        word = word.rstrip(",.;:!?\"')}]")
                                        extracted = extract_project_name_from_path(word)
                                        if extracted:
                                            project_name = extracted
                                            break
                                if project_name:
                                    break

                # Try to get from working directory or context
                if not project_name and "workingDirectory" in data:
                    project_name = extract_project_name_from_path(data["workingDirectory"])
                elif not project_name and "working_directory" in data:
                    project_name = extract_project_name_from_path(data["working_directory"])
                elif not project_name and "cwd" in data:
                    project_name = extract_project_name_from_path(data["cwd"])

                # Update or create session
                if session_id not in sessions:
                    sessions[session_id] = Session(session_id, project_name)
                else:
                    # Update project name if we found one and didn't have one before
                    if project_name and sessions[session_id].project_name == "Unknown":
                        sessions[session_id].project_name = project_name

                # Update activity
                if timestamp:
                    # Skip if before cutoff date
                    if cutoff_date and timestamp < cutoff_date:
                        continue
                    sessions[session_id].update_activity(timestamp)

    # Filter by project if specified
    session_list = list(sessions.values())
    if project_filter:
        project_filter_lower = project_filter.lower()
        session_list = [s for s in session_list if project_filter_lower in s.project_name.lower()]

    # Sort by last activity (newest first)
    session_list.sort(key=lambda s: s.last_activity or datetime.min, reverse=True)

    return session_list


def get_current_project_name() -> str | None:
    """Get the project name from current directory."""
    try:
        # Try to get from git repository
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
        return Path(repo_root).name
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo, try current directory name
        cwd = Path.cwd()
        return extract_project_name_from_path(str(cwd))


def display_sessions(
    console: Console, project_name: str | None = None, limit: int = 10, days: int | None = None
) -> None:
    """Display sessions in a formatted table.

    Args:
        console: Rich console for output
        project_name: Filter sessions by project name
        limit: Maximum number of sessions to display
        days: Only show sessions from the last N days
    """
    # If no project name specified, try to get from current directory
    if project_name is None:
        current_project = get_current_project_name()
        if current_project:
            console.print(f"[cyan]Searching for sessions in project: {current_project}[/cyan]")
            project_name = current_project

    # Load sessions
    sessions = load_sessions(project_filter=project_name, days=days)

    if not sessions:
        if project_name:
            console.print(f"[yellow]No sessions found for project '{project_name}'[/yellow]")
        else:
            console.print("[yellow]No Claude sessions found[/yellow]")
        return

    # Limit to requested number
    sessions = sessions[:limit][::-1]

    # Create table
    title = "Claude Sessions"
    if project_name:
        title += f" for '{project_name}'"
    if days:
        title += f" (Last {days} days)"
    title += f" - Most Recent {len(sessions)}"

    table = Table(title=title)
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Project", style="magenta")
    table.add_column("Last Activity", style="green")
    table.add_column("Messages", justify="right")

    for session in sessions:
        table.add_row(
            session.session_id,
            session.project_name,
            session.last_activity_str,
            str(session.message_count),
        )

    console.print(table)
