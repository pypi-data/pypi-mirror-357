import datetime
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from xml.etree.ElementTree import SubElement
import pytest
from _pytest.logging import LogCaptureHandler
from .config import load_config, get_config
from .report_generator import process_test_data, generate_html_from_json

# Configure custom logging levels
STEP_LEVEL = 24
ASSERTION_LEVEL = 25

logging.addLevelName(STEP_LEVEL, "STEP")
logging.addLevelName(ASSERTION_LEVEL, "ASSERTION")


def step(self, message, *args, **kwargs):
    self._log(STEP_LEVEL, message, args, **kwargs)


def assertion_log(self, message, *args, **kwargs):
    self._log(ASSERTION_LEVEL, message, args, **kwargs)


logging.Logger.step = step
logging.Logger.assertion = assertion_log


class StepAssertLogHandler(LogCaptureHandler):
    def __init__(self):
        super().__init__()
        self.step_assert_records = []

    def emit(self, record):
        if record.levelno in {STEP_LEVEL, ASSERTION_LEVEL}:
            if record.levelno == STEP_LEVEL:
                self.step_assert_records.append(["Step", record.getMessage()])
            else:
                self.step_assert_records.append(["Assert", record.getMessage()])


_plugin_initialized = False


def init_plugin():
    """Initialize the pytest-html-report plugin"""
    global _plugin_initialized
    if not _plugin_initialized:
        # Load configuration on initialization
        load_config()
        _plugin_initialized = True


@pytest.fixture
def logger(request):
    """Provides a logger instance for tests with step and assertion methods"""
    logger = logging.getLogger(request.node.name)
    logger.setLevel(logging.DEBUG)

    handler = StepAssertLogHandler()
    logger.addHandler(handler)

    yield logger

    request.node.user_properties.append(("logs", handler.step_assert_records))
    logger.removeHandler(handler)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption("--use-last-checkpoint", action="store_true", default=False,
                     help="Use the last checkpoint file instead of creating a new one")
    parser.addoption("--rerun-failed-tests-only", action="store_true", default=False,
                     help="Rerun only the failed tests from the last checkpoint")


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "reporting: Mark test with reporting metadata"
    )
    config.addinivalue_line(
        "markers", "category: Mark test with categories"
    )


def pytest_sessionstart(session):
    """Initialize checkpoint file at session start"""
    CONFIG = get_config()
    results_dir = Path(CONFIG['report']['report_dir'])
    results_dir.mkdir(exist_ok=True, parents=True)

    env_name = CONFIG['report']['test_environment']
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if session.config.getoption("--use-last-checkpoint"):
        checkpoint_files = list(results_dir.glob(f"{env_name}_checkpoint_*.json"))
        if not checkpoint_files:
            raise ValueError("No checkpoint files found when --use-last-checkpoint was specified.")

        old_checkpoint_file = max(checkpoint_files, key=lambda x: x.stat().st_mtime)
        new_checkpoint_file = results_dir / f"{env_name}_checkpoint_{current_time}.json"

        with open(old_checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
            checkpoint_data['test_status'] = 'ongoing'

        with open(new_checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        old_checkpoint_file.unlink()
        checkpoint_file = new_checkpoint_file
    else:
        checkpoint_file = results_dir / f"{env_name}_checkpoint_{current_time}.json"
        initial_data = {
            "specs": {},
            "functional_spec_count": {},
            "testsuites": [{"cases": []}],
            "test_environment": env_name,
            "timestamp": datetime.datetime.now().strftime("%d %b %Y, %H:%M"),
            "img_url": CONFIG['report']['img_url'],
            "test_status": "ongoing",
            "report_title": CONFIG['report']['title']
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(initial_data, f, indent=2)

    session.config._checkpoint_file = checkpoint_file


def pytest_sessionfinish(session, exitstatus):
    """Update checkpoint and generate HTML report at session end"""
    if "junitxml" in session.config.pluginmanager.get_plugins():
        xml = session.config._xml
        for test in xml.node_reporter.values():
            testcase_xml = xml.testcase_node_reporter(test.nodeid)
            for name, value in test.user_properties:
                property_xml = SubElement(testcase_xml, "property", name=name, value=value)
                property_xml.text = value
        xml.write_xml()

    checkpoint_file = getattr(session.config, "_checkpoint_file", None)
    if checkpoint_file and checkpoint_file.exists():
        # Update test status to complete
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        data['test_status'] = 'complete'
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Generate HTML report
        CONFIG = get_config()
        results_dir = Path(CONFIG['report']['report_dir'])
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = results_dir / f"report_{timestamp}.html"

        try:
            generate_html_from_json(str(checkpoint_file), str(html_file))
            print(f"\n{'='*60}")
            print(f"HTML Report Generated: {html_file}")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"\nError generating HTML report: {str(e)}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add reporting metadata to test results"""
    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)

    # Collect all markers
    reporting_marker = item.get_closest_marker("reporting")
    category_marker = item.get_closest_marker("category")

    if not hasattr(report, "user_properties"):
        report.user_properties = []

    # Handle reporting marker
    if reporting_marker:
        developer = reporting_marker.kwargs.get("developer")
        functional_specification = reporting_marker.kwargs.get("functional_specification")
        test_description = reporting_marker.kwargs.get("test_description") or reporting_marker.kwargs.get("comment")

        if developer is not None:
            report.user_properties.append(("developer", developer))
        if functional_specification is not None:
            functional_specification_str = f"['{functional_specification}']" if isinstance(functional_specification,
                                                                                           str) else str(
                functional_specification)
            report.user_properties.append(("functional_specification", functional_specification_str))
        else:
            report.user_properties.append(("functional_specification", "[]"))
        if test_description is not None:
            report.user_properties.append(("test_description", test_description))

    # Handle category marker
    if category_marker:
        categories = category_marker.args
        if len(categories) == 1 and isinstance(categories[0], (list, tuple)):
            categories = categories[0]
        report.user_properties.append(("categories", str(list(categories))))
    else:
        report.user_properties.append(("categories", "[]"))


def pytest_collection_modifyitems(config, items):
    """Filter tests based on checkpoint"""
    if not config.getoption("--use-last-checkpoint"):
        return

    CONFIG = get_config()
    env_name = CONFIG['report']['test_environment']
    results_dir = Path(CONFIG['report']['report_dir'])
    checkpoint_files = list(results_dir.glob(f"{env_name}_checkpoint_*.json"))
    if not checkpoint_files:
        return

    checkpoint_file = max(checkpoint_files, key=lambda x: x.stat().st_mtime)

    try:
        with open(checkpoint_file, "r") as f:
            checkpoint_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return

    test_statuses = {}
    if (checkpoint_data.get("testsuites") and
            checkpoint_data["testsuites"][0].get("cases")):
        for case in checkpoint_data["testsuites"][0]["cases"]:
            if "name" in case and "status" in case:
                test_statuses[case["name"]] = case["status"]

    if not test_statuses:
        return

    selected = []
    deselected = []
    rerun_failed_only = config.getoption("--rerun-failed-tests-only")

    for item in items:
        if item.name in test_statuses:
            if rerun_failed_only:
                if test_statuses[item.name] == "Failed":
                    selected.append(item)
                else:
                    deselected.append(item)
            else:
                deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@pytest.fixture(autouse=True)
def save_test_result(request):
    """Save test results to checkpoint after each test"""
    yield

    checkpoint_file = getattr(request.config, "_checkpoint_file", None)
    if not checkpoint_file:
        logging.warning("No checkpoint file set in session.config; skipping checkpoint update.")
        return

    # Extract test information
    test_name = request.node.name
    test_class = request.node.nodeid.split("::")[0].replace("/", ".").replace("\\", ".").replace(".py", "")

    # Determine status and details
    status, details = determine_test_status(request.node)

    # Gather metadata
    test_case = gather_test_metadata(request.node, test_name, test_class, status, details)

    # Update checkpoint
    update_checkpoint(checkpoint_file, test_case)


def determine_test_status(node):
    """Determine test status and details from node"""
    if hasattr(node, "rep_setup") and node.rep_setup.failed:
        return "Failed", f"Setup failed: {str(node.rep_setup.longrepr)}"
    elif hasattr(node, "rep_setup") and node.rep_setup.skipped:
        skip_reason = node.rep_setup.longrepr[2] if len(node.rep_setup.longrepr) > 2 else ""
        return "Skipped", f"Type: Skip\nMessage: {skip_reason}"
    elif hasattr(node, "rep_call"):
        if node.rep_call.failed:
            if hasattr(node.rep_call.longrepr, "reprcrash"):
                details = (
                    f"Message: {node.rep_call.longrepr.reprcrash.message}\n"
                    f"Details: {str(node.rep_call.longrepr)}"
                )
            else:
                details = f"Details: {str(node.rep_call.longrepr)}"
            return "Failed", details
        else:
            return "Passed", ""
    else:
        return "Skipped", "Test was not executed"


def gather_test_metadata(node, test_name, test_class, status, details):
    """Gather test metadata from markers and properties"""
    reporting_marker = node.get_closest_marker("reporting")
    category_marker = node.get_closest_marker("category")

    developer = "-"
    functional_specifications = []
    test_description = ""
    logs = []
    categories = []

    if reporting_marker:
        developer = reporting_marker.kwargs.get("developer", "-")
        functional_specification = reporting_marker.kwargs.get("functional_specification")
        if functional_specification:
            if isinstance(functional_specification, str):
                functional_specifications = [functional_specification]
            else:
                functional_specifications = functional_specification
        test_description = (
                reporting_marker.kwargs.get("test_description")
                or reporting_marker.kwargs.get("comment", "")
        )

    if category_marker:
        categories = list(category_marker.args)
        if len(categories) == 1 and isinstance(categories[0], (list, tuple)):
            categories = list(categories[0])

    for prop in node.user_properties:
        if prop[0] == "logs":
            logs = prop[1]

    def process_comment(comment: str):
        if not comment:
            return ""
        lines = [line for line in comment.splitlines() if line.strip()]
        if len(lines) > 1:
            results = []
            for index, line in enumerate(lines):
                results.append(f"{line}")
            return "<br>".join(results)
        else:
            return "".join(lines)

    def process_logs(logs_list):
        log_html = "<ul style='list-style-type: none; padding: 0;'>"
        for log_type, log_text in logs_list:
            bg_color = "#E6F3FF" if log_type == "Step" else "#E6FFE6"
            log_text = log_text.replace("\n", "<br>")
            log_html += f"<li style='background-color: {bg_color}; padding: 5px; margin: 2px 0;'>{log_text}</li>"
        log_html += "</ul>"
        return log_html

    return {
        "classname": test_class,
        "name": test_name,
        "developer": developer,
        "test_description": process_comment(test_description),
        "status": status,
        "logs": process_logs(logs),
        "details": details,
        "functional_specifications": functional_specifications,
        "categories": categories
    }


def update_checkpoint(checkpoint_file, test_case):
    """Update checkpoint file with test result"""
    CONFIG = get_config()

    # Load existing data
    data = {
        "specs": {},
        "functional_spec_count": {},
        "testsuites": [{"cases": []}],
        "test_environment": CONFIG['report']['test_environment'],
        "timestamp": datetime.datetime.now().strftime("%d %b %Y, %H:%M"),
        "img_url": CONFIG['report']['img_url'],
        "test_status": "ongoing",
        "report_title": CONFIG['report']['title']
    }

    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, "r") as f:
                file_content = f.read()
                if file_content.strip():
                    data = json.loads(file_content)
                    # Remove existing test case if present
                    if "testsuites" in data and data["testsuites"][0]["cases"]:
                        data["testsuites"][0]["cases"] = [
                            case for case in data["testsuites"][0]["cases"]
                            if case["name"] != test_case["name"]
                        ]
        except json.JSONDecodeError:
            pass

    # Add test case
    data["testsuites"][0]["cases"].append(test_case)

    # Reprocess all test data
    processed_data = process_test_data(
        data["testsuites"][0]["cases"],
        data.get("test_environment")
    )

    # Update data with processed results
    data.update(processed_data)

    # Save checkpoint
    with open(checkpoint_file, "w") as f:
        json.dump(data, f, indent=2)