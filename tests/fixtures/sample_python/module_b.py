"""Module B — imports module_a to create a circular dependency."""

from . import module_a


class ServiceB:
    """A service that depends on module_a."""

    def process(self) -> str:
        return module_a.greet("world")


def helper() -> str:
    """Helper function called by module_a."""
    return "helped"
