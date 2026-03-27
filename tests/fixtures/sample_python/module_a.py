"""Module A — imports module_b to create a circular dependency."""

from . import module_b


class ServiceA:
    """A service that depends on module_b."""

    def do_work(self) -> str:
        return module_b.helper()


def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}"
