"""Claude usage statistics module."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


class ModelCosts:
    """Model token costs per million tokens."""

    # Default costs per million tokens
    DEFAULT_COSTS = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "claude-3-7-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "claude-3-5-haiku-20241022": {
            "input": 1.00,
            "output": 5.00,
            "cache_creation": 1.25,
            "cache_read": 0.10,
        },
        "claude-sonnet-4-20250514": {
            "input": 3.00,
            "output": 15.00,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "claude-opus-4-20250514": {
            "input": 15.00,
            "output": 75.00,
            "cache_creation": 18.75,
            "cache_read": 1.50,
        },
        # Default for unknown models (Sonnet)
        "default": {
            "input": 3.00,
            "output": 15.00,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
    }

    @classmethod
    def calculate_cost_from_tokens(cls, usage: dict[str, Any], model: str) -> float:
        """Calculate cost for a specific message's token usage."""
        model_costs = cls.DEFAULT_COSTS.get(model, cls.DEFAULT_COSTS["default"])

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
        cache_read_tokens = usage.get("cache_read_input_tokens", 0)

        cost = 0.0
        cost += (input_tokens / 1_000_000) * model_costs["input"]
        cost += (output_tokens / 1_000_000) * model_costs["output"]
        cost += (cache_creation_tokens / 1_000_000) * model_costs["cache_creation"]
        cost += (cache_read_tokens / 1_000_000) * model_costs["cache_read"]

        return cost


class UsageEntry:
    """Represents a single usage entry with cost calculation."""

    def __init__(self, data: dict[str, Any]):
        # Validate required fields
        if "timestamp" not in data:
            raise ValueError("Missing required field: timestamp")

        try:
            self.timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {e}") from e

        self.message = data.get("message", {})
        self.usage = self.message.get("usage", {})
        self.model = self.message.get("model", "unknown")
        self.message_id = self.message.get("id")
        self.request_id = data.get("requestId")
        self.cost_usd = data.get("costUSD")

        # Token counts
        self.input_tokens = self.usage.get("input_tokens", 0)
        self.output_tokens = self.usage.get("output_tokens", 0)
        self.cache_creation_tokens = self.usage.get("cache_creation_input_tokens", 0)
        self.cache_read_tokens = self.usage.get("cache_read_input_tokens", 0)

        # Calculate cost (auto mode: use costUSD if available, otherwise calculate)
        if self.cost_usd is not None:
            self.cost = self.cost_usd
        elif self.model and self.model != "unknown":
            self.cost = ModelCosts.calculate_cost_from_tokens(self.usage, self.model)
        else:
            self.cost = 0.0

    @property
    def unique_hash(self) -> str | None:
        """Create unique hash for deduplication."""
        if self.message_id and self.request_id:
            return f"{self.message_id}:{self.request_id}"
        return None

    @property
    def date_str(self) -> str:
        """Get date string in YYYY-MM-DD format."""
        return self.timestamp.strftime("%Y-%m-%d")


class DailyUsage:
    """Aggregated usage data for a single day."""

    def __init__(self, date: str):
        self.date = date
        self.entries: list[UsageEntry] = []
        self.models: set[str] = set()

    def add_entry(self, entry: UsageEntry) -> None:
        """Add an entry to this day."""
        self.entries.append(entry)
        if entry.model and entry.model != "unknown":
            self.models.add(entry.model)

    @property
    def input_tokens(self) -> int:
        return sum(e.input_tokens for e in self.entries)

    @property
    def output_tokens(self) -> int:
        return sum(e.output_tokens for e in self.entries)

    @property
    def cache_creation_tokens(self) -> int:
        return sum(e.cache_creation_tokens for e in self.entries)

    @property
    def cache_read_tokens(self) -> int:
        return sum(e.cache_read_tokens for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_creation_tokens + self.cache_read_tokens

    @property
    def total_cost(self) -> float:
        return sum(e.cost for e in self.entries)

    @property
    def message_count(self) -> int:
        return len(self.entries)


def get_earliest_timestamp(file_path: Path) -> datetime | None:
    """Extract the earliest timestamp from a JSONL file."""
    earliest = None
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # Skip malformed JSON lines

            if "timestamp" in data:
                try:
                    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                    if earliest is None or timestamp < earliest:
                        earliest = timestamp
                except ValueError:
                    continue  # Skip invalid timestamp formats

    return earliest


def load_usage_data(days: int = 30, project_filter: str | None = None) -> dict[str, DailyUsage]:
    """Load and process Claude usage data with proper deduplication and cost calculation.

    Args:
        days: Number of days to load data for
        project_filter: Optional project name to filter by
    """
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return {}

    # Import the project extraction function from sessions module
    from evo.sessions import extract_project_name_from_path

    # Find all JSONL files
    jsonl_files = list(claude_dir.rglob("*.jsonl"))

    # Sort files by earliest timestamp for chronological processing
    files_with_timestamps = []
    for file_path in jsonl_files:
        earliest = get_earliest_timestamp(file_path)
        if earliest:
            files_with_timestamps.append((file_path, earliest))

    # Sort by timestamp (oldest first)
    files_with_timestamps.sort(key=lambda x: x[1])
    sorted_files = [f[0] for f in files_with_timestamps]

    # Track processed entries for deduplication
    processed_hashes = set()

    # Process files chronologically
    daily_usage = {}
    cutoff_date = datetime.now().date() - timedelta(days=days)

    for file_path in sorted_files:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Parse JSON
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue  # Skip malformed JSON lines

                # Only process lines with usage data
                if "message" not in data or "usage" not in data.get("message", {}):
                    continue

                # Try to create entry (validates timestamp)
                try:
                    entry = UsageEntry(data)
                except ValueError:
                    continue  # Skip entries with missing/invalid timestamps

                # Skip if before cutoff date
                if entry.timestamp.date() < cutoff_date:
                    continue

                # If project filter is specified, extract and check project name
                if project_filter:
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

                    # Skip if no project found or doesn't match filter
                    if not project_name or project_filter.lower() not in project_name.lower():
                        continue

                # Check for duplicates
                unique_hash = entry.unique_hash
                if unique_hash and unique_hash in processed_hashes:
                    continue
                if unique_hash:
                    processed_hashes.add(unique_hash)

                # Add to daily usage
                date_str = entry.date_str
                if date_str not in daily_usage:
                    daily_usage[date_str] = DailyUsage(date_str)
                daily_usage[date_str].add_entry(entry)

    return daily_usage


def display_usage_stats(console: Console, days: int = 30, project_name: str | None = None) -> None:
    """Display usage statistics for the specified number of days.

    Args:
        console: Rich console for output
        days: Number of days to show statistics for
        project_name: Optional project name to filter by
    """
    # Load and process data
    daily_stats = load_usage_data(days=days, project_filter=project_name)

    if not daily_stats:
        if project_name:
            console.print(
                f"[yellow]No Claude usage data found for project '{project_name}' in the last {days} days.[/yellow]"
            )
        else:
            console.print(f"[yellow]No Claude usage data found in the last {days} days.[/yellow]")
        return

    # Create table
    title = f"Claude Usage Statistics (Last {days} Days)"
    if project_name:
        title += f" for '{project_name}'"
    table = Table(title=title)
    table.add_column("Date", style="cyan")
    table.add_column("Messages", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache", justify="right")
    table.add_column("Total Tokens", justify="right")
    table.add_column("Cost (USD)", justify="right", style="green")
    table.add_column("Models", style="magenta")

    # Sort by date
    sorted_dates = sorted(daily_stats.keys())

    total_cost = 0.0
    total_tokens = 0
    total_messages = 0

    for date in sorted_dates:
        stats = daily_stats[date]

        total_cost += stats.total_cost
        total_tokens += stats.total_tokens
        total_messages += stats.message_count

        # Clean up model names
        cleaned_models = []
        for model in sorted(stats.models):
            if model.startswith("<synthetic>"):
                parts = model.split(", ")
                if len(parts) > 1:
                    cleaned_models.append(parts[1])
            else:
                cleaned_models.append(model)

        cleaned_models = sorted(set(cleaned_models))

        table.add_row(
            date,
            str(stats.message_count),
            f"{stats.input_tokens:,}",
            f"{stats.output_tokens:,}",
            f"{stats.cache_creation_tokens + stats.cache_read_tokens:,}",
            f"{stats.total_tokens:,}",
            f"${stats.total_cost:.2f}",
            ", ".join(cleaned_models),
        )

    # Add summary row
    table.add_section()
    table.add_row("TOTAL", str(total_messages), "", "", "", f"{total_tokens:,}", f"${total_cost:.2f}", "", style="bold")

    console.print(table)
