"""
Font Manager - Manages and provides access to custom fonts with robust fallback support
"""

import os
from typing import Dict, Optional, List, Union
from PIL import ImageFont, Image

from dolze_image_templates.utils.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

# Common system fonts to try as fallbacks
SYSTEM_FONT_FALLBACKS = [
    "Arial",
    "Helvetica",
    "DejaVuSans",
    "LiberationSans",
    "sans-serif",
    "NotoSans",
    "Roboto",
    "OpenSans",
]


class FontManager:
    """
    Manages font loading and provides access to custom fonts with graceful fallback to system fonts.
    """

    def __init__(self, font_dir: str = "fonts"):
        """
        Initialize the font manager.

        Args:
            font_dir: Directory containing font files
        """
        self.font_dir = font_dir
        self.fonts: Dict[str, str] = {}
        self._scan_fonts()

    def _scan_fonts(self) -> None:
        """
        Recursively scan the font directory and its subdirectories for available fonts.
        Fonts are stored with their base filename (without extension) as the key.
        """
        if not os.path.exists(self.font_dir):
            os.makedirs(self.font_dir, exist_ok=True)
            logger.warning(
                f"Font directory '{self.font_dir}' does not exist. Created directory."
            )
            return

        font_count = 0
        for root, _, files in os.walk(self.font_dir):
            for filename in files:
                if filename.lower().endswith((".ttf", ".otf")):
                    font_name = os.path.splitext(filename)[0]
                    font_path = os.path.join(root, filename)
                    self.fonts[font_name] = font_path
                    font_count += 1

        if font_count > 0:
            logger.debug(f"Loaded {font_count} fonts from {self.font_dir}")
        else:
            logger.warning(f"No fonts found in {self.font_dir}")

    def get_font(
        self,
        font_name: Optional[str] = None,
        size: int = 24,
        fallback_to_default: bool = True,
    ) -> ImageFont.FreeTypeFont:
        """
        Get a font by name and size with graceful fallback to system fonts.

        Font loading is attempted in this order:
        1. Try to load from registered fonts (if font_name is provided)
        2. Try to load as a system font (if font_name is provided)
        3. Try common system fonts
        4. Fall back to PIL's default font

        Args:
            font_name: Name of the font (without extension) or path to a font file
            size: Font size in points
            fallback_to_default: Whether to fall back to default font if all else fails

        Returns:
            PIL ImageFont object
        """
        # 1. Try to load from registered fonts if font_name is provided and exists
        if font_name and font_name in self.fonts:
            try:
                font_path = self.fonts[font_name]
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"Failed to load registered font '{font_name}': {e}")
                # Continue to next fallback

        # 2. Try to load as system font if font_name is provided
        if font_name:
            try:
                return ImageFont.truetype(font_name, size)
            except Exception as e:
                logger.debug(f"Font '{font_name}' not found in system: {e}")
                # Continue to next fallback

        # 3. Try system fallback fonts
        system_font = self._get_system_font(size, font_name)
        if system_font:
            return system_font

        # 4. Fall back to default font if enabled
        if fallback_to_default:
            logger.warning(f"Using default font as fallback")
            return ImageFont.load_default()

        # If we get here and fallback_to_default is False, raise an error
        raise ValueError(f"Could not load font: {font_name}")

    def _get_system_font(
        self, size: int, attempted_font: Optional[str] = None
    ) -> Optional[ImageFont.FreeTypeFont]:
        """
        Try to load a system font from common font families.

        Args:
            size: Font size in points
            attempted_font: The font name that was originally attempted (for logging)

        Returns:
            PIL ImageFont if successful, None if no system font could be loaded
        """
        # Try system fallback fonts
        for font_name in SYSTEM_FONT_FALLBACKS:
            try:
                if attempted_font and font_name.lower() == attempted_font.lower():
                    continue  # Skip if this is the font we already tried

                font = ImageFont.truetype(font_name, size)
                logger.debug(f"Using system font: {font_name}")
                return font
            except Exception as e:
                logger.debug(f"System font '{font_name}' not available: {e}")
                continue

        return None

    def list_fonts(self) -> List[str]:
        """
        Get a list of available font names.

        Returns:
            List of font names
        """
        return list(self.fonts.keys())

    def list_fonts(self) -> List[str]:
        """
        Get a list of available font names.

        Returns:
            List of font names
        """
        return list(self.fonts.keys())


# Singleton instance for easy access
_instance = None


def get_font_manager(font_dir: str = "fonts") -> FontManager:
    """
    Get the singleton instance of the font manager.

    Args:
        font_dir: Directory containing font files

    Returns:
        FontManager instance
    """
    global _instance
    if _instance is None:
        _instance = FontManager(font_dir)
    return _instance
