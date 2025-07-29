"""
MarkMate Enhanced Grading System

Advanced multi-provider grading with statistical aggregation, confidence scoring,
and comprehensive error handling using LiteLLM unified interface.
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from statistics import mean, median, stdev
from typing import Any, Optional

from ..config.grading_config import GraderConfig, GradingConfigManager
from .llm_provider import LLMProvider
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class EnhancedGradingSystem:
    """Enhanced grading system with multi-run capability and statistical aggregation."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the enhanced grading system.

        Args:
            config_path: Path to YAML configuration file.
        """
        self.config_manager: GradingConfigManager = GradingConfigManager()
        self.config: Any = self.config_manager.load_config(config_path)
        self.llm_provider: LLMProvider = LLMProvider()

        # Filter graders by available providers
        available_providers: list[str] = self.llm_provider.get_available_providers()
        self.config = self.config_manager.filter_graders_by_availability(
            self.config, available_providers
        )

        # Initialize prompt manager
        prompt_config: dict[str, Any] = {
            "prompts": self.config.prompts,
            "prompt_sections": self.config.prompt_sections,
        }
        self.prompt_manager: PromptManager = PromptManager(prompt_config)

        # Session tracking
        self.session_stats: dict[str, Any] = {
            "total_students": 0,
            "successful_grades": 0,
            "failed_grades": 0,
            "total_api_calls": 0,
            "total_cost": 0.0,
            "start_time": None,
            "end_time": None,
        }

    def grade_submission(
        self,
        student_data: dict[str, Any],
        assignment_spec: str,
        rubric: Optional[str] = None,
        max_cost_override: Optional[float] = None,
    ) -> dict[str, Any]:
        """Grade a single student submission using the enhanced multi-grader system.

        Args:
            student_data: Extracted content and metadata for the student.
            assignment_spec: Assignment specification/requirements.
            rubric: Optional separate rubric.
            max_cost_override: Override the default max cost per student.

        Returns:
            Dictionary containing comprehensive grading results.
        """
        student_id: str = student_data.get("student_id", "unknown")

        if not self.session_stats["start_time"]:
            self.session_stats["start_time"] = datetime.now()

        logger.info(f"Starting enhanced grading for student {student_id}")

        result: dict[str, Any] = {
            "student_id": student_id,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "runs_per_grader": self.config.runs_per_grader,
                "averaging_method": self.config.averaging_method,
                "graders_used": [g.name for g in self.config.graders],
            },
            "grader_results": {},
            "aggregate": {},
            "metadata": {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_cost": 0.0,
                "processing_time": 0.0,
                "errors": [],
            },
        }

        # Extract rubric if not provided
        if not rubric:
            rubric = self._extract_rubric(assignment_spec)

        # Detect assignment type for prompt selection
        assignment_type: Optional[str] = self._detect_assignment_type(student_data)

        # Extract max mark from assignment spec
        max_mark: int = self._extract_max_mark(assignment_spec)

        # Build grading prompt using PromptManager
        prompt_data: dict[str, str] = self.prompt_manager.build_grading_prompt(
            student_data=student_data,
            assignment_spec=assignment_spec,
            rubric=rubric,
            max_mark=max_mark,
            assignment_type=assignment_type,
        )

        # Check cost constraints
        max_cost: float = max_cost_override or self.config.max_cost_per_student
        estimated_cost: float = self._estimate_total_cost(prompt_data["user"])

        if estimated_cost > max_cost:
            logger.warning(
                f"Estimated cost ${estimated_cost:.4f} exceeds limit ${max_cost:.4f}"
            )
            result["metadata"]["errors"].append(
                f"Estimated cost ${estimated_cost:.4f} exceeds limit ${max_cost:.4f}"
            )

        # Process each grader
        start_time: float = time.time()

        for grader in self.config.graders:
            grader_result = self._process_grader(
                grader, prompt_data, assignment_spec, max_cost
            )
            result["grader_results"][grader.name] = grader_result

            # Update metadata
            result["metadata"]["total_runs"] += grader_result["metadata"]["total_runs"]
            result["metadata"]["successful_runs"] += grader_result["metadata"][
                "successful_runs"
            ]
            result["metadata"]["failed_runs"] += grader_result["metadata"][
                "failed_runs"
            ]
            result["metadata"]["total_cost"] += grader_result["metadata"]["total_cost"]
            result["metadata"]["errors"].extend(grader_result["metadata"]["errors"])

        # Calculate processing time
        end_time: float = time.time()
        result["metadata"]["processing_time"] = end_time - start_time

        # Aggregate results
        result["aggregate"] = self._aggregate_all_results(
            result["grader_results"], assignment_spec
        )

        # Update session statistics
        self.session_stats["total_students"] += 1
        if (
            result["aggregate"].get("mark", 0) > 0
            or result["metadata"]["successful_runs"] > 0
        ):
            self.session_stats["successful_grades"] += 1
        else:
            self.session_stats["failed_grades"] += 1

        self.session_stats["total_api_calls"] += result["metadata"]["total_runs"]
        self.session_stats["total_cost"] += result["metadata"]["total_cost"]

        logger.info(
            f"Completed grading for student {student_id}: "
            f"{result['metadata']['successful_runs']}/{result['metadata']['total_runs']} runs, "
            f"${result['metadata']['total_cost']:.4f}"
        )

        return result

    def _process_grader(
        self,
        grader: Any,
        prompt_data: dict[str, str],
        assignment_spec: str,
        max_cost: float,
    ) -> dict[str, Any]:
        """Process multiple runs for a single grader.
        
        Args:
            grader: Grader configuration object.
            prompt_data: Prompts for grading.
            assignment_spec: Assignment specification.
            max_cost: Maximum allowed cost.
            
        Returns:
            Dictionary containing grader results.
        """
        grader_result: dict[str, Any] = {
            "grader_name": grader.name,
            "provider": grader.provider,
            "model": grader.model,
            "weight": grader.weight,
            "runs": [],
            "aggregated": {},
            "metadata": {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_cost": 0.0,
                "average_response_time": 0.0,
                "errors": [],
            },
        }

        successful_runs: list[dict[str, Any]] = []
        total_response_time: float = 0.0

        for run_number in range(self.config.runs_per_grader):
            # Check cost constraint
            if grader_result["metadata"]["total_cost"] >= max_cost:
                logger.warning(f"Cost limit reached for {grader.name}, stopping runs")
                break

            run_result: dict[str, Any] = self._execute_single_run(
                grader, prompt_data, run_number + 1, assignment_spec
            )

            grader_result["runs"].append(run_result)
            grader_result["metadata"]["total_runs"] += 1

            if run_result["success"]:
                successful_runs.append(run_result)
                grader_result["metadata"]["successful_runs"] += 1
                total_response_time += run_result.get("response_time", 0)
            else:
                grader_result["metadata"]["failed_runs"] += 1
                grader_result["metadata"]["errors"].append(
                    f"Run {run_number + 1}: {run_result.get('error', 'Unknown error')}"
                )

            grader_result["metadata"]["total_cost"] += run_result.get("cost", 0.0)

        # Calculate average response time
        if successful_runs:
            grader_result["metadata"]["average_response_time"] = (
                total_response_time / len(successful_runs)
            )

        # Aggregate runs for this grader
        if successful_runs:
            grader_result["aggregated"] = self._aggregate_grader_runs(
                successful_runs, assignment_spec
            )
        else:
            grader_result["aggregated"] = {
                "mark": 0,
                "feedback": f"All runs failed for {grader.name}",
                "confidence": 0.0,
                "max_mark": self._extract_max_mark(assignment_spec),
            }

        return grader_result

    def _execute_single_run(
        self,
        grader: Any,
        prompt_data: dict[str, str],
        run_number: int,
        assignment_spec: str,
    ) -> dict[str, Any]:
        """Execute a single grading run.
        
        Args:
            grader: Grader configuration object.
            prompt_data: Prompts for grading.
            run_number: Current run number.
            assignment_spec: Assignment specification.
            
        Returns:
            Dictionary containing run results.
        """
        try:
            # Add retry logic
            for attempt in range(self.config.retry_attempts):
                try:
                    # Use system prompt from prompt data if available, otherwise from grader config
                    system_prompt: str = prompt_data.get("system") or grader.system_prompt

                    llm_result: dict[str, Any] = self.llm_provider.grade_submission(
                        provider=grader.provider,
                        model=grader.model,
                        prompt=prompt_data["user"],
                        system_prompt=system_prompt,
                        temperature=grader.temperature,
                        max_tokens=grader.max_tokens,
                        rate_limit=grader.rate_limit,
                        timeout=self.config.timeout_per_run,
                    )

                    if llm_result["success"]:
                        # Parse the grading response
                        parsed_result: dict[str, Any] = self._parse_grading_response(
                            llm_result["content"], assignment_spec
                        )

                        return {
                            "run_number": run_number,
                            "attempt": attempt + 1,
                            "success": True,
                            "mark": parsed_result["mark"],
                            "feedback": parsed_result["feedback"],
                            "max_mark": parsed_result["max_mark"],
                            "response_time": llm_result["usage"]["response_time"],
                            "cost": llm_result["usage"]["cost"],
                            "token_usage": {
                                "input_tokens": llm_result["usage"]["input_tokens"],
                                "output_tokens": llm_result["usage"]["output_tokens"],
                            },
                            "timestamp": llm_result["timestamp"],
                        }
                    else:
                        if attempt == self.config.retry_attempts - 1:
                            # Last attempt failed
                            raise Exception(llm_result.get("error", "LLM call failed"))
                        else:
                            logger.warning(
                                f"Attempt {attempt + 1} failed for {grader.name} run {run_number}, retrying..."
                            )
                            time.sleep(2**attempt)  # Exponential backoff

                except Exception as e:
                    if attempt == self.config.retry_attempts - 1:
                        logger.error(
                            f"All attempts failed for {grader.name} run {run_number}: {e}"
                        )
                        return {
                            "run_number": run_number,
                            "attempt": attempt + 1,
                            "success": False,
                            "error": str(e),
                            "cost": 0.0,
                            "timestamp": datetime.now().isoformat(),
                        }
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                        time.sleep(2**attempt)

            # If we reach here, all retry attempts were exhausted without success
            logger.error(f"All retry attempts exhausted for {grader.name} run {run_number}")
            return {
                "run_number": run_number,
                "attempt": self.config.retry_attempts,
                "success": False,
                "error": "All retry attempts exhausted",
                "cost": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Unexpected error in {grader.name} run {run_number}: {e}")
            return {
                "run_number": run_number,
                "success": False,
                "error": str(e),
                "cost": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

    def _aggregate_grader_runs(
        self, successful_runs: list[dict[str, Any]], assignment_spec: str
    ) -> dict[str, Any]:
        """Aggregate multiple runs from a single grader.
        
        Args:
            successful_runs: List of successful run results.
            assignment_spec: Assignment specification.
            
        Returns:
            Dictionary containing aggregated results.
        """
        marks: list[float] = [run["mark"] for run in successful_runs]
        feedbacks: list[str] = [run["feedback"] for run in successful_runs]

        # Calculate aggregated mark
        aggregated_mark: float
        if self.config.averaging_method == "mean":
            aggregated_mark = mean(marks)
        elif self.config.averaging_method == "median":
            aggregated_mark = median(marks)
        elif self.config.averaging_method == "trimmed_mean":
            # Remove highest and lowest, then take mean
            if len(marks) > 2:
                sorted_marks: list[float] = sorted(marks)
                trimmed_marks: list[float] = sorted_marks[1:-1]
                aggregated_mark = mean(trimmed_marks) if trimmed_marks else mean(marks)
            else:
                aggregated_mark = mean(marks)
        else:  # Default to mean
            aggregated_mark = mean(marks)

        # Calculate confidence based on consistency
        confidence: float
        if len(marks) > 1:
            mark_std: float = stdev(marks)
            max_mark: int = self._extract_max_mark(assignment_spec)
            confidence = max(0.1, 1.0 - (mark_std / max_mark))
        else:
            confidence = 0.7  # Lower confidence for single run

        # Combine feedback (use most detailed one)
        primary_feedback: str = max(feedbacks, key=len)

        return {
            "mark": round(aggregated_mark, 1),
            "feedback": primary_feedback,
            "confidence": round(confidence, 3),
            "max_mark": self._extract_max_mark(assignment_spec),
            "run_marks": marks,
            "mark_std_dev": round(stdev(marks), 2) if len(marks) > 1 else 0.0,
            "runs_used": len(successful_runs),
        }

    def _aggregate_all_results(
        self, grader_results: dict[str, Any], assignment_spec: str
    ) -> dict[str, Any]:
        """Aggregate results from all graders.
        
        Args:
            grader_results: Results from all graders.
            assignment_spec: Assignment specification.
            
        Returns:
            Dictionary containing final aggregated results.
        """
        # Extract aggregated results from each grader
        grader_aggregates: list[dict[str, Any]] = []
        weights: list[float] = []

        for grader_name, grader_result in grader_results.items():
            if grader_result["metadata"]["successful_runs"] > 0:
                grader_aggregates.append(grader_result["aggregated"])
                weights.append(grader_result["weight"])

        if not grader_aggregates:
            return {
                "mark": 0,
                "feedback": "No successful grading runs",
                "confidence": 0.0,
                "max_mark": self._extract_max_mark(assignment_spec),
                "grader_marks": [],
                "final_method": "failed",
            }

        # Calculate weighted average
        marks: list[float] = [result["mark"] for result in grader_aggregates]

        final_mark: float
        if self.config.averaging_method == "weighted_mean":
            weighted_sum: float = sum(mark * weight for mark, weight in zip(marks, weights))
            total_weight: float = sum(weights)
            final_mark = weighted_sum / total_weight
        else:
            # Use the same method as individual grader aggregation
            if self.config.averaging_method == "median":
                final_mark = median(marks)
            elif self.config.averaging_method == "trimmed_mean" and len(marks) > 2:
                sorted_marks: list[float] = sorted(marks)
                trimmed_marks: list[float] = sorted_marks[1:-1]
                final_mark = mean(trimmed_marks) if trimmed_marks else mean(marks)
            else:
                final_mark = mean(marks)

        # Calculate overall confidence
        mark_std: float = stdev(marks) if len(marks) > 1 else 0
        max_mark: int = self._extract_max_mark(assignment_spec)
        base_confidence: float = max(0.3, 1.0 - (mark_std / max_mark))

        # Boost confidence based on number of successful graders
        grader_bonus: float = min(0.2, len(grader_aggregates) * 0.05)
        final_confidence: float = min(0.95, base_confidence + grader_bonus)

        # Get primary feedback (from primary_feedback grader if available)
        primary_feedback: str = ""
        for grader_name, grader_result in grader_results.items():
            grader_config: Optional[Any] = next(
                (g for g in self.config.graders if g.name == grader_name), None
            )
            if (
                grader_config
                and grader_config.primary_feedback
                and grader_result["metadata"]["successful_runs"] > 0
            ):
                primary_feedback = grader_result["aggregated"]["feedback"]
                break

        # If no primary feedback grader, use the most detailed feedback
        if not primary_feedback and grader_aggregates:
            primary_feedback = max(grader_aggregates, key=lambda x: len(x["feedback"]))[
                "feedback"
            ]

        return {
            "mark": round(final_mark, 1),
            "feedback": primary_feedback,
            "confidence": round(final_confidence, 3),
            "max_mark": max_mark,
            "grader_marks": marks,
            "mark_std_dev": round(mark_std, 2),
            "final_method": self.config.averaging_method,
            "graders_used": len(grader_aggregates),
            "total_runs": sum(
                gr["metadata"]["total_runs"] for gr in grader_results.values()
            ),
        }

    def _detect_assignment_type(self, student_data: dict[str, Any]) -> Optional[str]:
        """Detect assignment type based on content for prompt selection.

        Args:
            student_data: Student submission data.

        Returns:
            Assignment type string or None.
        """
        content: dict[str, Any] = student_data.get("content", {})

        # Check for WordPress indicators
        if any(key.startswith("wordpress_") for key in content):
            return "wordpress"

        # Check for programming assignment indicators
        if "code" in content and content["code"]:
            # Look for specific programming languages or frameworks
            for code_file in content["code"]:
                filename = code_file.get("filename", "").lower()
                language = code_file.get("language", "").lower()

                if any(
                    ext in filename
                    for ext in [".py", ".js", ".html", ".css", ".java", ".cpp"]
                ):
                    return "programming"
                if language in ["python", "javascript", "java", "cpp", "html", "css"]:
                    return "programming"

        # Check for React/web development
        if "web" in content and content["web"]:
            return "programming"

        # Default to general
        return "general"

    def _extract_rubric(self, assignment_spec: str) -> str:
        """Extract rubric information from assignment specification.
        
        Args:
            assignment_spec: Assignment specification text.
            
        Returns:
            Extracted rubric text.
        """
        # Look for common rubric patterns
        rubric_patterns: list[str] = [
            r"(?i)rubric[:\s]*(.*?)(?=\n\n|\Z)",
            r"(?i)assessment criteria[:\s]*(.*?)(?=\n\n|\Z)",
            r"(?i)marking scheme[:\s]*(.*?)(?=\n\n|\Z)",
            r"(?i)grading[:\s]*(.*?)(?=\n\n|\Z)",
        ]

        for pattern in rubric_patterns:
            match: Optional[re.Match[str]] = re.search(pattern, assignment_spec, re.DOTALL)
            if match:
                return match.group(1).strip()

        # If no specific rubric found, return the whole assignment spec
        return assignment_spec

    def _extract_max_mark(self, assignment_spec: str) -> int:
        """Extract maximum mark from assignment specification.
        
        Args:
            assignment_spec: Assignment specification text.
            
        Returns:
            Maximum mark value.
        """
        # Look for patterns like "Total: 100", "out of 50", "marks: 30"
        mark_patterns: list[str] = [
            r"(?i)total[:\s]*(\d+)",
            r"(?i)out of[:\s]*(\d+)",
            r"(?i)marks?[:\s]*(\d+)",
            r"(?i)points?[:\s]*(\d+)",
        ]

        for pattern in mark_patterns:
            match: Optional[re.Match[str]] = re.search(pattern, assignment_spec)
            if match:
                return int(match.group(1))

        # Default to 100 if no max mark found
        return 100

    def _parse_grading_response(
        self, response_text: str, assignment_spec: str
    ) -> dict[str, Any]:
        """Parse LLM grading response into structured format.
        
        Args:
            response_text: Raw response text from LLM.
            assignment_spec: Assignment specification.
            
        Returns:
            Dictionary containing parsed grading results.
        """
        result: dict[str, Any] = {
            "mark": 0,
            "feedback": "",
            "max_mark": self._extract_max_mark(assignment_spec),
            "timestamp": datetime.now().isoformat(),
            "strengths": [],
            "improvements": [],
            "confidence": 0.8,
        }

        # Try to parse as JSON first (new prompt format)
        try:
            # Clean up response to extract JSON
            response_clean: str = response_text.strip()

            # Find JSON in response
            json_start: int = response_clean.find("{")
            json_end: int = response_clean.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str: str = response_clean[json_start:json_end]
                parsed_json: dict[str, Any] = json.loads(json_str)

                # Extract fields from JSON
                result["mark"] = float(parsed_json.get("mark", 0))
                result["feedback"] = parsed_json.get("feedback", "")
                result["max_mark"] = int(
                    parsed_json.get("max_mark", self._extract_max_mark(assignment_spec))
                )
                result["strengths"] = parsed_json.get("strengths", [])
                result["improvements"] = parsed_json.get("improvements", [])
                result["confidence"] = float(parsed_json.get("confidence", 0.8))

                return result

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(
                f"Failed to parse JSON response, falling back to text parsing: {e}"
            )

        # Fallback to legacy text parsing
        # Extract mark
        mark_match: Optional[re.Match[str]] = re.search(
            r"MARK[:\s]*(\d+(?:\.\d+)?)", response_text, re.IGNORECASE
        )
        if mark_match:
            result["mark"] = float(mark_match.group(1))

        # Extract feedback
        feedback_match: Optional[re.Match[str]] = re.search(
            r"FEEDBACK[:\s]*(.*?)(?=\n\n|\Z)", response_text, re.IGNORECASE | re.DOTALL
        )
        if feedback_match:
            result["feedback"] = feedback_match.group(1).strip()
        else:
            # If no explicit feedback section, use the whole response
            result["feedback"] = response_text.strip()

        return result

    def _estimate_total_cost(self, prompt: str) -> float:
        """Estimate total cost for all grading runs.
        
        Args:
            prompt: Grading prompt text.
            
        Returns:
            Estimated total cost.
        """
        total_cost: float = 0.0

        # Rough token estimation (characters / 4)
        input_tokens: int = len(prompt) // 4
        output_tokens: int = 500  # Estimated output

        for grader in self.config.graders:
            grader_cost: float = self.llm_provider.estimate_cost(
                grader.provider, grader.model, input_tokens, output_tokens
            )
            total_cost += grader_cost * self.config.runs_per_grader

        return total_cost

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of the current grading session.
        
        Returns:
            Dictionary containing session summary statistics.
        """
        self.session_stats["end_time"] = datetime.now()

        duration_seconds: float
        if self.session_stats["start_time"]:
            duration = self.session_stats["end_time"] - self.session_stats["start_time"]
            duration_seconds = duration.total_seconds()
        else:
            duration_seconds = 0

        # Get total usage from LLM provider
        usage_stats: dict[str, Any] = self.llm_provider.get_total_usage()

        return {
            "session_stats": self.session_stats,
            "duration_seconds": duration_seconds,
            "usage_stats": usage_stats,
            "config_summary": {
                "graders": len(self.config.graders),
                "runs_per_grader": self.config.runs_per_grader,
                "averaging_method": self.config.averaging_method,
            },
        }
