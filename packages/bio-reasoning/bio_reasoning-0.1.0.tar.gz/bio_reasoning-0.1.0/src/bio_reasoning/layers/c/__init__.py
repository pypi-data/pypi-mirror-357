"""
Layer C encompasses external knowledge sources - APIs, databases, and knowledge graphs - to provide access to large, dynamic, or regulated datasets that cannot reside fully within models.
"""

from .biorxiv import biorxiv_search_factory, medrxiv_search_factory

__all__ = [
    "biorxiv_search_factory",
    "medrxiv_search_factory",
]
