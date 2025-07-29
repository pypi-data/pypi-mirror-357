"""AgentOps CLI - Requirements-Driven Test Automation.

Implements the core Infer → Approve → Test workflow for requirements-driven test automation.

The CLI supports multiple modes:
- Single file processing with interactive approval
- Bulk processing with Gherkin export for manual editing
- CLI approval workflow for one-by-one review

Key Commands:
- init: Initialize AgentOps project structure
- infer: Extract requirements from code changes
- approve: Process pending requirements interactively
- import-requirements: Import edited requirements with clarification
- generate-tests: Create tests from approved requirements
- run: Execute tests with root cause analysis
- traceability: Export requirements-to-tests mapping

Reference: PRD Section 5.2 (CLI Requirements)
"""

import click
import os
import sys
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import csv
from rich.table import Table
import tempfile
import subprocess
from rich.progress import Progress

from agentops_ai.agentops_core.workflow import AgentOpsWorkflow
from agentops_ai.agentops_core.requirement_store import RequirementStore

console = Console()


def find_python_files(directory: str = ".", exclude_patterns: list = None) -> list[str]:
    """Find all Python files in the directory tree.

    Recursively searches for .py files while excluding common patterns like
    test directories, cache folders, and virtual environments.

    Args:
        directory: Root directory to search (default: current directory)
        exclude_patterns: List of patterns to exclude from search

    Returns:
        List of Python file paths, sorted alphabetically

    Example:
        >>> find_python_files(".", ["tests", "venv"])
        ["./src/main.py", "./src/utils.py"]
    """
    if exclude_patterns is None:
        # WHY: Default exclusions cover common patterns that shouldn't be processed
        exclude_patterns = [
            "tests",
            "__pycache__",
            ".pytest_cache",
            ".agentops",
            "venv",
            "env",
            ".git",
        ]

    python_files = []

    for root, dirs, files in os.walk(directory):
        # WHY: Modify dirs in-place to prevent walking into excluded directories
        dirs[:] = [
            d for d in dirs if d not in exclude_patterns and not d.startswith(".")
        ]

        for file in files:
            if file.endswith(".py") and not file.startswith("."):
                file_path = os.path.join(root, file)
                # WHY: Double-check exclusion to handle nested patterns
                if not any(pattern in file_path for pattern in exclude_patterns):
                    python_files.append(file_path)

    return sorted(python_files)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version="0.2.0")
def cli():
    """AgentOps - AI-powered QA co-pilot for vibe coders."""
    pass


@cli.command()
@click.argument("directory", default=".")
def init(directory: str):
    """Initialize a new AgentOps project.

    Creates the .agentops directory structure, initializes the SQLite database,
    and sets up the project for requirements-driven test automation.

    This command must be run before any other AgentOps commands. It creates:
    - .agentops/ directory for project data
    - .agentops/tests/ directory for generated tests
    - .agentops/requirements.db SQLite database
    - .gitignore entry for .agentops/ (if .git exists)

    Args:
        directory: Project directory to initialize (default: current directory)

    Reference: PRD Section 8.1 (Phase 1: Foundation)
    """
    project_dir = Path(directory).resolve()

    # Create .agentops directory structure
    agentops_dir = project_dir / ".agentops"
    tests_dir = agentops_dir / "tests"

    agentops_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    # WHY: Initialize database early to catch any permission/disk issues
    RequirementStore(str(agentops_dir / "requirements.db"))

    # Create .gitignore entry for .agentops if .git exists
    gitignore_path = project_dir / ".gitignore"
    if (project_dir / ".git").exists():
        gitignore_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()

        # WHY: Only add if not already present to avoid duplicates
        if ".agentops/" not in gitignore_content:
            with open(gitignore_path, "a") as f:
                f.write("\n# AgentOps\n.agentops/\n")

    console.print(
        Panel(
            "[bold green]✓ AgentOps project initialized![/bold green]\n\n"
            f"Directory: {project_dir}\n"
            f"Database: {agentops_dir / 'requirements.db'}\n"
            f"Tests: {tests_dir}\n\n"
            f"Next steps:\n"
            f"1. Make changes to your Python files\n"
            f"2. Run [bold cyan]agentops infer <file>[/bold cyan] to start the workflow\n"
            f"3. Or run [bold cyan]agentops infer --all[/bold cyan] for all Python files",
            title="AgentOps Init",
            border_style="green",
        )
    )


@cli.command()
@click.argument("file_path", required=False)
@click.option(
    "--all",
    "process_all",
    is_flag=True,
    help="Process all Python files in the codebase",
)
@click.option(
    "--cli-approval",
    is_flag=True,
    help="Use CLI approval workflow instead of bulk export (only with --all)",
)
def infer(file_path: str, process_all: bool, cli_approval: bool):
    """Infer requirements from code changes using LLM analysis.

    This is the main entry point for requirements extraction. The command supports
    three modes of operation:

    1. Single file: `agentops infer mymodule.py`
       - Processes one file with interactive CLI approval
       - Best for focused development on specific modules

    2. Bulk export (default): `agentops infer --all`
       - Processes all Python files and exports to Gherkin format
       - Opens requirements file in editor for manual review
       - Most efficient for large codebases

    3. CLI approval: `agentops infer --all --cli-approval`
       - Processes all files with one-by-one terminal approval
       - Interactive workflow for detailed review

    The command uses LLM-based analysis to extract functional requirements
    from code structure, comments, and implementation patterns.

    Args:
        file_path: Path to specific Python file to process
        process_all: Process all Python files in the codebase
        cli_approval: Use CLI approval workflow instead of bulk export

    Reference: PRD Section 1.1 (Requirements Extraction Engine)
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()

        if process_all:
            if cli_approval:
                # WHY: CLI approval mode provides interactive review for detailed analysis
                console.print(
                    Panel(
                        "[bold]Analyzing all Python files and inferring requirements...[/bold]\n"
                        "[yellow]Using CLI approval workflow. Use without --cli-approval for bulk editing.[/yellow]",
                        title="AgentOps Requirements Inference (CLI Mode)",
                        border_style="cyan",
                    )
                )

                python_files = find_python_files(
                    exclude_patterns=[".agentops", "venv", "__pycache__"]
                )
                total_files = len(python_files)

                if total_files == 0:
                    console.print(
                        Panel(
                            "[yellow]No Python files found to process.[/yellow]",
                            title="No Files",
                            border_style="yellow",
                        )
                    )
                    sys.exit(1)

                processed_files = 0
                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]Processing files...", total=total_files
                    )

                    for file_path in python_files:
                        progress.update(
                            task, description=f"[cyan]Processing {file_path}..."
                        )
                        result = workflow.process_file_change(file_path)
                        if result["success"]:
                            processed_files += 1
                        progress.advance(task)

                console.print(
                    Panel(
                        f"[bold green]✓ Processing completed![/bold green]\n\n"
                        f"Files processed: {processed_files}/{total_files}\n"
                        f"Run [bold cyan]agentops approve[/bold cyan] to review and approve requirements.",
                        title="Summary",
                        border_style="green",
                    )
                )
            else:
                # WHY: Bulk export mode is most efficient for large codebases
                console.print(
                    Panel(
                        "[bold]Generating requirements for all files and exporting for editing...[/bold]\n"
                        "[green]Default mode: Bulk export. Use --cli-approval for one-by-one approval.[/green]",
                        title="AgentOps Bulk Requirements Generation",
                        border_style="cyan",
                    )
                )

                # Process all files first
                python_files = find_python_files(
                    exclude_patterns=[".agentops", "venv", "__pycache__"]
                )
                total_files = len(python_files)

                if total_files == 0:
                    console.print(
                        Panel(
                            "[yellow]No Python files found to process.[/yellow]",
                            title="No Files",
                            border_style="yellow",
                        )
                    )
                    sys.exit(1)

                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]Processing files...", total=total_files
                    )

                    for file_path in python_files:
                        progress.update(
                            task, description=f"[cyan]Processing {file_path}..."
                        )
                        workflow.process_file_change(file_path)
                        progress.advance(task)

                # Export all requirements to editable format
                result = workflow.export_requirements_for_editing()

                if result["success"]:
                    console.print(
                        Panel(
                            f"[bold green]✓ Requirements exported successfully![/bold green]\n\n"
                            f"File: {result['file_path']}\n"
                            f"Total requirements: {result['count']}\n\n"
                            f"The file will now open in your editor for review and editing.",
                            title="Export Complete",
                            border_style="green",
                        )
                    )

                    # WHY: Try multiple editors to ensure compatibility across systems
                    requirements_file = result["file_path"]
                    try:
                        # Try Cursor first, then VS Code, then default editor
                        editors = ["cursor", "code", os.environ.get("EDITOR", "nano")]
                        for editor in editors:
                            try:
                                subprocess.run([editor, requirements_file], check=True)
                                console.print(
                                    f"[green]Opened {requirements_file} in {editor}[/green]"
                                )
                                break
                            except (subprocess.CalledProcessError, FileNotFoundError):
                                continue
                        else:
                            console.print(
                                f"[yellow]Please manually open {requirements_file} in your preferred editor[/yellow]"
                            )

                        console.print(
                            Panel(
                                "[bold]Next Steps:[/bold]\n\n"
                                "1. Edit the requirements file as needed\n"
                                "2. Save the file\n"
                                "3. Run [bold cyan]agentops import-requirements[/bold cyan] to import and clarify\n"
                                "4. Run [bold cyan]agentops generate-tests[/bold cyan] to create tests",
                                title="Instructions",
                                border_style="blue",
                            )
                        )

                    except Exception as e:
                        console.print(
                            f"[yellow]Could not auto-open editor: {e}[/yellow]"
                        )
                        console.print(
                            f"[yellow]Please manually open {requirements_file} in your preferred editor[/yellow]"
                        )

                else:
                    console.print(
                        Panel(
                            f"[red]Export failed:[/red] {result['error']}",
                            title="Error",
                            border_style="red",
                        )
                    )
                    sys.exit(1)

        elif file_path:
            # WHY: Single file mode provides focused analysis for specific modules
            if not file_path.endswith(".py"):
                console.print(
                    Panel(
                        "[red]Error: Only Python files are supported in MVP[/red]",
                        title="Invalid File Type",
                        border_style="red",
                    )
                )
                sys.exit(1)

            if not os.path.exists(file_path):
                console.print(
                    Panel(
                        f"[red]Error: File not found: {file_path}[/red]",
                        title="File Not Found",
                        border_style="red",
                    )
                )
                sys.exit(1)

            try:
                workflow = AgentOpsWorkflow()

                console.print(
                    Panel(
                        f"[bold]Analyzing {file_path} and inferring requirements...[/bold]",
                        title="AgentOps Requirements Inference",
                        border_style="cyan",
                    )
                )

                result = workflow.process_file_change(file_path)

                if result["success"]:
                    console.print(
                        Panel(
                            f"[bold green]✓ Requirements inferred successfully![/bold green]\n\n"
                            f"File: {file_path}\n"
                            f"Requirements found: {result.get('requirements_count', 'Unknown')}\n"
                            f"Run [bold cyan]agentops approve[/bold cyan] to review and approve.",
                            title="Success",
                            border_style="green",
                        )
                    )
                else:
                    console.print(
                        Panel(
                            f"[red]Inference failed:[/red] {result['error']}",
                            title="Error",
                            border_style="red",
                        )
                    )
                    sys.exit(1)

            except KeyboardInterrupt:
                console.print("\n[yellow]Workflow cancelled by user[/yellow]")
                sys.exit(1)
            except Exception as e:
                console.print(
                    Panel(
                        f"[red]Unexpected error:[/red] {str(e)}",
                        title="Error",
                        border_style="red",
                    )
                )
                sys.exit(1)
        else:
            console.print(
                Panel(
                    "[red]Error: Please specify a file path or use --all flag[/red]\n\n"
                    "Examples:\n"
                    "  agentops infer mymodule.py           # Single file with CLI approval\n"
                    "  agentops infer --all                 # All files with bulk export (default)\n"
                    "  agentops infer --all --cli-approval  # All files with CLI approval",
                    title="Missing Argument",
                    border_style="red",
                )
            )
            sys.exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
def approve():
    """Process all pending requirements through the approval workflow."""
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()

        console.print(
            Panel(
                "[bold]Processing pending requirements...[/bold]",
                title="AgentOps Approval",
                border_style="cyan",
            )
        )

        result = workflow.process_pending_requirements()

        if result["processed"] == 0:
            console.print(
                Panel(
                    "[bold green]No pending requirements to process.[/bold green]",
                    title="All Done",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold green]✓ Processing completed![/bold green]\n\n"
                    f"Processed: {result['processed']}\n"
                    f"Approved: {result['approved']}\n"
                    f"Rejected: {result['rejected']}",
                    title="Summary",
                    border_style="green",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]Approval process cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
@click.option("--file", help="Run tests for a specific file")
@click.option(
    "--all", "run_all", is_flag=True, help="Run tests for all generated test files"
)
def run(file, run_all):
    """Execute tests with root cause analysis for failures."""
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    if not os.path.exists(".agentops/tests"):
        console.print(
            Panel(
                "[yellow]No tests found.[/yellow]\n\n"
                "Run [bold cyan]agentops infer <file>[/bold cyan] or [bold cyan]agentops infer --all[/bold cyan] to generate tests first.",
                title="No Tests",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()

        # Determine what to run
        if file:
            # Run tests for specific file
            console.print(
                Panel(
                    f"[bold]Running tests for {file} with root cause analysis...[/bold]",
                    title="AgentOps Test Runner",
                    border_style="cyan",
                )
            )
            result = workflow.run_tests_for_file(file)
        elif run_all:
            # Run all tests
            console.print(
                Panel(
                    "[bold]Running all tests with root cause analysis...[/bold]",
                    title="AgentOps Test Runner",
                    border_style="cyan",
                )
            )
            result = workflow.run_all_tests()
        else:
            # Default: run all tests (same as --all)
            console.print(
                Panel(
                    "[bold]Running all tests with root cause analysis...[/bold]",
                    title="AgentOps Test Runner",
                    border_style="cyan",
                )
            )
            result = workflow.run_all_tests()

        if result["success"]:
            console.print(
                Panel(
                    f"[bold green]✓ All tests passed![/bold green]\n\n"
                    f"Total tests: {result['total_tests']}\n"
                    f"All tests are passing.",
                    title="Test Results",
                    border_style="green",
                )
            )
        else:
            # Check if this is an error (no tests found, etc.)
            if "error" in result:
                console.print(
                    Panel(
                        f"[red]Test execution failed:[/red] {result['error']}",
                        title="Error",
                        border_style="red",
                    )
                )
            else:
                # This is a test failure
                console.print(
                    Panel(
                        f"[bold red]✗ {result['failed_tests']} of {result['total_tests']} tests failed[/bold red]\n\n"
                        f"Root cause analysis has been displayed above.\n"
                        f"Review the requirement vs. failure comparison to determine if this is a code bug or test issue.",
                        title="Test Results",
                        border_style="red",
                    )
                )

                # Print raw output for detailed debugging
                if result.get("output"):
                    console.print("\n[bold]Detailed test output:[/bold]")
                    console.print(result["output"])

    except Exception as e:
        console.print(
            Panel(
                f"[red]Test execution failed:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
def stats():
    """Show requirement and test statistics."""
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()
        workflow.show_stats()

    except Exception as e:
        console.print(
            Panel(
                f"[red]Failed to show statistics:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
@click.argument("file_path", required=True)
def watch(file_path):
    """Watch a file for changes and automatically trigger the workflow.

    This command will watch the specified file and automatically run
    the infer -> approve -> test workflow when changes are detected.
    """
    console.print(
        Panel(
            "[yellow]File watching is planned for a future release.[/yellow]\n\n"
            "For now, manually run [bold cyan]agentops infer <file>[/bold cyan] after making changes.",
            title="Coming Soon",
            border_style="yellow",
        )
    )


@cli.command(hidden=True)
def version():
    """Show version information."""
    console.print(
        Panel(
            "[bold]AgentOps MVP v0.2[/bold]\n\n"
            "Requirements-driven test automation for vibe coders.\n"
            "Core workflow: Infer -> Approve -> Test",
            title="Version",
            border_style="cyan",
        )
    )


@cli.command()
def traceability():
    """Export and display the requirements-to-tests traceability matrix."""
    store = RequirementStore()
    requirements = store.get_all_requirements()

    rows = []
    for req in requirements:
        test_file = f".agentops/tests/test_{os.path.basename(req.file_path)}"
        rows.append(
            [
                req.id,
                req.file_path,
                req.requirement_text,
                req.status,
                test_file if os.path.exists(test_file) else "(not generated)",
            ]
        )

    # Print table in terminal
    table = Table(title="Requirements Traceability Matrix")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Source File", style="magenta")
    table.add_column("Requirement Text", style="white")
    table.add_column("Status", style="green")
    table.add_column("Test File(s)", style="yellow")
    for row in rows:
        table.add_row(*[str(x) for x in row])
    console.print(table)

    # Export CSV
    csv_path = ".agentops/traceability.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["ID", "Source File", "Requirement Text", "Status", "Test File(s)"]
        )
        writer.writerows(rows)
    console.print(f"[green]Traceability matrix exported to {csv_path}[/green]")

    # Export Markdown
    md_path = ".agentops/traceability.md"
    with open(md_path, "w") as mdfile:
        mdfile.write(
            "| ID | Source File | Requirement Text | Status | Test File(s) |\n"
        )
        mdfile.write(
            "|----|-------------|------------------|--------|--------------|\n"
        )
        for row in rows:
            mdfile.write(f"| {' | '.join(str(x) for x in row)} |\n")
    console.print(f"[green]Traceability matrix exported to {md_path}[/green]")


@cli.command()
@click.argument("requirement_id", type=int)
def edit_requirement(requirement_id):
    """Edit an existing requirement by ID."""
    store = RequirementStore()
    req = store.get_requirement(requirement_id)
    if not req:
        console.print(f"[red]Requirement ID {requirement_id} not found.[/red]")
        return
    # Open in editor
    initial = req.requirement_text
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tf:
        tf.write(initial)
        tf.flush()
        editor = os.environ.get("EDITOR", "nano")
        subprocess.call([editor, tf.name])
        tf.seek(0)
        edited = tf.read()
    if edited.strip() != initial.strip():
        store.update_requirement_text(requirement_id, edited.strip())
        console.print(f"[green]Requirement {requirement_id} updated.[/green]")
        # Optionally regenerate test if approved
        if req.status == "approved":
            workflow = AgentOpsWorkflow()
            updated_req = store.get_requirement(requirement_id)
            workflow._generate_tests_from_requirement(updated_req)
            console.print("[green]Test regenerated for updated requirement.[/green]")
    else:
        console.print(
            f"[yellow]No changes made to requirement {requirement_id}.[/yellow]"
        )


@cli.command()
@click.argument("source_file")
def edit_test(source_file):
    """Edit the generated test file for a given source file."""
    test_file = f".agentops/tests/test_{os.path.basename(source_file)}"
    if not os.path.exists(test_file):
        console.print(
            f"[red]Test file {test_file} not found. Run 'agentops infer {source_file}' first.[/red]"
        )
        return
    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, test_file])
    console.print(f"[green]Test file {test_file} opened for editing.[/green]")


@cli.command()
def import_requirements():
    """Import edited requirements file and run clarification workflow."""
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    requirements_file = ".agentops/requirements.gherkin"
    if not os.path.exists(requirements_file):
        console.print(
            Panel(
                "[yellow]No requirements file found.[/yellow]\n\n"
                f"Expected: {requirements_file}\n"
                "Run [bold cyan]agentops infer --all[/bold cyan] first to generate requirements.",
                title="File Not Found",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()

        console.print(
            Panel(
                "[bold]Importing edited requirements and running clarification...[/bold]",
                title="AgentOps Requirements Import",
                border_style="cyan",
            )
        )

        # Import and clarify requirements
        result = workflow.import_and_clarify_requirements(requirements_file)

        if result["success"]:
            console.print(
                Panel(
                    f"[bold green]✓ Requirements imported and clarified successfully![/bold green]\n\n"
                    f"Imported: {result['imported_count']}\n"
                    f"Clarified: {result['clarified_count']}\n"
                    f"Updated: {result['updated_count']}\n\n"
                    f"Next step: Run [bold cyan]agentops generate-tests[/bold cyan] to create tests.",
                    title="Import Complete",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]Import failed:[/red] {result['error']}",
                    title="Error",
                    border_style="red",
                )
            )
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Import cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
def generate_tests():
    """Generate tests from approved requirements."""
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    try:
        workflow = AgentOpsWorkflow()

        console.print(
            Panel(
                "[bold]Generating tests from approved requirements...[/bold]",
                title="AgentOps Test Generation",
                border_style="cyan",
            )
        )

        # Generate tests from all approved requirements
        result = workflow.generate_tests_from_requirements()

        if result["success"]:
            console.print(
                Panel(
                    f"[bold green]✓ Tests generated successfully![/bold green]\n\n"
                    f"Requirements processed: {result['processed_count']}\n"
                    f"Test files created: {result['test_files_created']}\n"
                    f"Test directory: .agentops/tests/\n\n"
                    f"Next step: Run [bold cyan]agentops run --all[/bold cyan] to execute tests.",
                    title="Generation Complete",
                    border_style="green",
                )
            )

            # Show generated test files
            if result.get("test_files"):
                console.print("\n[bold]Generated test files:[/bold]")
                for test_file in result["test_files"]:
                    console.print(f"  • {test_file}")
        else:
            console.print(
                Panel(
                    f"[red]Test generation failed:[/red] {result['error']}",
                    title="Error",
                    border_style="red",
                )
            )
            sys.exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    cli()
