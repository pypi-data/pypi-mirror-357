"""
Text element classes for natural-pdf.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from natural_pdf.elements.base import Element

if TYPE_CHECKING:
    from natural_pdf.core.page import Page


class TextElement(Element):
    """
    Represents a text element in a PDF.

    This class is a wrapper around pdfplumber's character objects,
    providing additional functionality for text extraction and analysis.
    """

    def __init__(self, obj: Dict[str, Any], page: "Page"):
        """
        Initialize a text element.

        Args:
            obj: The underlying pdfplumber object. For OCR text elements,
                 should include 'text', 'bbox', 'source', and 'confidence'
            page: The parent Page object
        """
        # Add object_type if not present
        if "object_type" not in obj:
            obj["object_type"] = "text"

        super().__init__(obj, page)
        # Explicitly store constituent characters if provided
        # (Pop from obj to avoid storing it twice if super() stores _obj by ref)
        self._char_dicts = obj.pop("_char_dicts", [])

    @property
    def text(self) -> str:
        """Get the text content."""
        return self._obj.get("text", "")

    @text.setter
    def text(self, value: str):
        """Set the text content and synchronise underlying char dictionaries (if any)."""
        # Update the primary text value stored on the object itself
        self._obj["text"] = value

        # --- Keep _char_dicts in sync so downstream utilities (e.g. extract_text)
        #     that rely on the raw character dictionaries see the corrected text.
        #     For OCR-generated words we usually have a single representative char
        #     dict; for native words there may be one per character.
        # ---------------------------------------------------------------------
        try:
            if hasattr(self, "_char_dicts") and isinstance(self._char_dicts, list):
                if not self._char_dicts:
                    return  # Nothing to update

                if len(self._char_dicts) == 1:
                    # Simple case – a single char dict represents the whole text
                    self._char_dicts[0]["text"] = value
                else:
                    # Update character-by-character. If new value is shorter than
                    # existing char dicts, truncate remaining dicts by setting
                    # their text to empty string; if longer, extend by repeating
                    # the last char dict geometry (best-effort fallback).
                    for idx, char_dict in enumerate(self._char_dicts):
                        if idx < len(value):
                            char_dict["text"] = value[idx]
                        else:
                            # Clear extra characters from old text
                            char_dict["text"] = ""

                    # If new text is longer, append additional char dicts based
                    # on the last available geometry. This is an approximation
                    # but ensures text length consistency for downstream joins.
                    if len(value) > len(self._char_dicts):
                        last_dict = self._char_dicts[-1]
                        for extra_idx in range(len(self._char_dicts), len(value)):
                            new_dict = last_dict.copy()
                            new_dict["text"] = value[extra_idx]
                            # Advance x0/x1 roughly by average char width if available
                            char_width = last_dict.get("adv") or (
                                last_dict.get("width", 0) / max(len(self.text), 1)
                            )
                            if isinstance(char_width, (int, float)) and char_width > 0:
                                shift = char_width * (extra_idx - len(self._char_dicts) + 1)
                                new_dict["x0"] = last_dict.get("x0", 0) + shift
                                new_dict["x1"] = last_dict.get("x1", 0) + shift
                            self._char_dicts.append(new_dict)
        except Exception as sync_err:  # pragma: no cover
            # Keep failures silent but logged; better to have outdated chars than crash.
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"TextElement: Failed to sync _char_dicts after text update: {sync_err}")

    @property
    def source(self) -> str:
        """Get the source of this text element (pdf or ocr)."""
        return self._obj.get("source", "pdf")

    @property
    def confidence(self) -> float:
        """Get the confidence score for OCR text elements."""
        return self._obj.get("confidence", 1.0)

    @property
    def fontname(self) -> str:
        """Get the font name."""
        # First check if we have a real fontname from PDF resources
        if "real_fontname" in self._obj:
            return self._obj["real_fontname"]
        # Otherwise use standard fontname
        return self._obj.get("fontname", "") or self._obj.get("font", "")

    @property
    def font_family(self) -> str:
        """
        Get a cleaner font family name by stripping PDF-specific prefixes.

        PDF font names often include prefixes like 'ABCDEF+' followed by the font name
        or unique identifiers. This method attempts to extract a more readable font name.
        """
        font = self.fontname

        # Remove common PDF font prefixes (e.g., 'ABCDEF+')
        if "+" in font:
            font = font.split("+", 1)[1]

        # Try to extract common font family names
        common_fonts = [
            "Arial",
            "Helvetica",
            "Times",
            "Courier",
            "Calibri",
            "Cambria",
            "Georgia",
            "Verdana",
            "Tahoma",
            "Trebuchet",
        ]

        for common in common_fonts:
            if common.lower() in font.lower():
                return common

        return font

    @property
    def font_variant(self) -> str:
        """
        Get the font variant identifier (prefix before the '+' in PDF font names).

        PDF embeds font subsets with unique identifiers like 'AAAAAB+FontName'.
        Different variants of the same base font will have different prefixes.
        This can be used to differentiate text that looks different despite
        having the same font name and size.

        Returns:
            The font variant prefix, or empty string if no variant is present
        """
        font = self.fontname

        # Extract the prefix before '+' if it exists
        if "+" in font:
            return font.split("+", 1)[0]

        return ""

    @property
    def size(self) -> float:
        """Get the font size."""
        return self._obj.get("size", 0)

    @property
    def color(self) -> tuple:
        """Get the text color (RGB tuple)."""
        # PDFs often use non-RGB values, so we handle different formats
        # In pdfplumber, colors can be in various formats depending on the PDF
        color = self._obj.get("non_stroking_color", (0, 0, 0))

        # If it's a single value, treat as grayscale
        if isinstance(color, (int, float)):
            return (color, color, color)

        # If it's a tuple of 3 values, treat as RGB
        if isinstance(color, tuple) and len(color) == 3:
            return color

        # If it's a tuple of 4 values, treat as CMYK and convert to approximate RGB
        if isinstance(color, tuple) and len(color) == 4:
            c, m, y, k = color
            r = 1 - min(1, c + k)
            g = 1 - min(1, m + k)
            b = 1 - min(1, y + k)
            return (r, g, b)

        # Default to black
        return (0, 0, 0)

    def extract_text(self, keep_blank_chars=True, strip: Optional[bool] = True, **kwargs) -> str:
        """
        Extract text from this element.

        Args:
            keep_blank_chars: Retained for API compatibility (unused).
            strip: If True (default) remove leading/trailing whitespace. Users may
                   pass ``strip=False`` to preserve whitespace exactly as stored.
            **kwargs: Accepted for forward-compatibility and ignored here.

        Returns:
            The text content, optionally stripped.
        """
        # Basic retrieval
        result = self.text or ""

        # Apply optional stripping – align with global convention where simple
        # element extraction is stripped by default.
        if strip:
            result = result.strip()

        return result

    def contains(self, substring: str, case_sensitive: bool = True) -> bool:
        """
        Check if this text element contains a substring.

        Args:
            substring: The substring to check for
            case_sensitive: Whether the check is case-sensitive

        Returns:
            True if the text contains the substring
        """
        if case_sensitive:
            return substring in self.text
        else:
            return substring.lower() in self.text.lower()

    def matches(self, pattern: str) -> bool:
        """
        Check if this text element matches a regular expression pattern.

        Args:
            pattern: Regular expression pattern

        Returns:
            True if the text matches the pattern
        """
        import re

        return bool(re.search(pattern, self.text))

    @property
    def bold(self) -> bool:
        """
        Check if the text is bold based on multiple indicators in the PDF.

        PDFs encode boldness in several ways:
        1. Font name containing 'bold' or 'black'
        2. Font descriptor flags (bit 2 indicates bold)
        3. StemV value (thickness of vertical stems)
        4. Font weight values (700+ is typically bold)
        5. Text rendering mode 2 (fill and stroke)
        """
        # Check font name (original method)
        fontname = self.fontname.lower()
        if "bold" in fontname or "black" in fontname or self.fontname.endswith("-B"):
            return True

        # Check font descriptor flags if available (bit 2 = bold)
        flags = self._obj.get("flags")
        if flags is not None and (flags & 4) != 0:  # Check if bit 2 is set
            return True

        # Check StemV (vertical stem width) if available
        # Higher StemV values indicate bolder fonts
        stemv = self._obj.get("stemv") or self._obj.get("StemV")
        if stemv is not None and isinstance(stemv, (int, float)) and stemv > 120:
            return True

        # Check font weight if available (700+ is typically bold)
        weight = self._obj.get("weight") or self._obj.get("FontWeight")
        if weight is not None and isinstance(weight, (int, float)) and weight >= 700:
            return True

        # Check text rendering mode (mode 2 = fill and stroke, can make text appear bold)
        render_mode = self._obj.get("render_mode")
        if render_mode is not None and render_mode == 2:
            return True

        # Additional check: if we have text with the same font but different paths/strokes
        # Path widths or stroke widths can indicate boldness
        stroke_width = self._obj.get("stroke_width") or self._obj.get("lineWidth")
        if stroke_width is not None and isinstance(stroke_width, (int, float)) and stroke_width > 0:
            return True

        return False

    @property
    def italic(self) -> bool:
        """
        Check if the text is italic based on multiple indicators in the PDF.

        PDFs encode italic (oblique) text in several ways:
        1. Font name containing 'italic' or 'oblique'
        2. Font descriptor flags (bit 6 indicates italic)
        3. Text with non-zero slant angle
        """
        # Check font name (original method)
        fontname = self.fontname.lower()
        if "italic" in fontname or "oblique" in fontname or self.fontname.endswith("-I"):
            return True

        # Check font descriptor flags if available (bit 6 = italic)
        flags = self._obj.get("flags")
        if flags is not None and (flags & 64) != 0:  # Check if bit 6 is set
            return True

        # Check italic angle if available
        # Non-zero italic angle indicates italic font
        italic_angle = self._obj.get("italic_angle") or self._obj.get("ItalicAngle")
        if (
            italic_angle is not None
            and isinstance(italic_angle, (int, float))
            and italic_angle != 0
        ):
            return True

        return False

    def __repr__(self) -> str:
        """String representation of the text element."""
        if self.text:
            preview = self.text[:10] + "..." if len(self.text) > 10 else self.text
        else:
            preview = "..."
        font_style = []
        if self.bold:
            font_style.append("bold")
        if self.italic:
            font_style.append("italic")
        style_str = f", style={font_style}" if font_style else ""

        # Use font_family for display but include raw fontname and variant
        font_display = self.font_family
        variant = self.font_variant
        variant_str = f", variant='{variant}'" if variant else ""

        if font_display != self.fontname and "+" in self.fontname:
            base_font = self.fontname.split("+", 1)[1]
            font_display = f"{font_display} ({base_font})"

        return f"<TextElement text='{preview}' font='{font_display}'{variant_str} size={self.size}{style_str} bbox={self.bbox}>"

    def font_info(self) -> dict:
        """
        Get detailed font information for this text element.

        Returns a dictionary with all available font-related properties,
        useful for debugging font detection issues.
        """
        info = {
            "text": self.text,
            "fontname": self.fontname,
            "font_family": self.font_family,
            "font_variant": self.font_variant,
            "size": self.size,
            "bold": self.bold,
            "italic": self.italic,
            "color": self.color,
        }

        # Include raw font properties from the PDF
        font_props = [
            "flags",
            "stemv",
            "StemV",
            "weight",
            "FontWeight",
            "render_mode",
            "stroke_width",
            "lineWidth",
        ]

        for prop in font_props:
            if prop in self._obj:
                info[f"raw_{prop}"] = self._obj[prop]

        return info
