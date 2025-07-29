"""
Dolze Templates - A flexible template generation library for creating social media posts, banners, and more.

This package provides a powerful and extensible system for generating images with text, shapes, and other
components in a template-based approach.
"""

import os
import logging

# Version information
__version__ = "0.1.2"

# Set up logging
from .utils.logging_config import setup_logging

# Default log level (can be overridden by applications using this package)
LOG_LEVEL = os.environ.get("DOLZE_LOG_LEVEL", "WARNING").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.WARNING)

# Set up logging with default level
setup_logging(level=LOG_LEVEL)

# Core functionality
from .core import (
    Template,
    TemplateEngine,
    TemplateRegistry,
    get_template_registry,
    FontManager,
    get_font_manager,
)
from typing import Optional, Dict, Any, Union


def get_all_image_templates() -> list[str]:
    """
    Get a list of all available template names.

    Returns:
        List[str]: A list of all available template names
    """
    return get_template_registry().get_all_templates()


def render_template(
    template_name: str,
    variables: Optional[Dict[str, Any]] = None,
    output_format: str = "png",
    return_bytes: bool = True,
    output_dir: str = "output",
    output_path: Optional[str] = None,
) -> Union[bytes, str]:
    """
    Render a template with the given variables.

    This is a convenience function that creates a TemplateEngine instance and
    renders a template in one step. The template must be present in the templates directory.

    Args:
        template_name: Name of the template to render (must be in the templates directory)
        variables: Dictionary of variables to substitute in the template
        output_format: Output image format (e.g., 'png', 'jpg', 'jpeg')
        return_bytes: If True, returns the image as bytes instead of saving to disk
        output_dir: Directory to save the rendered image (used if return_bytes is False and output_path is None)
        output_path: Full path to save the rendered image. If None and return_bytes is False, a path will be generated.

    Returns:
        If return_bytes is True: Image bytes
        If return_bytes is False: Path to the rendered image

    Example:
        ```python
        from dolze_image_templates import render_template

        # Define template variables
        variables = {
            "title": "Welcome to Dolze",
            "subtitle": "Create amazing images with ease",
            "image_url": "https://example.com/hero.jpg"
        }

        # Render a template and get bytes
        image_bytes = render_template(
            template_name="my_template",
            variables=variables,
            return_bytes=True
        )
        
        # Use the bytes directly (e.g., send in API response)
        # Or save to file if needed
        with open('my_image.png', 'wb') as f:
            f.write(image_bytes)
        ```
    """
    engine = TemplateEngine(output_dir=output_dir)
    return engine.render_template(
        template_name=template_name,
        variables=variables or {},
        output_path=output_path if not return_bytes else None,
        output_format=output_format,
        return_bytes=return_bytes,
    )


# Resource management and caching
from .resources import load_image, load_font
from .utils.cache import clear_cache, get_cache_info

# Components
from .components import (
    Component,
    TextComponent,
    ImageComponent,
    CircleComponent,
    RectangleComponent,
    CTAButtonComponent,
    FooterComponent,
    create_component_from_config,
)

# Configuration
from .config import (
    Settings,
    get_settings,
    configure,
    DEFAULT_TEMPLATES_DIR,
    DEFAULT_FONTS_DIR,
    DEFAULT_OUTPUT_DIR,
)

# Version
__version__ = "0.1.2"


# Package metadata
__author__ = "Dolze Team"
__email__ = "support@dolze.com"
__license__ = "MIT"
__description__ = "A flexible template generation library for creating social media posts, banners, and more."


# Package-level initialization
def init() -> None:
    """
    Initialize the Dolze Templates package.
    This function ensures all required directories exist and performs any necessary setup.
    """
    logger = logging.getLogger(__name__)
    logger.info("Initializing Dolze Templates package")
    
    settings = get_settings()

    # Ensure required directories exist
    os.makedirs(settings.templates_dir, exist_ok=True)
    os.makedirs(settings.fonts_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    
    logger.debug("Package initialization complete")


# Initialize the package when imported
init()


# Clean up namespace
del init

__all__ = [
    # Core
    "Template",
    "TemplateEngine",
    "TemplateRegistry",
    "get_template_registry",
    "FontManager",
    "get_font_manager",
    # Components
    "Component",
    "TextComponent",
    "ImageComponent",
    "CircleComponent",
    "RectangleComponent",
    "CTAButtonComponent",
    "FooterComponent",
    "create_component_from_config",
    # Configuration
    "Settings",
    "get_settings",
    "configure",
    "DEFAULT_TEMPLATES_DIR",
    "DEFAULT_FONTS_DIR",
    "DEFAULT_OUTPUT_DIR",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]
