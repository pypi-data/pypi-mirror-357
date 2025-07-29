"""Factory for creating formatters."""

from typing import Dict, Type

from ..core.interfaces.formatter import FormatterInterface
from ..exceptions.base import FormatterError
from .slack import SlackFormatter
from .teams import TeamsFormatter
from .whatsapp import WhatsAppFormatter
from .email import EmailFormatter


class FormatterFactory:
    """Factory for creating formatters."""

    _formatters: Dict[str, Type[FormatterInterface]] = {
        "slack": SlackFormatter,
        "teams": TeamsFormatter,
        "whatsapp": WhatsAppFormatter,
        "email": EmailFormatter,
    }

    @classmethod
    def create_formatter(
        cls, format_type: str, status_info: Dict[str, Dict[str, str]]
    ) -> FormatterInterface:
        """Create a formatter instance.

        Args:
            format_type: Type of formatter to create (slack/teams/whatsapp/email)
            status_info: Status configuration from config manager

        Returns:
            Formatter instance

        Raises:
            FormatterError: If format type is not supported
        """
        formatter_class = cls._formatters.get(format_type.lower())
        if not formatter_class:
            supported = ", ".join(cls._formatters.keys())
            raise FormatterError(
                f"Unsupported format: {format_type}. " f"Supported formats: {supported}"
            )

        return formatter_class(status_info)

    @classmethod
    def register_formatter(
        cls, name: str, formatter_class: Type[FormatterInterface]
    ) -> None:
        """Register a new formatter type.

        Args:
            name: Name of the formatter
            formatter_class: Formatter class to register

        Raises:
            FormatterError: If formatter class is invalid
        """
        if not issubclass(formatter_class, FormatterInterface):
            raise FormatterError(
                f"Formatter class must inherit from FormatterInterface: {formatter_class}"
            )
        cls._formatters[name.lower()] = formatter_class

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get list of supported format types.

        Returns:
            List of supported format names
        """
        return list(cls._formatters.keys())
