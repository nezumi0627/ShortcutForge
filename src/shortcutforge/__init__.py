"""ShortcutForge: deterministic shortcut planning utilities."""

from .catalog import (
    ActionAvailability,
    ActionCatalog,
    CatalogAction,
    CatalogLanguage,
    IOSVersion,
    catalog_entries,
    get_default_catalog,
    render_catalog_markdown,
)

__version__ = "0.1.0"

__all__ = [
    "ActionAvailability",
    "ActionCatalog",
    "CatalogAction",
    "CatalogLanguage",
    "IOSVersion",
    "catalog_entries",
    "get_default_catalog",
    "render_catalog_markdown",
    "__version__",
]
