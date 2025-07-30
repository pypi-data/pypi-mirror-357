"""
Web validation module for HTML, CSS, and JavaScript analysis.

This module provides comprehensive web content validation using multiple tools:
- HTML5 validation with accessibility checks
- CSS validation and best practices analysis
- JavaScript basic syntax and structure checking
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, TypedDict, Union

# Web parsing imports - handle optional dependencies
try:
    import cssutils
    import html5lib
    from bs4 import BeautifulSoup
    
    web_tools_available: bool = True
except ImportError:
    cssutils = None  # type: ignore[assignment]
    html5lib = None  # type: ignore[assignment] 
    BeautifulSoup = None  # type: ignore[assignment]
    web_tools_available = False


# Type definitions for web validation results
class HTMLValidationResult(TypedDict):
    """Structure for HTML5 validation results."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    total_issues: int


class AccessibilityResult(TypedDict):
    """Structure for accessibility check results."""
    issues: List[str]
    warnings: List[str]
    good_practices: List[str]
    score: float


class BestPracticesResult(TypedDict):
    """Structure for best practices results."""
    issues: List[str]
    warnings: List[str]
    good_practices: List[str]
    score: float


class SEOResult(TypedDict):
    """Structure for SEO analysis results."""
    issues: List[str]
    warnings: List[str]
    good_practices: List[str]
    score: float


class HTMLSummaryResult(TypedDict):
    """Structure for HTML validation summary."""
    status: str
    errors: int
    warnings: int
    overall_score: float
    recommendations: List[str]


class CSSValidationResult(TypedDict):
    """Structure for CSS validation results."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    rules_count: int
    style_rules: Optional[int]
    at_rules: Optional[int]


class CSSPerformanceResult(TypedDict):
    """Structure for CSS performance analysis."""
    issues: List[str]
    warnings: List[str]
    good_practices: List[str]
    metrics: Dict[str, Union[int, float]]


class CSSSummaryResult(TypedDict):
    """Structure for CSS analysis summary."""
    status: str
    total_issues: int
    overall_score: float
    recommendations: List[str]


class JSSyntaxResult(TypedDict):
    """Structure for JavaScript syntax check results."""
    issues: List[str]
    warnings: List[str]
    score: float


class JSStructureResult(TypedDict):
    """Structure for JavaScript structure analysis."""
    complexity_estimate: str
    function_count: int
    class_count: int
    estimated_lines_of_code: int
    has_modules: bool
    has_async_code: bool


class JSSummaryResult(TypedDict):
    """Structure for JavaScript analysis summary."""
    quality: str
    total_issues: int
    overall_score: float
    recommendations: List[str]


def _ensure_list_field(data: Dict[str, Any], field_name: str) -> List[Any]:
    """Ensure a dictionary field is a list, converting if necessary.
    
    Args:
        data: Dictionary to check/modify.
        field_name: Name of the field that should be a list.
        
    Returns:
        The field value as a list.
    """
    if field_name not in data:
        data[field_name] = []
    elif not isinstance(data[field_name], list):
        # Convert non-list to single-item list if it has meaningful content
        if data[field_name] is not None and data[field_name] != "" and data[field_name] != 0:
            data[field_name] = [data[field_name]]
        else:
            data[field_name] = []
    return data[field_name]


def _safe_append(lst: Any, item: Any) -> None:
    """Safely append to a list-like object.
    
    Args:
        lst: List-like object to append to.
        item: Item to append.
    """
    if isinstance(lst, list):
        lst.append(item)
    else:
        logger.warning(f"Attempted to append to non-list: {type(lst)}")


def _safe_len(obj: Any) -> int:
    """Safely get length of an object, returning 0 for non-sized objects.
    
    Args:
        obj: Object to get length of.
        
    Returns:
        Length of object, or 0 if not applicable.
    """
    try:
        if hasattr(obj, '__len__'):
            return len(obj)
        return 0
    except (TypeError, AttributeError):
        return 0

logger = logging.getLogger(__name__)


class HTMLValidator:
    """HTML validation with accessibility and best practices checking."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the HTML validator.

        Args:
            config: Optional configuration for validation.
        """
        self.config: Dict[str, Any] = config or {}
        self.tools_available: bool = web_tools_available

        # Suppress cssutils warnings - disable due to type checker issues
        # if self.tools_available and cssutils is not None:
        #     cssutils.log.setLevel(logging.ERROR)

        logger.info(
            f"HTML validator initialized (tools available: {self.tools_available})"
        )

    def validate_html(self, file_path: str, html_content: str) -> Dict[str, Any]:  # type: ignore[misc] - Complex return structure
        """Validate HTML content for structure, accessibility, and best practices.

        Args:
            file_path: Path to the HTML file.
            html_content: HTML content to validate.

        Returns:
            Dictionary containing validation results.
        """
        if not self.tools_available:
            return {"error": "HTML validation tools not available"}

        validation_results: Dict[str, Any] = {
            "file_path": file_path,
            "validation_timestamp": "analyzed",  # Simple timestamp
            "html5_validation": {},
            "accessibility_check": {},
            "best_practices": {},
            "seo_analysis": {},
            "summary": {},
        }

        try:
            # Parse HTML with html5lib for strict validation
            validation_results["html5_validation"] = self._validate_html5(html_content)

            # Parse with BeautifulSoup for analysis - only if tools available
            if BeautifulSoup is not None:
                soup = BeautifulSoup(html_content, "html.parser")

                # Accessibility analysis
                validation_results["accessibility_check"] = self._check_accessibility(soup)

                # Best practices analysis
                validation_results["best_practices"] = self._check_best_practices(
                    soup, html_content
                )

                # SEO analysis
                validation_results["seo_analysis"] = self._analyze_seo(soup)

            # Generate summary
            validation_results["summary"] = self._generate_html_summary(
                validation_results
            )

            return validation_results

        except Exception as e:
            logger.error(f"HTML validation failed for {file_path}: {e}")
            return {"error": str(e)}

    def _validate_html5(self, html_content: str) -> Dict[str, Any]:
        """Validate HTML5 structure and syntax."""
        try:
            # Initialize validation result with proper types
            validation_result: Dict[str, Any] = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "total_issues": 0,
            }
            
            # Ensure list fields are properly typed
            errors_list = _ensure_list_field(validation_result, "errors")
            warnings_list = _ensure_list_field(validation_result, "warnings")

            try:
                # Use html5lib for strict HTML5 parsing if available
                if html5lib is not None:
                    parser = html5lib.HTMLParser(strict=True)
                    parser.parse(html_content)
                    
                # Check document structure
                if not html_content.strip().lower().startswith("<!doctype"):
                    _safe_append(warnings_list, "Missing DOCTYPE declaration")

                # Basic structure validation with BeautifulSoup if available
                if BeautifulSoup is not None:
                    soup = BeautifulSoup(html_content, "html5lib")
                    if not soup.find("html"):
                        _safe_append(errors_list, "Missing <html> element")
                    if not soup.find("head"):
                        _safe_append(errors_list, "Missing <head> element")
                    if not soup.find("body"):
                        _safe_append(errors_list, "Missing <body> element")

            except Exception as parse_error:
                _safe_append(errors_list, f"HTML5 parsing error: {str(parse_error)}")

            # Update validation result
            validation_result["valid"] = _safe_len(errors_list) == 0
            validation_result["total_issues"] = _safe_len(errors_list) + _safe_len(warnings_list)

            return validation_result

        except Exception as e:
            logger.error(f"HTML5 validation failed: {e}")
            return {"error": str(e)}

    def _check_accessibility(self, soup: Any) -> Dict[str, Any]:  # type: ignore[misc] - BeautifulSoup typing complex
        """Check accessibility compliance."""
        accessibility: Dict[str, Any] = {"issues": [], "warnings": [], "good_practices": [], "score": 0}
        
        # Ensure list fields are properly typed
        issues_list = _ensure_list_field(accessibility, "issues")
        warnings_list = _ensure_list_field(accessibility, "warnings")
        good_practices_list = _ensure_list_field(accessibility, "good_practices")

        try:
            # Image alt text check
            images = soup.find_all("img")
            images_without_alt = [img for img in images if not img.get("alt")]
            if images_without_alt:
                _safe_append(issues_list,
                    f"{len(images_without_alt)} images missing alt attributes"
                )
            else:
                _safe_append(good_practices_list, "All images have alt attributes")

            # Form label check
            inputs = soup.find_all(
                "input", {"type": lambda x: x not in ["submit", "button", "hidden"]}
            )
            inputs_without_labels = []
            for input_elem in inputs:
                input_id = input_elem.get("id")
                if not input_id or not soup.find("label", {"for": input_id}):
                    inputs_without_labels.append(input_elem)

            if inputs_without_labels:
                _safe_append(issues_list,
                    f"{len(inputs_without_labels)} form inputs missing labels"
                )
            elif inputs:
                _safe_append(good_practices_list,
                    "All form inputs have proper labels"
                )

            # Heading hierarchy check
            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if headings:
                heading_levels = [int(h.name[1]) for h in headings]
                if heading_levels and heading_levels[0] != 1:
                    _safe_append(warnings_list,
                        "Page should start with h1 heading"
                    )

                # Check for heading level skipping
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] - heading_levels[i - 1] > 1:
                        _safe_append(warnings_list,
                            "Heading levels should not skip (e.g., h2 to h4)"
                        )
                        break
            else:
                _safe_append(warnings_list, "Page has no headings")

            # Language attribute check
            html_tag = soup.find("html")
            if not html_tag or not html_tag.get("lang"):
                _safe_append(issues_list, "Missing lang attribute on html element")
            else:
                _safe_append(good_practices_list,
                    "HTML element has lang attribute"
                )

            # Color contrast (basic check - look for inline styles)
            elements_with_color = soup.find_all(
                attrs={"style": re.compile(r"color\s*:")}
            )
            if elements_with_color:
                _safe_append(warnings_list,
                    "Inline color styles found - ensure sufficient contrast"
                )

            # Link text check
            links = soup.find_all("a", href=True)
            vague_link_texts = ["click here", "read more", "more", "here", "link"]
            vague_links = [
                link
                for link in links
                if link.get_text().lower().strip() in vague_link_texts
            ]
            if vague_links:
                _safe_append(warnings_list,
                    f"{len(vague_links)} links with vague text (e.g., 'click here')"
                )

            # Calculate basic accessibility score
            total_checks = 6  # Number of accessibility checks
            issues_weight = 2
            warnings_weight = 1

            penalty = (
                _safe_len(issues_list) * issues_weight
                + _safe_len(warnings_list) * warnings_weight
            )
            max_penalty = total_checks * issues_weight

            accessibility["score"] = max(0, 100 - (penalty / max_penalty * 100))

            return accessibility

        except Exception as e:
            logger.error(f"Accessibility check failed: {e}")
            return {"error": str(e)}

    def _check_best_practices(
        self, soup: Any, html_content: str  # type: ignore[misc] - BeautifulSoup typing complex
    ) -> Dict[str, Any]:
        """Check HTML best practices."""
        best_practices: Dict[str, Any] = {
            "issues": [],
            "warnings": [],
            "good_practices": [],
            "score": 0,
        }
        
        # Ensure list fields are properly typed
        issues_list = _ensure_list_field(best_practices, "issues")
        warnings_list = _ensure_list_field(best_practices, "warnings")
        good_practices_list = _ensure_list_field(best_practices, "good_practices")

        try:
            # Meta viewport check
            viewport_meta = soup.find("meta", attrs={"name": "viewport"})
            if not viewport_meta:
                _safe_append(warnings_list,
                    "Missing viewport meta tag for mobile responsiveness"
                )
            else:
                _safe_append(good_practices_list, "Has viewport meta tag")

            # Character encoding check
            charset_meta = soup.find("meta", attrs={"charset": True}) or soup.find(
                "meta", attrs={"http-equiv": "Content-Type"}
            )
            if not charset_meta:
                _safe_append(warnings_list,
                    "Missing character encoding declaration"
                )
            else:
                _safe_append(good_practices_list,
                    "Has character encoding declaration"
                )

            # Title tag check
            title = soup.find("title")
            if not title or not title.get_text().strip():
                _safe_append(issues_list, "Missing or empty title tag")
            elif len(title.get_text()) > 60:
                _safe_append(warnings_list,
                    "Title tag is too long (>60 characters)"
                )
            else:
                _safe_append(good_practices_list, "Has appropriate title tag")

            # Meta description check
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if not meta_desc:
                _safe_append(warnings_list, "Missing meta description")
            elif len(meta_desc.get("content", "")) > 160:
                _safe_append(warnings_list,
                    "Meta description is too long (>160 characters)"
                )
            else:
                _safe_append(good_practices_list, "Has meta description")

            # Semantic HTML check
            semantic_tags = soup.find_all(
                ["header", "nav", "main", "section", "article", "aside", "footer"]
            )
            if semantic_tags:
                _safe_append(good_practices_list, "Uses semantic HTML5 elements")
            else:
                _safe_append(warnings_list,
                    "Consider using semantic HTML5 elements"
                )

            # External resource optimization
            external_scripts = soup.find_all("script", src=True)
            external_styles = soup.find_all("link", {"rel": "stylesheet"})

            if len(external_scripts) + len(external_styles) > 10:
                _safe_append(warnings_list,
                    "Many external resources - consider bundling"
                )

            # Inline styles check
            elements_with_style = soup.find_all(attrs={"style": True})
            if elements_with_style:
                _safe_append(warnings_list,
                    f"{len(elements_with_style)} elements with inline styles"
                )

            # Calculate best practices score
            total_checks = 7
            issues_weight = 3
            warnings_weight = 1

            penalty = (
                _safe_len(issues_list) * issues_weight
                + _safe_len(warnings_list) * warnings_weight
            )
            max_penalty = total_checks * issues_weight

            best_practices["score"] = max(0, 100 - (penalty / max_penalty * 100))

            return best_practices

        except Exception as e:
            logger.error(f"Best practices check failed: {e}")
            return {"error": str(e)}

    def _analyze_seo(self, soup: Any) -> Dict[str, Any]:  # type: ignore[misc] - BeautifulSoup typing complex
        """Analyze SEO-related aspects."""
        seo: Dict[str, Any] = {"issues": [], "warnings": [], "good_practices": [], "score": 0}
        
        # Ensure list fields are properly typed
        issues_list = _ensure_list_field(seo, "issues")
        warnings_list = _ensure_list_field(seo, "warnings")
        good_practices_list = _ensure_list_field(seo, "good_practices")

        try:
            # Title optimization
            title = soup.find("title")
            if title:
                title_text = title.get_text().strip()
                if 30 <= len(title_text) <= 60:
                    _safe_append(good_practices_list, "Title length is optimal")
                elif len(title_text) < 30:
                    _safe_append(warnings_list, "Title is too short for SEO")
                else:
                    _safe_append(warnings_list, "Title is too long for SEO")

            # Heading structure for SEO
            h1_tags = soup.find_all("h1")
            if len(h1_tags) == 1:
                _safe_append(good_practices_list, "Has exactly one H1 tag")
            elif len(h1_tags) == 0:
                _safe_append(issues_list, "Missing H1 tag")
            else:
                _safe_append(warnings_list, "Multiple H1 tags found")

            # Image SEO
            images = soup.find_all("img")
            images_without_alt = [img for img in images if not img.get("alt")]
            if images and not images_without_alt:
                _safe_append(good_practices_list, "All images have alt attributes for SEO")

            # Internal linking
            internal_links = soup.find_all("a", href=re.compile(r"^[^http]"))
            if internal_links:
                _safe_append(good_practices_list, "Has internal links")

            # Calculate SEO score
            total_checks = 4
            issues_weight = 3
            warnings_weight = 1

            penalty = (
                _safe_len(issues_list) * issues_weight
                + _safe_len(warnings_list) * warnings_weight
            )
            max_penalty = total_checks * issues_weight

            seo["score"] = max(0, 100 - (penalty / max_penalty * 100))

            return seo

        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {"error": str(e)}

    def _generate_html_summary(
        self, validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall HTML validation summary."""
        summary: Dict[str, Any] = {
            "status": "unknown",
            "errors": 0,
            "warnings": 0,
            "overall_score": 0,
            "recommendations": [],
        }
        
        # Ensure list field is properly typed
        recommendations_list = _ensure_list_field(summary, "recommendations")

        try:
            # Count issues
            for section in [
                "html5_validation",
                "accessibility_check",
                "best_practices",
                "seo_analysis",
            ]:
                if (
                    section in validation_results
                    and "error" not in validation_results[section]
                ):
                    section_data = validation_results[section]
                    summary["errors"] += _safe_len(section_data.get("issues", []))
                    summary["warnings"] += _safe_len(section_data.get("warnings", []))

            # Calculate overall score
            scores = []
            for section in ["accessibility_check", "best_practices", "seo_analysis"]:
                if (
                    section in validation_results
                    and "score" in validation_results[section]
                ):
                    scores.append(validation_results[section]["score"])

            if scores:
                summary["overall_score"] = sum(scores) / len(scores)

            # Determine status
            if summary["errors"] == 0 and summary["warnings"] <= 2:
                summary["status"] = "excellent"
            elif summary["errors"] <= 1 and summary["warnings"] <= 5:
                summary["status"] = "good"
            elif summary["errors"] <= 3 and summary["warnings"] <= 10:
                summary["status"] = "fair"
            else:
                summary["status"] = "needs_improvement"

            # Generate recommendations
            if summary["errors"] > 0:
                _safe_append(recommendations_list, "Fix HTML validation errors")

            if "accessibility_check" in validation_results:
                acc_score = validation_results["accessibility_check"].get("score", 0)
                if acc_score < 80:
                    _safe_append(recommendations_list,
                        "Improve accessibility compliance"
                    )

            if "best_practices" in validation_results:
                bp_score = validation_results["best_practices"].get("score", 0)
                if bp_score < 80:
                    _safe_append(recommendations_list, "Follow HTML best practices")

            if "seo_analysis" in validation_results:
                seo_score = validation_results["seo_analysis"].get("score", 0)
                if seo_score < 80:
                    _safe_append(recommendations_list, "Optimize for search engines")

            return summary

        except Exception as e:
            logger.error(f"HTML summary generation failed: {e}")
            return {"error": str(e)}


class CSSAnalyzer:
    """CSS analysis with validation and best practices checking."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the CSS analyzer."""
        self.config = config or {}
        self.tools_available = web_tools_available

        # Configure cssutils to reduce logging - disable due to type checker issues
        # if self.tools_available and cssutils is not None:
        #     cssutils.log.setLevel(logging.ERROR)

        logger.info(
            f"CSS analyzer initialized (tools available: {self.tools_available})"
        )

    def analyze_css(self, file_path: str, css_content: str) -> Dict[str, Any]:  # type: ignore[misc] - Complex return structure
        """Analyze CSS for validation and best practices."""
        if not self.tools_available:
            return {"error": "CSS analysis tools not available"}

        analysis_results: Dict[str, Any] = {
            "file_path": file_path,
            "validation": {},
            "best_practices": {},
            "performance": {},
            "summary": {},
        }

        try:
            # CSS validation using cssutils
            analysis_results["validation"] = self._validate_css(css_content)

            # Best practices analysis
            analysis_results["best_practices"] = self._check_css_best_practices(
                css_content
            )

            # Performance analysis
            analysis_results["performance"] = self._analyze_css_performance(css_content)

            # Generate summary
            analysis_results["summary"] = self._generate_css_summary(analysis_results)

            return analysis_results

        except Exception as e:
            logger.error(f"CSS analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _validate_css(self, css_content: str) -> dict[str, Any]:
        """Validate CSS syntax and structure."""
        try:
            # Parse CSS with cssutils
            sheet = cssutils.parseString(css_content)

            validation: Dict[str, Any] = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "rules_count": len(sheet.cssRules),
                "at_rules": 0,
                "style_rules": 0,
            }

            # Count different rule types
            for rule in sheet.cssRules:
                if rule.type == rule.STYLE_RULE:
                    validation["style_rules"] += 1
                elif rule.type in [
                    rule.MEDIA_RULE,
                    rule.IMPORT_RULE,
                    rule.FONT_FACE_RULE,
                ]:
                    validation["at_rules"] += 1

            return validation

        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "rules_count": 0,
            }

    def _check_css_best_practices(self, css_content: str) -> dict[str, Any]:
        """Check CSS best practices."""
        best_practices: Dict[str, Any] = {
            "issues": [],
            "warnings": [],
            "good_practices": [],
            "score": 0,
        }

        try:
            # Check for !important overuse
            important_count = len(re.findall(r"!important", css_content, re.IGNORECASE))
            total_declarations = len(re.findall(r"[^{}]+:[^{}]+;", css_content))

            if important_count > 0:
                important_ratio = important_count / max(total_declarations, 1)
                if important_ratio > 0.1:
                    best_practices["issues"].append(
                        f"Overuse of !important ({important_count} instances)"
                    )
                elif important_count > 5:
                    best_practices["warnings"].append(
                        f"Consider reducing !important usage ({important_count} instances)"
                    )
            else:
                best_practices["good_practices"].append("No !important declarations")

            # Check for CSS organization
            if "@media" in css_content:
                best_practices["good_practices"].append(
                    "Uses media queries for responsiveness"
                )

            if "--" in css_content:
                best_practices["good_practices"].append(
                    "Uses CSS custom properties (variables)"
                )

            # Check for modern CSS features
            modern_features = [
                "flexbox",
                "grid",
                "transform",
                "transition",
                "animation",
            ]
            used_features = [
                feature for feature in modern_features if feature in css_content.lower()
            ]

            if used_features:
                best_practices["good_practices"].append(
                    f"Uses modern CSS features: {', '.join(used_features)}"
                )

            # Check for vendor prefixes (might indicate older code)
            vendor_prefixes = re.findall(r"-(?:webkit|moz|ms|o)-", css_content)
            if vendor_prefixes:
                best_practices["warnings"].append(
                    f"Contains vendor prefixes ({len(set(vendor_prefixes))} unique)"
                )

            # Calculate score
            total_checks = 4
            issues_weight = 3
            warnings_weight = 1

            penalty = (
                len(best_practices["issues"]) * issues_weight
                + len(best_practices["warnings"]) * warnings_weight
            )
            max_penalty = total_checks * issues_weight

            best_practices["score"] = max(0, 100 - (penalty / max_penalty * 100))

            return best_practices

        except Exception as e:
            logger.error(f"CSS best practices check failed: {e}")
            return {"error": str(e)}

    def _analyze_css_performance(self, css_content: str) -> dict[str, Any]:
        """Analyze CSS for performance issues."""
        performance: Dict[str, Any] = {
            "issues": [],
            "warnings": [],
            "good_practices": [],
            "metrics": {},
        }

        try:
            # File size analysis
            file_size = len(css_content.encode("utf-8"))
            performance["metrics"]["file_size_bytes"] = file_size
            performance["metrics"]["file_size_kb"] = round(file_size / 1024, 2)

            if file_size > 100000:  # 100KB
                performance["warnings"].append(
                    f"Large CSS file ({performance['metrics']['file_size_kb']}KB)"
                )

            # Selector complexity analysis
            complex_selectors = re.findall(r"[^{}]+{", css_content)
            deeply_nested = [sel for sel in complex_selectors if sel.count(" ") > 4]

            if deeply_nested:
                performance["warnings"].append(
                    f"Deeply nested selectors found ({len(deeply_nested)})"
                )

            # Universal selector usage
            universal_selectors = re.findall(r"\*\s*{", css_content)
            if universal_selectors:
                performance["warnings"].append(
                    "Universal selector (*) usage can impact performance"
                )

            # Duplicate rules detection (basic)
            rules = re.findall(r"([^{}]+){([^{}]*)}", css_content)
            rule_counts = {}
            for selector, _declarations in rules:
                key = selector.strip()
                rule_counts[key] = rule_counts.get(key, 0) + 1

            duplicates = {k: v for k, v in rule_counts.items() if v > 1}
            if duplicates:
                performance["warnings"].append(
                    f"Duplicate selectors found ({len(duplicates)})"
                )

            return performance

        except Exception as e:
            logger.error(f"CSS performance analysis failed: {e}")
            return {"error": str(e)}

    def _generate_css_summary(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Generate CSS analysis summary."""
        summary: Dict[str, Any] = {
            "status": "unknown",
            "total_issues": 0,
            "overall_score": 0,
            "recommendations": [],
        }

        try:
            # Count issues
            for section in ["validation", "best_practices", "performance"]:
                if (
                    section in analysis_results
                    and "error" not in analysis_results[section]
                ):
                    section_data = analysis_results[section]
                    summary["total_issues"] += len(section_data.get("issues", []))
                    summary["total_issues"] += len(section_data.get("warnings", []))

            # Calculate overall score
            scores = []
            if (
                "best_practices" in analysis_results
                and "score" in analysis_results["best_practices"]
            ):
                scores.append(analysis_results["best_practices"]["score"])

            # Add validation score
            if "validation" in analysis_results:
                val_data = analysis_results["validation"]
                if val_data.get("valid", False):
                    scores.append(100)
                else:
                    scores.append(max(0, 100 - len(val_data.get("errors", [])) * 20))

            if scores:
                summary["overall_score"] = sum(scores) / len(scores)

            # Determine status
            if summary["total_issues"] <= 2:
                summary["status"] = "excellent"
            elif summary["total_issues"] <= 5:
                summary["status"] = "good"
            elif summary["total_issues"] <= 10:
                summary["status"] = "fair"
            else:
                summary["status"] = "needs_improvement"

            # Generate recommendations
            if "validation" in analysis_results and not analysis_results[
                "validation"
            ].get("valid", True):
                summary["recommendations"].append("Fix CSS syntax errors")

            if "best_practices" in analysis_results:
                bp_score = analysis_results["best_practices"].get("score", 100)
                if bp_score < 80:
                    summary["recommendations"].append("Follow CSS best practices")

            if "performance" in analysis_results:
                perf_data = analysis_results["performance"]
                if len(perf_data.get("warnings", [])) > 0:
                    summary["recommendations"].append(
                        "Optimize CSS for better performance"
                    )

            return summary

        except Exception as e:
            logger.error(f"CSS summary generation failed: {e}")
            return {"error": str(e)}


class JSAnalyzer:
    """JavaScript basic analysis and structure checking."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the JavaScript analyzer."""
        self.config = config or {}
        logger.info("JavaScript analyzer initialized")

    def analyze_javascript(self, file_path: str, js_content: str) -> Dict[str, Any]:  # type: ignore[misc] - Complex return structure
        """Analyze JavaScript for basic syntax and best practices."""
        analysis_results: Dict[str, Any] = {
            "file_path": file_path,
            "syntax_check": {},
            "best_practices": {},
            "structure_analysis": {},
            "summary": {},
        }

        try:
            # Basic syntax checking
            analysis_results["syntax_check"] = self._check_js_syntax(js_content)

            # Best practices analysis
            analysis_results["best_practices"] = self._check_js_best_practices(
                js_content
            )

            # Structure analysis
            analysis_results["structure_analysis"] = self._analyze_js_structure(
                js_content
            )

            # Generate summary
            analysis_results["summary"] = self._generate_js_summary(analysis_results)

            return analysis_results

        except Exception as e:
            logger.error(f"JavaScript analysis failed for {file_path}: {e}")
            return {"error": str(e)}

    def _check_js_syntax(self, js_content: str) -> dict[str, Any]:
        """Basic JavaScript syntax checking."""
        syntax_check: Dict[str, Any] = {"issues": [], "warnings": [], "score": 100}

        try:
            # Basic bracket/parenthesis matching
            brackets = {"(": ")", "[": "]", "{": "}"}
            stack = []

            in_string = False
            string_char = None
            escape_next = False

            for i, char in enumerate(js_content):
                if escape_next:
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                if char in ['"', "'"]:
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                    continue

                if not in_string:
                    if char in brackets:
                        stack.append((char, i))
                    elif char in brackets.values():
                        if not stack:
                            syntax_check["issues"].append(
                                f"Unmatched closing '{char}' at position {i}"
                            )
                        else:
                            opening, pos = stack.pop()
                            if brackets[opening] != char:
                                syntax_check["issues"].append(
                                    f"Mismatched brackets: '{opening}' at {pos} and '{char}' at {i}"
                                )

            # Check for unmatched opening brackets
            for opening, pos in stack:
                syntax_check["issues"].append(
                    f"Unmatched opening '{opening}' at position {pos}"
                )

            # Check for common syntax issues
            if "function(" in js_content.replace(" ", ""):
                syntax_check["warnings"].append(
                    "Missing space after 'function' keyword"
                )

            # Check for semicolon usage
            lines = js_content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith("//") and not line.startswith("/*"):
                    if (
                        line.endswith("{")
                        or line.endswith("}")
                        or line.startswith("if")
                        or line.startswith("for")
                        or line.startswith("while")
                        or line.startswith("function")
                    ):
                        continue
                    if not line.endswith(";") and not line.endswith(","):
                        syntax_check["warnings"].append(
                            f"Missing semicolon on line {i + 1}"
                        )
                        break  # Only report first few to avoid spam

            # Calculate syntax score
            penalty = (
                len(syntax_check["issues"]) * 20 + len(syntax_check["warnings"]) * 5
            )
            syntax_check["score"] = max(0, 100 - penalty)

            return syntax_check

        except Exception as e:
            logger.error(f"JavaScript syntax check failed: {e}")
            return {"error": str(e)}

    def _check_js_best_practices(self, js_content: str) -> dict[str, Any]:
        """Check JavaScript best practices."""
        best_practices: Dict[str, Any] = {
            "issues": [],
            "warnings": [],
            "good_practices": [],
            "score": 0,
        }

        try:
            # Strict mode check
            if "'use strict'" in js_content or '"use strict"' in js_content:
                best_practices["good_practices"].append("Uses strict mode")
            else:
                best_practices["warnings"].append("Consider using strict mode")

            # Variable declaration practices
            var_count = len(re.findall(r"\bvar\s+", js_content))
            let_count = len(re.findall(r"\blet\s+", js_content))
            const_count = len(re.findall(r"\bconst\s+", js_content))

            if var_count > 0 and (let_count > 0 or const_count > 0):
                best_practices["warnings"].append(
                    "Mix of var and let/const - prefer let/const"
                )
            elif let_count > 0 or const_count > 0:
                best_practices["good_practices"].append(
                    "Uses modern variable declarations (let/const)"
                )

            # Function declaration styles
            len(re.findall(r"\bfunction\s+\w+", js_content))
            arrow_functions = len(re.findall(r"=>", js_content))

            if arrow_functions > 0:
                best_practices["good_practices"].append("Uses arrow functions")

            # Error handling
            try_catch = len(re.findall(r"\btry\s*{", js_content))
            if try_catch > 0:
                best_practices["good_practices"].append("Includes error handling")
            else:
                best_practices["warnings"].append("No error handling found")

            # Console.log usage (should be removed in production)
            console_logs = len(re.findall(r"console\.log", js_content, re.IGNORECASE))
            if console_logs > 3:
                best_practices["warnings"].append(
                    f"Many console.log statements ({console_logs}) - remove for production"
                )

            # Global variables (basic check)
            if re.search(r"^\s*var\s+\w+", js_content, re.MULTILINE):
                best_practices["warnings"].append(
                    "Potential global variables - use modules or namespacing"
                )

            # Calculate score
            total_checks = 6
            issues_weight = 3
            warnings_weight = 1

            penalty = (
                len(best_practices["issues"]) * issues_weight
                + len(best_practices["warnings"]) * warnings_weight
            )
            max_penalty = total_checks * issues_weight

            best_practices["score"] = max(0, 100 - (penalty / max_penalty * 100))

            return best_practices

        except Exception as e:
            logger.error(f"JavaScript best practices check failed: {e}")
            return {"error": str(e)}

    def _analyze_js_structure(self, js_content: str) -> dict[str, Any]:
        """Analyze JavaScript code structure."""
        structure: Dict[str, Any] = {
            "complexity_estimate": "low",
            "function_count": 0,
            "class_count": 0,
            "estimated_lines_of_code": 0,
            "has_modules": False,
            "has_async_code": False,
        }

        try:
            # Count functions
            function_patterns = [
                r"\bfunction\s+\w+",  # function declarations
                r"\w+\s*:\s*function",  # object methods
                r"=>",  # arrow functions
            ]

            for pattern in function_patterns:
                structure["function_count"] += len(re.findall(pattern, js_content))

            # Count classes
            structure["class_count"] = len(re.findall(r"\bclass\s+\w+", js_content))

            # Estimate lines of code (excluding empty lines and comments)
            lines = js_content.split("\n")
            loc = 0
            for line in lines:
                line = line.strip()
                if line and not line.startswith("//") and not line.startswith("/*"):
                    loc += 1
            structure["estimated_lines_of_code"] = loc

            # Check for modules
            if (
                "import" in js_content
                or "export" in js_content
                or "require(" in js_content
            ):
                structure["has_modules"] = True

            # Check for async code
            if (
                "async" in js_content
                or "await" in js_content
                or "Promise" in js_content
            ):
                structure["has_async_code"] = True

            # Estimate complexity
            function_count = structure.get("function_count", 0)
            class_count = structure.get("class_count", 0)
            
            # Ensure we have integers for the sum
            if not isinstance(function_count, int):
                function_count = 0
            if not isinstance(class_count, int):
                class_count = 0
                
            complexity_indicators = [
                len(re.findall(r"\bif\b", js_content)),
                len(re.findall(r"\bfor\b", js_content)),
                len(re.findall(r"\bwhile\b", js_content)),
                len(re.findall(r"\bswitch\b", js_content)),
                function_count,
                class_count,
            ]

            total_complexity = sum(complexity_indicators)
            if total_complexity < 10:
                structure["complexity_estimate"] = "low"
            elif total_complexity < 25:
                structure["complexity_estimate"] = "moderate"
            else:
                structure["complexity_estimate"] = "high"

            return structure

        except Exception as e:
            logger.error(f"JavaScript structure analysis failed: {e}")
            return {"error": str(e)}

    def _generate_js_summary(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Generate JavaScript analysis summary."""
        summary: Dict[str, Any] = {
            "quality": "unknown",
            "total_issues": 0,
            "overall_score": 0,
            "recommendations": [],
        }

        try:
            # Count issues
            for section in ["syntax_check", "best_practices"]:
                if (
                    section in analysis_results
                    and "error" not in analysis_results[section]
                ):
                    section_data = analysis_results[section]
                    summary["total_issues"] += len(section_data.get("issues", []))
                    summary["total_issues"] += len(section_data.get("warnings", []))

            # Calculate overall score
            scores = []
            for section in ["syntax_check", "best_practices"]:
                if section in analysis_results and "score" in analysis_results[section]:
                    scores.append(analysis_results[section]["score"])

            if scores:
                summary["overall_score"] = sum(scores) / len(scores)

            # Determine quality
            if summary["total_issues"] <= 2 and summary["overall_score"] >= 90:
                summary["quality"] = "excellent"
            elif summary["total_issues"] <= 5 and summary["overall_score"] >= 70:
                summary["quality"] = "good"
            elif summary["total_issues"] <= 10 and summary["overall_score"] >= 50:
                summary["quality"] = "fair"
            else:
                summary["quality"] = "needs_improvement"

            # Generate recommendations
            if "syntax_check" in analysis_results:
                syntax_score = analysis_results["syntax_check"].get("score", 100)
                if syntax_score < 80:
                    summary["recommendations"].append("Fix JavaScript syntax issues")

            if "best_practices" in analysis_results:
                bp_score = analysis_results["best_practices"].get("score", 100)
                if bp_score < 70:
                    summary["recommendations"].append(
                        "Follow JavaScript best practices"
                    )

            if "structure_analysis" in analysis_results:
                structure = analysis_results["structure_analysis"]
                if structure.get("complexity_estimate") == "high":
                    summary["recommendations"].append(
                        "Consider refactoring complex code"
                    )

                if (
                    not structure.get("has_modules")
                    and structure.get("estimated_lines_of_code", 0) > 100
                ):
                    summary["recommendations"].append(
                        "Consider using modules for better organization"
                    )

            return summary

        except Exception as e:
            logger.error(f"JavaScript summary generation failed: {e}")
            return {"error": str(e)}


# Add datetime import at module level
from datetime import datetime
