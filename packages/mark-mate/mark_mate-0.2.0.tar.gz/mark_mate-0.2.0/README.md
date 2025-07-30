# MarkMate
**Your AI Teaching Assistant for Assignments and Assessment**

[![PyPI version](https://badge.fury.io/py/mark-mate.svg)](https://badge.fury.io/py/mark-mate)
[![Python versions](https://img.shields.io/pypi/pyversions/mark-mate.svg)](https://pypi.org/project/mark-mate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive system for processing, consolidating, and grading student submissions with support for multiple content types, GitHub repository analysis, WordPress assignments, and AI-powered assessment using **Claude 3.5 Sonnet**, **GPT-4o**, and **Google Gemini** through a unified LiteLLM interface.

## 🚀 Quick Start

### Installation

```bash
pip install mark-mate
```

### GUI Application (Recommended)

Launch the cross-platform desktop application:

```bash
mark-mate-gui
```

The GUI provides an intuitive interface for all MarkMate functionality with:
- **Visual workflow navigation** between consolidate → scan → extract → grade
- **Progress tracking** for long-running operations  
- **Interactive configuration** builder for grading settings
- **Real-time status updates** and error handling
- **Cross-platform support** (Windows, macOS, Linux)

### CLI Usage

```bash
# Consolidate submissions
mark-mate consolidate raw_submissions/

# Scan for GitHub URLs
mark-mate scan processed_submissions/ --output github_urls.txt

# Extract content with analysis
mark-mate extract processed_submissions/ --github-urls github_urls.txt --output extracted.json

# Grade submissions (uses auto-configuration)
mark-mate grade extracted.json assignment_spec.txt --output results.json

# Use custom grading configuration
mark-mate grade extracted.json assignment_spec.txt --config grading_config.yaml
```

### API Keys Setup

```bash
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
export GEMINI_API_KEY="your_gemini_key"  # or GOOGLE_API_KEY
```

## 📋 System Overview

MarkMate consists of four main components accessible via **GUI**, **CLI**, or **Python API**:

### 1. **Consolidate** - File organization and filtering
- Groups files by student ID with intelligent pattern matching
- Extracts zip archives with conflict resolution
- Filters Mac system files (.DS_Store, resource forks, __MACOSX)
- WordPress mode for UpdraftPlus backup organization

### 2. **Scan** - GitHub repository detection
- Comprehensive URL detection with regex patterns
- Scans text files within zip archives
- Enhanced encoding support for international students
- Creates editable student_id:repo_url mapping files

### 3. **Extract** - Multi-format content processing
- **Document Processing**: PDF, DOCX, TXT, MD, Jupyter notebooks
- **Code Analysis**: Python, HTML, CSS, JavaScript, React/TypeScript
- **GitHub Analysis**: Commit history, development patterns, repository quality
- **WordPress Processing**: Themes, plugins, database, AI detection
- **Enhanced Encoding**: 18+ encodings for international students

### 4. **Grade** - AI-powered assessment
- **Multi-LLM Grading**: Claude 3.5 Sonnet + GPT-4o + Google Gemini via LiteLLM
- **Enhanced Multi-Run System**: Statistical averaging with configurable runs per grader
- **Flexible Configuration**: YAML-based grader setup with weights and priorities
- **Advanced Statistics**: Multiple averaging methods, confidence scoring, variance analysis
- **Cost Controls**: Budget limits, rate limiting, and usage tracking
- **Automatic Rubric Extraction**: From assignment specifications
- **Comprehensive Feedback**: Incorporating all analysis types

## 🌟 Key Features

- **Cross-Platform Desktop GUI**: Native desktop application powered by Flutter for Windows, macOS, and Linux
- **Multi-Format Support**: PDF, DOCX, TXT, MD, Jupyter notebooks, Python code, web files (HTML/CSS/JS), React/TypeScript projects
- **GitHub Repository Analysis**: Commit history, development patterns, repository quality assessment
- **Enhanced Encoding Support**: Optimized for ESL students with automatic encoding detection (UTF-8, UTF-16, CP1252, Latin-1, and more)
- **WordPress Assignment Processing**: Complete backup analysis with theme, plugin, and database evaluation
- **Multi-LLM Grading**: Claude 3.5 Sonnet + GPT-4o + Google Gemini with statistical aggregation and confidence scoring
- **Mac System File Filtering**: Automatic removal of .DS_Store, resource forks, and __MACOSX directories

## 🔗 LiteLLM Integration

MarkMate leverages [LiteLLM](https://github.com/BerriAI/litellm) for unified access to multiple LLM providers:

**Unified Interface Benefits:**
- **Consistent API**: Single interface for Claude, OpenAI, and Gemini
- **Error Handling**: Standardized exceptions across all providers  
- **Token Tracking**: Unified usage monitoring and cost calculation
- **Rate Limiting**: Built-in respect for provider-specific limits
- **Future-Proof**: Easy addition of 100+ supported providers

**Supported Models:**
```python
# Anthropic
"claude-3-5-sonnet", "claude-3-sonnet", "claude-3-haiku"

# OpenAI  
"gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"

# Google Gemini
"gemini-pro", "gemini-1.5-pro", "gemini-2.0-flash"
```

**Cost Optimization:**
- Automatic cost estimation before processing
- Per-student budget controls with early termination
- Real-time usage tracking across all providers
- Intelligent model selection based on cost/quality trade-offs

## 🖥️ CLI Interface

### Consolidate Command
```bash
mark-mate consolidate [OPTIONS] FOLDER_PATH

Options:
  --no-zip              Discard zip files instead of extracting
  --wordpress           Enable WordPress-specific processing
  --keep-mac-files      Preserve Mac system files
  --output-dir TEXT     Output directory (default: processed_submissions)
```

### Scan Command
```bash
mark-mate scan [OPTIONS] SUBMISSIONS_FOLDER

Options:
  --output TEXT         Output file for URL mappings (default: github_urls.txt)
  --encoding TEXT       Text encoding (default: utf-8)
```

### Extract Command
```bash
mark-mate extract [OPTIONS] SUBMISSIONS_FOLDER

Options:
  --output TEXT         Output JSON file (default: extracted_content.json)
  --wordpress           Enable WordPress processing
  --github-urls TEXT    GitHub URL mapping file
  --dry-run             Preview processing without extraction
  --max-students INT    Limit number of students (for testing)
```

### Grade Command
```bash
mark-mate grade [OPTIONS] EXTRACTED_CONTENT ASSIGNMENT_SPEC

Options:
  --output TEXT         Output JSON file (default: grading_results.json)
  --rubric TEXT         Separate rubric file
  --max-students INT    Limit number of students
  --dry-run             Preview grading without API calls
  --config TEXT         Path to YAML grading configuration file (optional - uses defaults if not provided)
```

## 🐍 Python API

### Library Usage

```python
from mark_mate import (
    EnhancedGradingSystem, LLMProvider,
    AssignmentProcessor, ContentAnalyzer, GradingConfigManager
)

# Process submissions
processor = AssignmentProcessor()
result = processor.process_submission(
    "/path/to/submission", 
    "123", 
    wordpress=True,
    github_url="https://github.com/user/repo"
)

# Grading with custom configuration
grader = EnhancedGradingSystem("grading_config.yaml")
grade_result = grader.grade_submission(
    student_data=result,
    assignment_spec="Assignment requirements..."
)

# Grading with auto-configuration (no config file)
auto_grader = EnhancedGradingSystem()  # Uses defaults based on available API keys
auto_result = auto_grader.grade_submission(
    student_data=result,
    assignment_spec="Assignment requirements..."
)

# Direct LLM provider usage
llm_provider = LLMProvider()
llm_result = llm_provider.grade_submission(
    provider="gemini",
    model="gemini-1.5-pro", 
    prompt="Grade this submission..."
)

# Generate configuration programmatically
config_manager = GradingConfigManager()
config = config_manager.load_config()  # Load defaults
config.save_default_config("my_config.yaml")

# Analyze content
analyzer = ContentAnalyzer()
summary = analyzer.generate_submission_summary(
    result["content"], 
    result["metadata"]
)
```

## 🔄 Complete Workflows

### Programming Assignment with GitHub
```bash
# 1. Consolidate submissions
mark-mate consolidate programming_submissions/

# 2. Scan for GitHub URLs
mark-mate scan processed_submissions/ --output github_urls.txt

# 3. Extract with comprehensive analysis
mark-mate extract processed_submissions/ --github-urls github_urls.txt

# 4. Grade with repository analysis
mark-mate grade extracted_content.json programming_assignment.txt
```

### WordPress Assignment
```bash
# 1. Consolidate WordPress backups
mark-mate consolidate wordpress_submissions/ --wordpress

# 2. Extract WordPress content
mark-mate extract processed_submissions/ --wordpress

# 3. Grade with WordPress criteria
mark-mate grade extracted_content.json wordpress_assignment.txt
```

### International Student Support
```bash
# Enhanced encoding detection handles international submissions automatically
mark-mate consolidate international_submissions/
mark-mate extract processed_submissions/  # Auto-detects 18+ encodings
mark-mate grade extracted_content.json assignment.txt
```

### Advanced Grading Workflows
```bash
# Auto-configuration based on available API keys
mark-mate grade extracted_content.json assignment.txt

# Custom configuration with multiple providers and runs
mark-mate grade extracted_content.json assignment.txt --config grading_config.yaml

# Generate configuration templates
mark-mate generate-config --template minimal --output simple_config.yaml
mark-mate generate-config --template cost-optimized --output cheap_config.yaml
```

## ⚙️ Configuration Management

### Automatic Configuration
MarkMate automatically creates optimal configurations based on your available API keys:
- **Single Provider**: Uses 3 runs for statistical reliability
- **Multiple Providers**: Uses 1 run each with weighted averaging
- **Cost Optimization**: Chooses appropriate models and limits

### Configuration Templates
Generate ready-to-use configurations:

```bash
# Full-featured with all providers
mark-mate generate-config --template full

# Minimal single-provider setup  
mark-mate generate-config --template minimal

# Cost-optimized for budget constraints
mark-mate generate-config --template cost-optimized

# Single provider focus
mark-mate generate-config --template single-provider --provider anthropic
```

## 🎯 Enhanced Grading System

### Multi-Run Statistical Grading
MarkMate's enhanced grading system provides unprecedented reliability through:

**Statistical Aggregation Methods:**
- **Mean**: Simple average of all runs
- **Median**: Middle value for robustness against outliers
- **Weighted Mean**: Importance-based averaging using grader weights
- **Trimmed Mean**: Removes highest/lowest values before averaging

**Configuration Example:**
```yaml
grading:
  runs_per_grader: 3
  averaging_method: "weighted_mean"
  parallel_execution: true

graders:
  - name: "claude-sonnet"
    provider: "anthropic"
    model: "claude-3-5-sonnet"
    weight: 2.0              # Higher importance
    primary_feedback: true   # Featured feedback
    
  - name: "gpt4o"
    provider: "openai"
    model: "gpt-4o"
    weight: 1.5
    
  - name: "gemini-pro"
    provider: "gemini"
    model: "gemini-1.5-pro"
    weight: 1.0

execution:
  max_cost_per_student: 0.75  # Budget control
  retry_attempts: 3           # Failure handling
```

**Advanced Features:**
- **Confidence Scoring**: Based on inter-grader agreement and variance
- **Cost Controls**: Per-student budget limits and usage tracking
- **Rate Limiting**: Respects API limits for each provider
- **Failure Recovery**: Graceful degradation with retry logic
- **Progress Tracking**: Real-time status for large batches

**Output Example:**
```json
{
  "aggregate": {
    "mark": 87.3,
    "feedback": "Excellent implementation with clear documentation...",
    "confidence": 0.92,
    "graders_used": 3,
    "total_runs": 9
  },
  "grader_results": {
    "claude-sonnet": {
      "aggregated": {"mark": 88.0, "runs_used": 3},
      "weight": 2.0
    }
  }
}
```

## 🌍 Enhanced Support for International Students

### Advanced Encoding Detection
Comprehensive support for ESL (English as a Second Language) students:

**Supported Encodings:**
- **UTF-16**: Windows systems with non-English locales
- **CP1252**: Windows-1252 (Western European, legacy systems)
- **Latin-1**: ISO-8859-1 (European systems, older editors)
- **Regional**: Cyrillic (CP1251), Turkish (CP1254), Chinese (GB2312, Big5), Japanese (Shift_JIS), Korean (EUC-KR)

**Intelligent Fallback Strategy:**
1. Try optimal encoding based on content type
2. Graceful fallback with error handling
3. Preserve international characters and symbols
4. Detailed logging of encoding attempts

## 🐙 GitHub Repository Analysis

### Comprehensive Development Assessment
Analyzes student GitHub repositories to evaluate development processes:

**Repository Analysis Features:**
- **Commit History**: Development timeline, frequency patterns, consistency
- **Message Quality**: Scoring based on descriptiveness and professionalism
- **Development Patterns**: Steady development vs. last-minute work detection
- **Collaboration**: Multi-author analysis, teamwork evaluation
- **Repository Quality**: README, documentation, directory structure
- **Code Organization**: File management, naming conventions, best practices

**Analysis Output Example:**
```json
{
  "github_metrics": {
    "total_commits": 15,
    "development_span_days": 14,
    "commit_message_quality": {
      "score": 89,
      "quality_level": "excellent"
    },
    "consistency_score": 0.86,
    "collaboration_level": "collaborative"
  }
}
```

## 🎯 WordPress Assignment Support

### Static Assessment Capabilities
Assess WordPress assignments without requiring site restoration:

**Technical Implementation:**
- Theme analysis and customization assessment
- Plugin inventory and functionality review
- Database content extraction and analysis
- Security configuration evaluation

**Content Quality Assessment:**
- Blog post count and word count analysis
- Media usage and organization
- User account configuration
- Comment analysis

**AI Integration Detection:**
- Automatic detection of AI-related plugins
- AI keyword analysis in plugin descriptions
- Assessment of AI integration documentation

## 📊 Output and Results

### Extraction Output
```json
{
  "extraction_session": {
    "timestamp": "2025-06-19T10:30:00",
    "total_students": 24,
    "wordpress_mode": true,
    "github_analysis": true
  },
  "students": {
    "123": {
      "content": {...},
      "metadata": {...}
    }
  }
}
```

### Grading Output
```json
{
  "grading_session": {
    "timestamp": "2025-06-19T11:00:00",
    "total_students": 24,
    "providers": ["claude", "openai"]
  },
  "results": {
    "123": {
      "aggregate": {
        "mark": 85,
        "feedback": "Comprehensive feedback...",
        "confidence": 0.95,
        "max_mark": 100
      },
      "providers": {
        "claude": {"mark": 83, "feedback": "..."},
        "openai": {"mark": 87, "feedback": "..."}
      }
    }
  }
}
```

## 🛠️ Development

### Setup Development Environment
```bash
git clone https://github.com/markmate-ai/mark-mate.git
cd mark-mate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black src/
flake8 src/
mypy src/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Adding New Features
1. **Content Extractors**: Follow the `BaseExtractor` pattern in `src/mark_mate/extractors/`
2. **Analysis Capabilities**: Extend existing analyzers or create new ones
3. **LLM Providers**: Add new providers in `src/mark_mate/core/grader.py`
4. **CLI Commands**: Add new commands in `src/mark_mate/cli/`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://mark-mate.readthedocs.io](https://mark-mate.readthedocs.io)
- **GitHub**: [https://github.com/markmate-ai/mark-mate](https://github.com/markmate-ai/mark-mate)
- **PyPI**: [https://pypi.org/project/mark-mate/](https://pypi.org/project/mark-mate/)
- **Issues**: [https://github.com/markmate-ai/mark-mate/issues](https://github.com/markmate-ai/mark-mate/issues)

## 🙏 Acknowledgments

MarkMate is designed for educational assessment purposes. Please ensure compliance with your institution's policies regarding automated grading and student data processing.

---

**MarkMate: Your AI Teaching Assistant for Assignments and Assessment**