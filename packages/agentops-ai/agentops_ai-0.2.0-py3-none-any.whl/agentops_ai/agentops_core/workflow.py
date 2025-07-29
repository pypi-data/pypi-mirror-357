"""AgentOps workflow module.

Implements the main orchestration logic for requirements-driven test automation.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from .requirement_inference import RequirementInferenceEngine
from .requirement_store import RequirementStore, Requirement
from .terminal_ui import TerminalUI
from .services.test_generator import TestGenerator


class AgentOpsWorkflow:
    """Main workflow orchestrator for AgentOps MVP."""

    def __init__(self):
        """Initialize the workflow with all components."""
        self.inference_engine = RequirementInferenceEngine()
        self.requirement_store = RequirementStore()
        self.terminal_ui = TerminalUI()
        self.test_generator = TestGenerator()

    def process_file_change(self, file_path: str) -> Dict[str, Any]:
        """Process a file change through the complete workflow.

        This is the main entry point for the Infer -> Approve -> Test workflow.

        Args:
            file_path: Path to the changed Python file

        Returns:
            Dictionary with workflow results
        """
        # Step 1: Infer requirement from file changes
        inference_result = self.inference_engine.infer_requirement_from_file(file_path)

        if not inference_result["success"]:
            return {
                "success": False,
                "step": "inference",
                "error": inference_result["error"],
            }

        # Step 2: HITL approval
        approval_result = self._handle_requirement_approval(
            inference_result["requirement"],
            file_path,
            inference_result["confidence"],
            inference_result.get("metadata", {}),
        )

        if not approval_result["success"]:
            return {
                "success": False,
                "step": "approval",
                "error": approval_result.get("error", "User cancelled"),
            }

        # Step 3: Store approved requirement
        requirement = self.requirement_store.create_requirement_from_inference(
            approval_result["requirement_text"],
            file_path,
            inference_result["confidence"],
            inference_result.get("metadata", {}),
        )

        requirement.status = "approved"
        requirement_id = self.requirement_store.store_requirement(requirement)

        # Step 4: Generate tests based on approved requirement
        test_result = self._generate_tests_from_requirement(requirement)

        if not test_result["success"]:
            return {
                "success": False,
                "step": "test_generation",
                "error": test_result["error"],
            }

        return {
            "success": True,
            "requirement_id": requirement_id,
            "requirement_text": approval_result["requirement_text"],
            "test_file": test_result["test_file"],
            "confidence": inference_result["confidence"],
        }

    def _handle_requirement_approval(
        self,
        requirement_text: str,
        file_path: str,
        confidence: float,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle the human-in-the-loop requirement approval process.

        Args:
            requirement_text: Inferred requirement text
            file_path: Path to the file
            confidence: Confidence score
            metadata: Additional metadata

        Returns:
            Approval result dictionary
        """
        while True:
            # Show approval dialog
            choice = self.terminal_ui.show_requirement_approval(
                requirement_text, file_path, confidence, metadata
            )

            if choice == "approve":
                # Confirm approval
                if self.terminal_ui.show_approval_confirmation(requirement_text):
                    self.terminal_ui.show_success_message("approved", requirement_text)
                    return {
                        "success": True,
                        "requirement_text": requirement_text,
                        "action": "approved",
                    }
                else:
                    continue  # Go back to main approval dialog

            elif choice == "edit":
                # Edit requirement text
                edited_text = self.terminal_ui.edit_requirement_text(requirement_text)
                if edited_text:
                    # Confirm the edited requirement
                    if self.terminal_ui.show_approval_confirmation(edited_text):
                        self.terminal_ui.show_success_message("edited", edited_text)
                        return {
                            "success": True,
                            "requirement_text": edited_text,
                            "action": "edited",
                        }
                    else:
                        requirement_text = (
                            edited_text  # Keep the edit for next iteration
                        )
                        continue
                else:
                    continue  # No edit made, go back to main dialog

            elif choice == "reject":
                # Confirm rejection
                if self.terminal_ui.show_rejection_confirmation(requirement_text):
                    self.terminal_ui.show_success_message("rejected", requirement_text)
                    return {
                        "success": False,
                        "requirement_text": requirement_text,
                        "action": "rejected",
                    }
                else:
                    continue  # Go back to main approval dialog

            elif choice == "quit":
                return {"success": False, "action": "quit"}

    def _generate_tests_from_requirement(
        self, requirement: Requirement
    ) -> Dict[str, Any]:
        """Generate tests based on an approved requirement.

        Args:
            requirement: The approved requirement

        Returns:
            Test generation result
        """
        try:
            # Use the requirement-based test generation
            result = self.test_generator.generate_tests_from_requirement(
                requirement.file_path,
                requirement.requirement_text,
                requirement.confidence,
            )

            if result["success"]:
                # Determine test file path
                test_file_path = self._get_test_file_path(requirement.file_path)

                # Ensure test directory exists
                os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

                # Write test file
                with open(test_file_path, "w") as f:
                    f.write(result["code"])

                return {
                    "success": True,
                    "test_file": test_file_path,
                    "code": result["code"],
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Test generation failed"),
                }

        except Exception as e:
            return {"success": False, "error": f"Test generation error: {str(e)}"}

    def _get_test_file_path(self, file_path: str) -> str:
        """Get the test file path for a given source file.

        Args:
            file_path: Path to the source file

        Returns:
            Path to the corresponding test file
        """
        # Convert to Path object for easier manipulation
        source_path = Path(file_path)

        # Create test file path in .agentops/tests directory
        relative_path = (
            source_path.relative_to(Path.cwd())
            if source_path.is_absolute()
            else source_path
        )
        test_file_name = f"test_{source_path.name}"

        test_path = Path(".agentops") / "tests" / relative_path.parent / test_file_name

        return str(test_path)

    def run_tests_with_rca(self, test_file: str = None) -> Dict[str, Any]:
        """Run tests and provide root cause analysis for failures.

        Args:
            test_file: Optional specific test file to run

        Returns:
            Test results with root cause analysis
        """
        import subprocess
        import json

        # Determine test target
        if test_file:
            test_target = test_file
        else:
            test_target = ".agentops/tests"

        # Run pytest with JSON output
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_target,
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=.agentops/test_results.json",
                ],
                capture_output=True,
                text=True,
            )

            # Parse test results
            results_file = ".agentops/test_results.json"
            if os.path.exists(results_file):
                with open(results_file) as f:
                    test_results = json.load(f)
            else:
                test_results = {"tests": []}

            # Analyze failures
            failures = []
            for test in test_results.get("tests", []):
                if test.get("outcome") == "failed":
                    failures.append(
                        {
                            "test_name": test.get("nodeid", "unknown"),
                            "failure_message": test.get("call", {}).get(
                                "longrepr", "Unknown failure"
                            ),
                        }
                    )

            if failures:
                # Show root cause analysis for failures
                self._show_root_cause_analysis_for_failures(failures)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "failures": failures,
                "total_tests": len(test_results.get("tests", [])),
                "failed_tests": len(failures),
            }

        except Exception as e:
            return {"success": False, "error": f"Test execution failed: {str(e)}"}

    def run_tests_for_file(self, file_path: str) -> Dict[str, Any]:
        """Run tests for a specific source file.

        Args:
            file_path: Path to the source file

        Returns:
            Test results with root cause analysis
        """
        # Get the test file path for this source file
        test_file = self._get_test_file_path(file_path)

        # Check if test file exists
        if not os.path.exists(test_file):
            return {
                "success": False,
                "error": f"No tests found for {file_path}. Run 'agentops infer {file_path}' first.",
            }

        # Run tests for this specific file
        return self.run_tests_with_rca(test_file)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the .agentops/tests directory.

        Returns:
            Test results with root cause analysis
        """
        return self.run_tests_with_rca()

    def _show_root_cause_analysis_for_failures(self, failures: List[Dict[str, Any]]):
        """Show root cause analysis for test failures.

        Args:
            failures: List of test failures
        """
        for failure in failures:
            # Try to find the corresponding requirement
            test_name = failure["test_name"]

            # Extract file path from test name
            if "::" in test_name:
                test_file = test_name.split("::")[0]
                # Convert test file back to source file
                source_file = self._get_source_file_from_test(test_file)

                if source_file:
                    # Get approved requirements for this file
                    requirements = self.requirement_store.get_requirements_for_file(
                        source_file, status="approved"
                    )

                    if requirements:
                        # Show RCA for the most recent requirement
                        requirement = requirements[0]
                        self.terminal_ui.show_root_cause_analysis(
                            requirement, failure["failure_message"]
                        )

    def _get_source_file_from_test(self, test_file: str) -> Optional[str]:
        """Get the source file path from a test file path.

        Args:
            test_file: Path to the test file

        Returns:
            Path to the source file or None
        """
        # Convert test file path back to source file path
        test_path = Path(test_file)

        # Remove .agentops/tests prefix
        if test_path.parts[:2] == (".agentops", "tests"):
            relative_path = Path(*test_path.parts[2:])

            # Remove test_ prefix from filename
            if relative_path.name.startswith("test_"):
                source_name = relative_path.name[5:]  # Remove "test_"
                source_path = relative_path.parent / source_name

                if source_path.exists():
                    return str(source_path)

        return None

    def process_pending_requirements(self) -> Dict[str, Any]:
        """Process all pending requirements through the approval workflow.

        Returns:
            Summary of processing results
        """
        pending_requirements = self.requirement_store.get_pending_requirements()

        if not pending_requirements:
            self.terminal_ui.show_pending_requirements([])
            return {"success": True, "processed": 0}

        # Show pending requirements
        self.terminal_ui.show_pending_requirements(pending_requirements)

        approved_count = 0
        rejected_count = 0

        for requirement in pending_requirements:
            # Process each pending requirement
            approval_result = self._handle_requirement_approval(
                requirement.requirement_text,
                requirement.file_path,
                requirement.confidence,
                requirement.metadata,
            )

            if approval_result["success"]:
                # Update requirement status
                if approval_result["action"] == "approved":
                    self.requirement_store.approve_requirement(requirement.id)
                    approved_count += 1

                    # Generate tests
                    test_result = self._generate_tests_from_requirement(requirement)
                    if not test_result["success"]:
                        self.terminal_ui.show_error_message(
                            f"Failed to generate tests: {test_result['error']}"
                        )
                elif approval_result["action"] == "edited":
                    # Update requirement text and approve
                    self.requirement_store.update_requirement_text(
                        requirement.id, approval_result["requirement_text"]
                    )
                    self.requirement_store.approve_requirement(requirement.id)
                    approved_count += 1

                    # Generate tests with updated requirement
                    updated_requirement = self.requirement_store.get_requirement(
                        requirement.id
                    )
                    test_result = self._generate_tests_from_requirement(
                        updated_requirement
                    )
                    if not test_result["success"]:
                        self.terminal_ui.show_error_message(
                            f"Failed to generate tests: {test_result['error']}"
                        )
            else:
                if approval_result["action"] == "rejected":
                    self.requirement_store.reject_requirement(requirement.id)
                    rejected_count += 1

        return {
            "success": True,
            "processed": len(pending_requirements),
            "approved": approved_count,
            "rejected": rejected_count,
        }

    def show_stats(self):
        """Show requirement statistics."""
        stats = self.requirement_store.get_stats()
        self.terminal_ui.show_requirement_stats(stats)

    def export_requirements_for_editing(self) -> Dict[str, Any]:
        """Export all requirements to an editable Gherkin format file.

        Returns:
            Dictionary with success status, file path, and count
        """
        try:
            # Get all requirements
            all_requirements = self.requirement_store.get_all_requirements()

            if not all_requirements:
                return {
                    "success": False,
                    "error": "No requirements found to export. Run 'agentops infer' first.",
                }

            # Create requirements file in Gherkin format
            requirements_file = ".agentops/requirements.gherkin"

            with open(requirements_file, "w") as f:
                f.write("# AgentOps Requirements File\n")
                f.write(
                    "# Edit this file to modify requirements, then run 'agentops import-requirements'\n\n"
                )

                # Group requirements by file
                files_requirements = {}
                for req in all_requirements:
                    if req.file_path not in files_requirements:
                        files_requirements[req.file_path] = []
                    files_requirements[req.file_path].append(req)

                # Write requirements in Gherkin format
                for file_path, requirements in files_requirements.items():
                    f.write(f"# File: {file_path}\n")
                    f.write(f"Feature: {os.path.basename(file_path)} functionality\n\n")

                    for req in requirements:
                        f.write(f"  # Requirement ID: {req.id}\n")
                        f.write(f"  # Status: {req.status}\n")
                        f.write(f"  # Confidence: {req.confidence:.1%}\n")
                        f.write(f"  Scenario: {req.requirement_text}\n")
                        f.write(f"    Given the {os.path.basename(file_path)} module\n")
                        f.write("    When I use the functionality\n")
                        f.write(
                            f"    Then it should {req.requirement_text.lower()}\n\n"
                        )

                    f.write("\n")

            return {
                "success": True,
                "file_path": requirements_file,
                "count": len(all_requirements),
            }

        except Exception as e:
            return {"success": False, "error": f"Export failed: {str(e)}"}

    def import_and_clarify_requirements(self, requirements_file: str) -> Dict[str, Any]:
        """Import edited requirements file and run clarification workflow.

        Args:
            requirements_file: Path to the edited Gherkin requirements file

        Returns:
            Dictionary with import results
        """
        try:
            # Parse the Gherkin file
            parsed_requirements = self._parse_gherkin_requirements(requirements_file)

            if not parsed_requirements:
                return {
                    "success": False,
                    "error": "No valid requirements found in the file",
                }

            imported_count = 0
            clarified_count = 0
            updated_count = 0

            # Process each parsed requirement
            for req_data in parsed_requirements:
                # Check if requirement exists (by ID if present)
                if req_data.get("id"):
                    existing_req = self.requirement_store.get_requirement(
                        req_data["id"]
                    )
                    if existing_req:
                        # Update existing requirement if text changed
                        if (
                            existing_req.requirement_text
                            != req_data["requirement_text"]
                        ):
                            self.requirement_store.update_requirement_text(
                                req_data["id"], req_data["requirement_text"]
                            )
                            updated_count += 1
                        continue

                # Create new requirement
                requirement = self.requirement_store.create_requirement_from_inference(
                    requirement_text=req_data["requirement_text"],
                    file_path=req_data["file_path"],
                    confidence=req_data.get("confidence", 0.9),
                    metadata=req_data.get("metadata", {}),
                )

                # Run clarification if needed
                clarification_result = self._run_clarification_workflow(requirement)
                if clarification_result["clarified"]:
                    requirement.requirement_text = clarification_result[
                        "clarified_text"
                    ]
                    clarified_count += 1

                # Store the requirement as approved (since it was manually edited)
                requirement.status = "approved"
                self.requirement_store.store_requirement(requirement)
                imported_count += 1

            return {
                "success": True,
                "imported_count": imported_count,
                "clarified_count": clarified_count,
                "updated_count": updated_count,
            }

        except Exception as e:
            return {"success": False, "error": f"Import failed: {str(e)}"}

    def generate_tests_from_requirements(self) -> Dict[str, Any]:
        """Generate tests from all approved requirements.

        Returns:
            Dictionary with generation results
        """
        try:
            # Get all approved requirements
            approved_requirements = self.requirement_store.get_approved_requirements()

            if not approved_requirements:
                return {
                    "success": False,
                    "error": "No approved requirements found. Run 'agentops import-requirements' first.",
                }

            processed_count = 0
            test_files_created = 0
            test_files = []

            # Group requirements by file
            files_requirements = {}
            for req in approved_requirements:
                if req.file_path not in files_requirements:
                    files_requirements[req.file_path] = []
                files_requirements[req.file_path].append(req)

            # Generate tests for each file
            for file_path, requirements in files_requirements.items():
                for requirement in requirements:
                    test_result = self._generate_tests_from_requirement(requirement)
                    if test_result["success"]:
                        if test_result.get("test_file") not in test_files:
                            test_files.append(test_result["test_file"])
                            test_files_created += 1
                    processed_count += 1

            return {
                "success": True,
                "processed_count": processed_count,
                "test_files_created": test_files_created,
                "test_files": test_files,
            }

        except Exception as e:
            return {"success": False, "error": f"Test generation failed: {str(e)}"}

    def _parse_gherkin_requirements(
        self, requirements_file: str
    ) -> List[Dict[str, Any]]:
        """Parse the Gherkin requirements file.

        Args:
            requirements_file: Path to the Gherkin file

        Returns:
            List of parsed requirement dictionaries
        """
        requirements = []
        current_file = None
        current_req = {}

        try:
            with open(requirements_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    # Extract metadata from comments
                    if line.startswith("# File:"):
                        current_file = line.replace("# File:", "").strip()
                    elif line.startswith("# Requirement ID:"):
                        current_req["id"] = int(
                            line.replace("# Requirement ID:", "").strip()
                        )
                    elif line.startswith("# Confidence:"):
                        conf_str = (
                            line.replace("# Confidence:", "").strip().replace("%", "")
                        )
                        current_req["confidence"] = float(conf_str) / 100.0
                    continue

                # Parse Gherkin elements
                if line.startswith("Feature:"):
                    continue
                elif line.startswith("Scenario:"):
                    # Extract requirement text from scenario
                    requirement_text = line.replace("Scenario:", "").strip()
                    current_req["requirement_text"] = requirement_text
                    current_req["file_path"] = current_file
                elif (
                    line.startswith("Given")
                    or line.startswith("When")
                    or line.startswith("Then")
                ):
                    # End of scenario - save requirement
                    if current_req.get("requirement_text") and current_req.get(
                        "file_path"
                    ):
                        requirements.append(current_req.copy())
                        current_req = {}

            return requirements

        except Exception as e:
            raise Exception(f"Failed to parse Gherkin file: {str(e)}")

    def _run_clarification_workflow(self, requirement: "Requirement") -> Dict[str, Any]:
        """Run LLM-based clarification for a requirement.

        Args:
            requirement: Requirement object to clarify

        Returns:
            Dictionary with clarification results
        """
        try:
            # Load clarification prompt from file
            clarification_prompt = self._load_prompt(
                "requirement_clarification.txt"
            ).format(
                requirement_text=requirement.requirement_text,
                file_path=requirement.file_path,
            )

            # Use the requirement inference engine to clarify
            clarified_text = self.requirement_inference.infer_requirement(
                requirement.file_path, clarification_prompt
            )

            # Check if clarification actually improved the requirement
            if (
                clarified_text
                and clarified_text.strip() != requirement.requirement_text.strip()
            ):
                # Show clarification to user for approval
                approval = self.terminal_ui.show_clarification_approval(
                    original=requirement.requirement_text,
                    clarified=clarified_text,
                    file_path=requirement.file_path,
                )

                if approval:
                    return {"clarified": True, "clarified_text": clarified_text}

            return {"clarified": False, "clarified_text": requirement.requirement_text}

        except Exception:
            # If clarification fails, use original text
            return {"clarified": False, "clarified_text": requirement.requirement_text}

    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt from the prompts directory.

        Args:
            prompt_file: Name of the prompt file

        Returns:
            Prompt content as string
        """
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to hardcoded prompt if file not found
            return (
                "Please review and clarify this requirement for better test generation."
            )
