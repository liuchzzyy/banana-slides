"""
AI Providers factory module

Provides factory functions to get text/image generation providers
using OpenAI-compatible API format.

Configuration:
    OPENAI_API_KEY: API key (required)
    OPENAI_API_BASE: API base URL (default: https://api.openai.com/v1)
    TEXT_MODEL: Text generation model (required)
    IMAGE_MODEL: Image generation model (required)
"""

import logging
from typing import Dict, Any, Optional

from .text import TextProvider, OpenAITextProvider
from .image import ImageProvider, OpenAIImageProvider
from ...config import get_config

logger = logging.getLogger(__name__)

__all__ = [
    "TextProvider",
    "OpenAITextProvider",
    "ImageProvider",
    "OpenAIImageProvider",
    "get_text_provider",
    "get_image_provider",
]


def _get_provider_config() -> Dict[str, Any]:
    """
    Get OpenAI provider configuration from project config
    """
    config = get_config()

    api_key = config.OPENAI_API_KEY
    api_base = config.OPENAI_API_BASE or "https://api.openai.com/v1"

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required. Please set it in your .env file or environment."
        )

    logger.info(f"Provider config - api_base: {api_base}")

    return {
        "api_key": api_key,
        "api_base": api_base,
    }


def get_text_provider(model: Optional[str] = None) -> TextProvider:
    """
    Factory function to get text generation provider

    Args:
        model: Model name to use. If None, uses TEXT_MODEL from environment.

    Returns:
        OpenAITextProvider instance
    """
    config = get_config()
    provider_config = _get_provider_config()

    if model is None:
        model = config.TEXT_MODEL
        if not model:
            raise ValueError(
                "TEXT_MODEL is required. Please set it in your .env file or pass model parameter."
            )

    logger.info(f"Creating text provider with model: {model}")
    return OpenAITextProvider(
        api_key=str(provider_config["api_key"]),
        api_base=str(provider_config["api_base"]),
        model=str(model),
    )


def get_image_provider(model: Optional[str] = None) -> ImageProvider:
    """
    Factory function to get image generation provider

    Args:
        model: Model name to use. If None, uses IMAGE_MODEL from environment.

    Returns:
        OpenAIImageProvider instance
    """
    config = get_config()
    provider_config = _get_provider_config()

    if model is None:
        model = config.IMAGE_MODEL
        if not model:
            raise ValueError(
                "IMAGE_MODEL is required. Please set it in your .env file or pass model parameter."
            )

    logger.info(f"Creating image provider with model: {model}")
    return OpenAIImageProvider(
        api_key=str(provider_config["api_key"]),
        api_base=str(provider_config["api_base"]),
        model=str(model),
    )
