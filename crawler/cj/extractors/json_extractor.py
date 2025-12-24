"""
JSON Extractor
Extracts data from embedded JSON in HTML pages
"""

import json
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def unescape_js_string(s: str) -> str:
    """
    Unescape a JavaScript string while preserving UTF-8 encoding.

    Handles common JavaScript escape sequences but preserves UTF-8 characters.
    """
    # Map of escape sequences
    escape_map = {
        r'\"': '"',
        r'\/': '/',
        r'\\': '\\',
        r'\n': '\n',
        r'\r': '\r',
        r'\t': '\t',
        r'\b': '\b',
        r'\f': '\f',
    }

    def replace_escape(match):
        """Replace escape sequence with its actual character"""
        seq = match.group(0)
        return escape_map.get(seq, seq)

    # Match escape sequences: backslash followed by specific characters
    pattern = r'\\["\\/nrtbf]'
    result = re.sub(pattern, replace_escape, s)

    return result


class JSONExtractor:
    """Extract data from embedded JSON in HTML"""

    @staticmethod
    def extract_broadcast_json(html: str) -> Optional[Dict[str, Any]]:
        """
        Extract window.__viewerConfig.broadcast JSON from HTML

        Args:
            html: The HTML content to parse

        Returns:
            Parsed broadcast data as dict, or None if not found
        """
        try:
            # Pattern to match window.__viewerConfig.broadcast = '...'
            pattern = r'window\.__viewerConfig\.broadcast\s*=\s*\'(.+?)\'\s*;'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                json_str = match.group(1)
                # Unescape JavaScript string while preserving UTF-8 encoding
                json_str = unescape_js_string(json_str)

                data = json.loads(json_str)
                logger.info("Successfully extracted broadcast JSON from HTML")
                return data
            else:
                logger.warning("Could not find window.__viewerConfig.broadcast in HTML")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse broadcast JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting broadcast JSON: {e}")
            return None

    @staticmethod
    def extract_shortclip_json(html: str) -> Optional[Dict[str, Any]]:
        """
        Extract window.__shortclip JSON from HTML

        Args:
            html: The HTML content to parse

        Returns:
            Parsed shortclip data as dict, or None if not found
        """
        try:
            # Pattern to match window.__shortclip = '...' or window.__shortclip = {...}
            # First try quoted JSON string
            pattern = r'window\.__shortclip\s*=\s*\'(.+?)\'\s*;'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                json_str = match.group(1)
                # Unescape JavaScript string while preserving UTF-8 encoding
                json_str = unescape_js_string(json_str)

                data = json.loads(json_str)
                logger.info("Successfully extracted shortclip JSON from HTML (quoted)")
                return data

            # Try unquoted JSON object
            pattern = r'window\.__shortclip\s*=\s*(\{.+?\});'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
                logger.info("Successfully extracted shortclip JSON from HTML (object)")
                return data

            logger.warning("Could not find window.__shortclip in HTML")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse shortclip JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting shortclip JSON: {e}")
            return None

    @staticmethod
    def extract_any_json(html: str, variable_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract any window.__viewerConfig.{variable_name} JSON from HTML

        Args:
            html: The HTML content to parse
            variable_name: The variable name to extract (e.g., 'broadcast', 'shortclip')

        Returns:
            Parsed data as dict, or None if not found
        """
        try:
            # Pattern to match window.__viewerConfig.{variable_name} = '...'
            pattern = rf'window\.__viewerConfig\.{re.escape(variable_name)}\s*=\s*\'(.+?)\'\s*;'
            match = re.search(pattern, html, re.DOTALL)

            if match:
                json_str = match.group(1)
                # Unescape JavaScript string while preserving UTF-8 encoding
                json_str = unescape_js_string(json_str)

                data = json.loads(json_str)
                logger.info(f"Successfully extracted {variable_name} JSON from HTML")
                return data
            else:
                logger.warning(f"Could not find window.__viewerConfig.{variable_name} in HTML")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {variable_name} JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting {variable_name} JSON: {e}")
            return None
