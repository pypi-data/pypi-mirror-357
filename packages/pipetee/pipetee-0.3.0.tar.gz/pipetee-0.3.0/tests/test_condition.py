"""Unit tests for the Condition class in the pipeline module."""

import asyncio
from typing import Any, Callable, Dict, Union, cast

import pytest

from pipetee.pipeline import Condition

# Type alias for condition functions
ConditionCallable = Callable[[Any], Union[bool, asyncio.Future[bool]]]


@pytest.mark.asyncio
async def test_condition_basic() -> None:
    """Test basic boolean condition"""
    # Test basic boolean condition
    is_positive = Condition("is_positive", lambda x: x > 0)
    assert is_positive.name == "is_positive"
    assert await is_positive.evaluate(5) is True
    assert await is_positive.evaluate(-5) is False
    assert await is_positive.evaluate(0) is False


@pytest.mark.asyncio
async def test_condition_with_string() -> None:
    """Test condition with string input"""
    # Test condition with string input
    is_long_string = Condition("is_long_string", lambda s: len(s) > 10)
    assert await is_long_string.evaluate("short") is False
    assert await is_long_string.evaluate("this is a long string") is True


@pytest.mark.asyncio
async def test_condition_with_dict() -> None:
    """Test condition with dictionary input"""
    # Test condition with dictionary input
    has_required_fields = Condition(
        "has_required_fields", lambda d: all(key in d for key in ["id", "name"])
    )
    assert await has_required_fields.evaluate({"id": 1, "name": "test"}) is True
    assert await has_required_fields.evaluate({"id": 1}) is False
    assert await has_required_fields.evaluate({}) is False


@pytest.mark.asyncio
async def test_condition_with_none() -> None:
    """Test condition handling None values"""
    # Test condition handling None values
    is_none = Condition("is_none", lambda x: x is None)
    assert await is_none.evaluate(None) is True
    assert await is_none.evaluate("not none") is False


@pytest.mark.asyncio
async def test_condition_complex_logic() -> None:
    """Test condition with more complex logic"""
    # Test condition with more complex logic
    is_valid_user = Condition(
        "is_valid_user",
        lambda user: isinstance(user, dict)
        and "age" in user
        and len(str(user["age"])) > 0
        and len(user.get("name", "")) >= 2,
    )

    assert await is_valid_user.evaluate({"name": "John", "age": 25}) is True
    assert await is_valid_user.evaluate({"name": "J", "age": 25}) is False
    assert await is_valid_user.evaluate({"name": "John"}) is False
    assert await is_valid_user.evaluate({}) is False


@pytest.mark.asyncio
async def test_condition_with_exception_handling() -> None:
    """Test condition that might raise exceptions"""

    # Test condition that might raise exceptions
    def safe_divide(x: Dict[str, Any]) -> bool:
        try:
            result = x["numerator"] / x["denominator"]
            return bool(result > 1)
        except (KeyError, ZeroDivisionError, TypeError):
            return False

    is_ratio_greater_than_one = Condition("is_ratio_greater_than_one", safe_divide)

    assert (
        await is_ratio_greater_than_one.evaluate({"numerator": 10, "denominator": 5})
        is True
    )
    assert (
        await is_ratio_greater_than_one.evaluate({"numerator": 5, "denominator": 10})
        is False
    )
    assert (
        await is_ratio_greater_than_one.evaluate({"numerator": 1, "denominator": 0})
        is False
    )
    assert await is_ratio_greater_than_one.evaluate({}) is False
    assert await is_ratio_greater_than_one.evaluate(None) is False


@pytest.mark.asyncio
async def test_async_condition() -> None:
    """Test async condition function"""

    async def async_check(data: Any) -> bool:
        await asyncio.sleep(0.1)  # Simulate async work
        return isinstance(data, str) and len(data) > 5

    # Cast the async function to the expected condition type
    condition_func = cast(ConditionCallable, async_check)
    condition = Condition("async_test", condition_func)

    assert await condition.evaluate("short string") is True
    assert await condition.evaluate("short") is False
