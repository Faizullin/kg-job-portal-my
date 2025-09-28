from drf_standardized_errors.handler import (
    exception_handler as standardized_exception_handler,
)


class StandardizedViewMixin:
    """Mixin to provide standardized exception handling for DRF views."""

    def handle_exception(self, exc):
        response = standardized_exception_handler(
            exc, self.get_exception_handler_context()
        )
        if response is None:
            return super().handle_exception(exc)
        return response
