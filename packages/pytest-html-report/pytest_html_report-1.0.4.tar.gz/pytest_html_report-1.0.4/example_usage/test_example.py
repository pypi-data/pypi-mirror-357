import pytest
import asyncio


comment_1_1 = '''
This is a sample test that demonstrates the reporting features.
1. First step of the test
2. Second step of the test
3. Third step with verification
Multiline comments like this are shown the same way on the report.
'''


@pytest.mark.asyncio
@pytest.mark.reporting(developer="John Doe", functional_specification="SPEC-001", comment=comment_1_1)
@pytest.mark.category("smoke", "regression")
async def test_example_async_test(logger):
    """Example async test with reporting and categories"""

    logger.step("Starting the test execution")

    # Simulate some async operation
    await asyncio.sleep(0.1)

    logger.step("Performing test operation")
    result = 10 + 20

    logger.assertion(f"Verifying result equals 30: {result == 30}")
    assert result == 30

    logger.step("Test completed successfully")


@pytest.mark.reporting(developer="Jane Smith", functional_specification=["SPEC-001", "SPEC-002"],
                       test_description="This test validates multiple specifications")
@pytest.mark.category("integration")
def test_example_sync_test(logger):
    """Example sync test with multiple specs"""

    logger.step("Initializing test data")
    test_data = {"key": "value", "number": 42}

    logger.step(f"Test data created: {test_data}")

    logger.assertion("Verifying 'key' exists in test_data")
    assert "key" in test_data

    logger.assertion("Verifying number equals 42")
    assert test_data["number"] == 42


@pytest.mark.skip(reason="This test is marked as optional")
@pytest.mark.reporting(developer="Bob Johnson", functional_specification="SPEC-003")
@pytest.mark.category("optional", "manual")
def test_skipped_example(logger):
    """Example of a skipped test with categories"""
    logger.step("This test should be skipped")
    assert False  # This won't run


@pytest.mark.reporting(developer="Alice Brown", functional_specification="SPEC-001")
@pytest.mark.category("unit")
def test_failing_example(logger):
    """Example of a test that fails"""

    logger.step("Setting up test scenario")
    expected = 100
    actual = 99

    logger.step(f"Expected: {expected}, Actual: {actual}")

    logger.assertion("Verifying values match")
    assert expected == actual, f"Expected {expected} but got {actual}"


# Parameterized test example
@pytest.mark.parametrize("input_value,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
@pytest.mark.reporting(developer="Charlie Davis", functional_specification="SPEC-004",
                       test_description="Validates square calculation for different inputs")
@pytest.mark.category("unit", "regression")
def test_parameterized_example(input_value, expected, logger):
    """Example of parameterized test with categories"""

    logger.step(f"Testing square of {input_value}")
    result = input_value ** 2

    logger.assertion(f"Verifying {input_value}² = {expected}")
    assert result == expected


# Test with unknown category
@pytest.mark.reporting(developer="David Wilson", functional_specification="SPEC-005")
@pytest.mark.category("unknown_category", "performance")
def test_with_unknown_category(logger):
    """Example test with an unknown category"""

    logger.step("Running performance test")
    logger.assertion("Performance within limits")
    assert True
