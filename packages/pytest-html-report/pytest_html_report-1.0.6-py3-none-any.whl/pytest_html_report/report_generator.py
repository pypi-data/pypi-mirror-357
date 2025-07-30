import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Set
from pathlib import Path
from .config import get_config


def load_html_template():
    """Load HTML template from package"""
    template_path = Path(__file__).parent / 'templates' / 'report_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_functional_spec_name(spec_id: str) -> str:
    """Get functional spec name from configuration"""
    CONFIG = get_config()
    functional_spec_dict = CONFIG.get('functional_specs', {})
    functional_spec_dict.update({"CORE": "Core Feature with No Functional Spec Associated"})
    return functional_spec_dict.get(spec_id, f"Specification {spec_id}")


def get_category_display_name(category_id: str) -> str:
    """Get category display name from configuration"""
    CONFIG = get_config()
    categories_dict = CONFIG.get('categories', {})
    return categories_dict.get(category_id, f"Custom: {category_id}")


def is_known_category(category: str) -> bool:
    """Check if a category is defined in the configuration"""
    CONFIG = get_config()
    categories_dict = CONFIG.get('categories', {})
    return category in categories_dict


def process_test_data(test_cases: List[Dict], test_environment: str = None) -> Dict:
    """Process test cases into report data structure"""
    CONFIG = get_config()
    specs = {}
    functional_spec_count = {}
    category_count = {}
    all_categories = set()

    # Collect all categories
    for case in test_cases:
        all_categories.update(case.get("categories", []))

    # Initialize category count structure
    for category in all_categories:
        category_count[category] = 0

    # Process test cases
    for case in test_cases:
        # Count categories
        for category in case.get("categories", []):
            category_count[category] += 1

        # Process functional specifications
        for spec_id in case.get("functional_specifications", []):
            if spec_id not in functional_spec_count:
                functional_spec_count[spec_id] = {
                    "pass": 0, "fail": 0, "skip": 0, "total": 0
                }
                # Initialize category counts for this spec
                for category in all_categories:
                    functional_spec_count[spec_id][category] = 0

            functional_spec_count[spec_id]["total"] += 1

            if case["status"] == "Passed":
                functional_spec_count[spec_id]["pass"] += 1
            elif case["status"] == "Failed":
                functional_spec_count[spec_id]["fail"] += 1
            elif case["status"] == "Skipped":
                functional_spec_count[spec_id]["skip"] += 1

            # Count categories for this spec
            for category in case.get("categories", []):
                functional_spec_count[spec_id][category] += 1

            if spec_id not in specs:
                specs[spec_id] = {"cases": [], "status": "Passing"}

            specs[spec_id]["cases"].append(case)

            # Update spec status
            if case["status"] == "Failed":
                specs[spec_id]["status"] = "Failing"
            elif case["status"] == "Skipped" and specs[spec_id]["status"] == "Passing":
                specs[spec_id]["status"] = "Partially Passing"

    return {
        "specs": specs,
        "functional_spec_count": functional_spec_count,
        "category_count": category_count,
        "all_categories": list(all_categories),
        "testsuites": [{"cases": test_cases}],
        "test_environment": test_environment or CONFIG['report']['test_environment'],
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
        "img_url": CONFIG['report']['img_url'],
        "report_title": CONFIG['report']['title']
    }


def parse_json_to_data(json_source):
    """Parse JSON checkpoint into the data structure used by the HTML generator."""
    try:
        if isinstance(json_source, str):
            if os.path.isfile(json_source):
                with open(json_source, 'r') as f:
                    data = json.load(f)
            else:
                data = json.loads(json_source)
        else:
            data = json_source

        # Process to ensure all categories are accounted for
        all_categories = set()
        if "testsuites" in data:
            for suite in data["testsuites"]:
                for case in suite.get("cases", []):
                    all_categories.update(case.get("categories", []))

        data["all_categories"] = list(all_categories)

        # Ensure category counts are in functional_spec_count
        for spec_id, counts in data.get("functional_spec_count", {}).items():
            for category in all_categories:
                if category not in counts:
                    counts[category] = 0

        return data
    except Exception as e:
        raise ValueError(f"Failed to parse JSON data: {str(e)}")


def create_html_from_data(parsed_data):
    """Create HTML report from parsed data."""
    CONFIG = get_config()

    # Load template
    template = load_html_template()

    # Get theme colors from config
    theme = CONFIG.get('theme', {})

    # Generate content
    content = generate_html_content(parsed_data)

    # Replace placeholders in template
    html_output = template.replace("{{content}}", content)

    # Replace theme colors
    for key, value in theme.items():
        html_output = html_output.replace(f"{{{{{key}}}}}", value)

    # Replace category names for JavaScript
    category_names_js = json.dumps(parsed_data.get("all_categories", []))
    html_output = html_output.replace("{{category_names}}", category_names_js)

    return html_output


def generate_html_content(parsed_data):
    """Generate the main content of the HTML report"""
    CONFIG = get_config()
    content = ""

    # Header
    report_title = parsed_data.get('report_title', CONFIG['report']['title'])
    content += (f"<div class='header-container'>"
                f"<div class='header-content'>"
                f"<img src='{parsed_data['img_url']}' alt='Logo' class='logo'>"
                f"<div class='header-title'>"
                f"<h2>{report_title}</h2>"
                f"<div class='header-meta'>")

    # Timestamp
    content += f"<span>Report generation time: {parsed_data['timestamp']}</span>"

    # Test environment
    if parsed_data.get('test_environment'):
        content += f"<span>Test Environment: {parsed_data['test_environment']}</span>"

    content += "</div></div></div></div>"

    # Main content container
    content += "<div class='main-container'>\n"

    # Filter buttons
    content += generate_filter_buttons(parsed_data)

    # Summary table
    content += generate_summary_table(parsed_data)

    # Detailed test results
    content += generate_detailed_results(parsed_data)

    # No results message
    content += "<div id='no-results' class='no-results' style='display: none;'>No tests match the selected filters</div>"

    content += "</div>\n"

    return content


def generate_filter_buttons(parsed_data):
    """Generate filter button section"""
    all_categories = parsed_data.get("all_categories", [])

    html = "<div class='filter-container'>\n"

    # Status filters section
    html += "<div class='filter-section'>\n"
    html += "<div class='filter-label'>Status Filters:</div>\n"
    html += "<div class='filter-group'>\n"
    html += "<button class='filter-btn' onclick=\"toggleFilter('status', 'Passed')\">Passed</button>\n"
    html += "<button class='filter-btn' onclick=\"toggleFilter('status', 'Failed')\">Failed</button>\n"
    html += "<button class='filter-btn' onclick=\"toggleFilter('status', 'Skipped')\">Skipped</button>\n"
    html += "</div>\n"
    html += "</div>\n"

    # Category filters section
    if all_categories:
        html += "<div class='filter-section'>\n"
        html += "<div class='filter-label'>Category Filters:</div>\n"
        html += "<div class='filter-group'>\n"
        for category in sorted(all_categories):
            display_name = get_category_display_name(category)
            html += f"<button class='filter-btn' onclick=\"toggleFilter('category', '{category}')\">{display_name}</button>\n"
        html += "</div>\n"
        html += "</div>\n"

    html += "</div>\n"

    return html


def generate_summary_table(parsed_data):
    """Generate summary table with scrollable wrapper and totals"""
    all_categories = parsed_data.get("all_categories", [])

    html = "<div class='table-container'>\n"
    html += "<div class='table-wrapper'>\n"
    html += "<table class='top-table'>\n"
    html += "<tr><th>Functional Specification</th><th>Overall Status</th>"
    html += "<th>Tests Passed</th><th>Tests Failed</th><th>Tests Skipped</th>"

    # Add columns for categories
    for category in sorted(all_categories):
        display_name = get_category_display_name(category)
        html += f"<th>{display_name}</th>"

    html += "</tr>\n"

    for spec_id, content in parsed_data['specs'].items():
        counts = parsed_data['functional_spec_count'][spec_id]
        status_class = "passed" if content["status"] == "Passing" else (
            "failed" if content["status"] == "Failing" else "skipped")
        functional_spec_name = get_functional_spec_name(spec_id)

        html += f"<tr class='clickable-row' onclick='scrollToSpec(\"{spec_id}\")'>\n"
        html += f"<td>{spec_id} - {functional_spec_name}</td>\n"
        html += f"<td class='status-{status_class}'>{content['status']}</td>\n"
        html += f"<td>{counts['pass']}/{counts['total']}</td>\n"
        html += f"<td>{counts['fail']}/{counts['total']}</td>\n"
        html += f"<td>{counts['skip']}/{counts['total']}</td>\n"

        # Add category counts
        for category in sorted(all_categories):
            count = counts.get(category, 0)
            html += f"<td>{count}/{counts['total']}</td>\n"

        html += "</tr>\n"

    # Add totals row
    html += "<tr id='totals-row' class='totals-row'>\n"
    html += "<td>TOTAL</td>\n"
    html += "<td>-</td>\n"
    html += "<td>0</td>\n"
    html += "<td>0</td>\n"
    html += "<td>0</td>\n"

    # Add placeholders for category totals
    for category in sorted(all_categories):
        html += "<td>0</td>\n"

    html += "</tr>\n"

    html += "</table>\n"
    html += "</div>\n"
    html += "</div>\n"
    return html


def generate_detailed_results(parsed_data):
    """Generate detailed test results"""
    html = ""
    all_categories = parsed_data.get("all_categories", [])

    for spec_id, content in parsed_data['specs'].items():
        counts = parsed_data['functional_spec_count'][spec_id]
        status_class = "passed" if content["status"] == "Passing" else (
            "failed" if content["status"] == "Failing" else "skipped")

        html += f"<div id='spec-{spec_id}' class='test-result-block'>\n"
        html += f"<h2 class='spec-title'>{spec_id} - {get_functional_spec_name(spec_id)}</h2>\n"
        html += "<div class='spec-summary'>\n"
        html += f"<div class='spec-status'>Overall Status: <span class='{status_class}'>{content['status']}</span></div>\n"
        html += "<div class='test-counts'>\n"
        html += f"<span class='count passed'>Passed: {counts['pass']}/{counts['total']}</span>\n"
        html += f"<span class='count failed'>Failed: {counts['fail']}/{counts['total']}</span>\n"
        html += f"<span class='count skipped'>Skipped: {counts['skip']}/{counts['total']}</span>\n"

        # Add category counts
        for category in sorted(all_categories):
            count = counts.get(category, 0)
            if count > 0:
                display_name = get_category_display_name(category)
                # Use different style for unknown categories
                category_class = 'category' if is_known_category(category) else 'category-unknown'
                html += f"<span class='count {category_class}'>{display_name}: {count}/{counts['total']}</span>\n"

        html += f"<button id='btn-{spec_id}' onclick='toggleDetails(\"{spec_id}\")'>Expand</button>\n"
        html += "</div>\n</div>\n"

        # Test cases table with wrapper for horizontal scroll
        html += f"<div id='details-{spec_id}' style='display: none;'>\n"
        html += "<div class='detail-table-wrapper'>\n"  # Add wrapper div
        html += "<table>\n"
        html += "<tr><th>Test File</th><th>Test Name</th><th>Developer</th>"
        html += "<th>Description</th><th>Categories</th><th>Status</th><th>Execution Details</th></tr>\n"

        for case in content["cases"]:
            status_class = case["status"].lower()
            case_id = f"{case['classname']}-{case['name']}".replace(".", "-")
            categories_str = ",".join(case.get("categories", []))

            html += f"<tr class='{case['status']}' data-categories='{categories_str}'>\n"
            html += f"<td>{case['classname']}</td>\n"
            html += f"<td>{case['name']}</td>\n"
            html += f"<td>{case['developer']}</td>\n"
            html += f"<td>{case['test_description']}</td>\n"

            # Categories column
            html += "<td>"
            for category in case.get("categories", []):
                display_name = get_category_display_name(category)
                # Use different style for unknown categories
                tag_class = 'category-tag' if is_known_category(category) else 'category-tag unknown'
                html += f"<span class='{tag_class}'>{display_name}</span>"
            html += "</td>\n"

            # Status column
            html += f"<td class='{status_class}'>{case['status']}"
            if case["status"] in ["Failed", "Skipped"]:
                html += f" <button onclick=\"toggleTestDetails('{case_id}')\">Show details</button>"
                html += f"<code id='test-details-{case_id}' style='display: none;'>{case['details']}</code>"
            html += "</td>\n"

            # Execution details column
            html += f"<td><button onclick=\"toggleExecutionDetails('{case_id}')\">Show logs</button>"
            html += f"<div id='exec-details-{case_id}' style='display: none;'>{case['logs']}</div></td>\n"
            html += "</tr>\n"

        html += "</table>\n"
        html += "</div>\n"  # Close wrapper div
        html += "</div>\n</div>\n"

    return html


def generate_html_from_json(json_path, output_file):
    """Generate HTML report from JSON checkpoint file"""
    data = parse_json_to_data(json_path)
    html_output = create_html_from_data(data)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)