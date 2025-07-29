from loguru import logger
from typing import Any, Callable, Iterable, Optional, Union, Type, Tuple
import re
import inspect


class SoftAssert:
    _failures = []

    @classmethod
    def _record_failure(cls, msg: str, expected: Any = None, actual: Any = None) -> None:
        full_msg = msg or (f"Expected: {expected}\nActual:   {actual}" if expected is not None else "Assertion failed")
        cls._failures.append(full_msg)
        logger.error(f"SoftAssert failed: {full_msg}")

    @classmethod
    def _format_message(cls, msg: Optional[str], default_msg: str) -> str:
        return msg if msg is not None else default_msg

    @classmethod
    def Condition(cls, condition: bool, msg: Optional[str] = None) -> 'SoftAssert':
        if not condition:
            cls._record_failure(cls._format_message(msg, "Condition not satisfied"))
        return cls

    @classmethod
    def Equal(cls, expected: Any, actual: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if expected != actual:
            cls._record_failure(
                cls._format_message(msg, "Values are not equal"),
                expected,
                actual
            )
        return cls

    @classmethod
    def NotEqual(cls, expected: Any, actual: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if expected == actual:
            cls._record_failure(
                cls._format_message(msg, "Values are equal"),
                f"Not {expected}",
                actual
            )
        return cls

    @classmethod
    def Contains(cls, container: Iterable, item: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if item not in container:
            cls._record_failure(
                cls._format_message(msg, "Container does not contain item"),
                f"Container with {item}",
                container
            )
        return cls

    @classmethod
    def NotContains(cls, container: Iterable, item: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if item in container:
            cls._record_failure(
                cls._format_message(msg, "Container contains item"),
                f"Container without {item}",
                container
            )
        return cls

    @classmethod
    def is_true(cls, value: bool, msg: Optional[str] = None) -> 'SoftAssert':
        if not value:
            cls._record_failure(
                cls._format_message(msg, "Value is not True"),
                True,
                value
            )
        return cls

    @classmethod
    def is_false(cls, value: bool, msg: Optional[str] = None) -> 'SoftAssert':
        if value:
            cls._record_failure(
                cls._format_message(msg, "Value is not False"),
                False,
                value
            )
        return cls

    @classmethod
    def is_none(cls, value: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if value is not None:
            cls._record_failure(
                cls._format_message(msg, "Value is not None"),
                None,
                value
            )
        return cls

    @classmethod
    def not_none(cls, value: Any, msg: Optional[str] = None) -> 'SoftAssert':
        if value is None:
            cls._record_failure(
                cls._format_message(msg, "Value is None"),
                "Not None",
                value
            )
        return cls

    @classmethod
    def is_empty(cls, container: Iterable, msg: Optional[str] = None) -> 'SoftAssert':
        if len(container) != 0:  # type: ignore
            cls._record_failure(
                cls._format_message(msg, "Container is not empty"),
                "Empty container",
                container
            )
        return cls

    @classmethod
    def not_empty(cls, container: Iterable, msg: Optional[str] = None) -> 'SoftAssert':
        if len(container) == 0:  # type: ignore
            cls._record_failure(
                cls._format_message(msg, "Container is empty"),
                "Non-empty container",
                container
            )
        return cls

    @classmethod
    def is_type(cls, obj: Any, typ: Type, msg: Optional[str] = None) -> 'SoftAssert':
        if not isinstance(obj, typ):
            cls._record_failure(
                cls._format_message(msg, "Object is not of expected type"),
                typ,
                type(obj)
            )
        return cls


    @classmethod
    def verify_assert(cls) -> None:
        if cls._failures:
            failures = "\n".join(f"{i + 1}. {msg}" for i, msg in enumerate(cls._failures))
            logger.error(f"SoftAssert failures:\n{failures}")
            cls._failures.clear()
            raise AssertionError(f"Soft assertions failed:\n{failures}")
        cls._failures.clear()

    @classmethod
    def expect(cls, condition: bool, msg: Optional[str] = None) -> 'SoftAssert':
        """Entry point for basic boolean condition checks."""
        if not condition:
            cls._record_failure(cls._format_message(msg, "Expectation failed"))
        return cls

    @classmethod
    def reset_assert(cls) -> None:
        cls._failures.clear()