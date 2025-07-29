# pytest-html-report

[![PyPI version](https://badge.fury.io/py/pytest-html-report.svg)](https://badge.fury.io/py/pytest-html-report)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-html-report.svg)](https://pypi.org/project/pytest-html-report/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Source Code
[![GitLab](https://img.shields.io/badge/GitLab-Project-blue.svg)](https://gitlab.com/fabdullah230/pytest-html-report)

## Features

- ✅ Structured HTML reports with categorization
- ✅ Support for functional specifications and test categories 
- ✅ Detailed test execution logs with step-by-step tracking
- ✅ Report theme and metadata customization

## Installation

```bash
pip install pytest-html-report
```

## Usage

### Basic Configuration

Create a `pytest_html_report.yml` file in your project root:

```yaml
report:
  title: "My Test Report"
  img_url: "https://your-logo-url.png"
  report_dir: "reports"
  test_environment: "Development"

functional_specs:
  SPEC-001: "User Authentication"
  SPEC-002: "Data Processing"
  SPEC-003: "API Integration"

categories:
  unit: "Unit Tests"
  integration: "Integration Tests"
  regression: "Regression Tests"
```

### Writing Tests

Use the provided markers to add metadata to your tests:

```python
import pytest

@pytest.mark.reporting(
    developer="John Doe",
    functional_specification="SPEC-001",
    test_description="Validate user login flow"
)
@pytest.mark.category("integration", "regression")
def test_user_login(logger):
    """Test user authentication process"""
    logger.step("Setting up test data")
    # Test implementation
    logger.step("Validating results")
    assert True

@pytest.mark.reporting(
    developer="Jane Smith",
    functional_specification=["SPEC-002", "SPEC-003"],
    test_description="Complex data pipeline test"
)
@pytest.mark.category("integration")
def test_data_pipeline(logger):
    """Test data processing pipeline"""
    logger.step("Initializing pipeline")
    # Test implementation
    logger.step("Verifying output")
    assert 1 == 1
    # Test assertions
    logger.assertion("Output 1 matches expected result 1")
```

### Running Tests

Run your tests with pytest as usual:

```bash
pytest 
```

The HTML report will be generated in the configured report directory (default: `reports/`). The report name is the report_date_time.html, e.g., `reports/report_20250622_231929.html`.

## Example Report Output

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center">
    <img src="https://gitlab.com/fabdullah230/pytest-html-report/-/raw/master/docs/assets/report-ss-1.png" width="45%" alt="Report Overview"/>
    <img src="https://gitlab.com/fabdullah230/pytest-html-report/-/raw/master/docs/assets/report-ss-2.png" width="45%" alt="Test Categories"/>
    <img src="https://gitlab.com/fabdullah230/pytest-html-report/-/raw/master/docs/assets/report-ss-3.png" width="45%" alt="Test Details"/>
    <img src="https://gitlab.com/fabdullah230/pytest-html-report/-/raw/master/docs/assets/report-ss-4.png" width="45%" alt="Test Results"/>
</div>

### Available Markers

- `@pytest.mark.reporting`: Add metadata about the test
  - `developer`: Test owner/developer
  - `functional_specification`: Link to functional specs
  - `test_description`: Brief description of the test

- `@pytest.mark.category`: Categorize tests
  - Multiple categories can be specified

### Logging Steps

The plugin provides a `logger` fixture for detailed test steps:

```python
def test_example(logger):
    logger.step("Starting test preparation")
    # Test setup
    logger.step("Executing main test logic")
    # Test execution
    logger.assertion("Asserting result 1 == 1")
    # Assertions
```

### Customizing Report Theme

You can customize the report appearance in your config:

```yaml
theme:
  primary_color: "#0052CC"
  success_bg: "#E3FCEF"
  error_bg: "#FFEBE6"
  warning_bg: "#FFFAE6"
  info_bg: "#DEEBFF"
```

