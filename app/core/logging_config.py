import logging
from typing import Optional


class LoggingConfigurator:
    """Configures application logging following SRP."""

    def __init__(
            self,
            log_file: str = "word_game.log",
            log_level: int = logging.INFO,
            log_format: Optional[str] = None
    ):
        self.log_file = log_file
        self.log_level = log_level
        self.log_format = log_format or '%(asctime)s - %(levelname)s - %(message)s'

    def configure(self) -> logging.Logger:
        """Configure and return the root logger."""
        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
