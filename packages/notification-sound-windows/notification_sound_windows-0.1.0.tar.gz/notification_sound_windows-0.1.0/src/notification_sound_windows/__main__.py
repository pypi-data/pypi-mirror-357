"""
Entry point for the MCP Play Sound Server.

This module provides the main entry point for running the MCP server
that handles audio playback notifications for AI agents.
"""

import logging
import sys

from .config import ServerConfig, ConfigurationError
from .server import PlaySoundServer


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load configuration
        logger.info("Loading server configuration...")
        config = ServerConfig.from_environment()
        
        # Validate configuration
        logger.info("Validating configuration...")
        config.validate()
        
        # Create and run server
        logger.info("Starting MCP Play Sound Server...")
        server = PlaySoundServer(config)
        
        # Run the server
        server.run()
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
