"""
Utility functions for MultiMed-RAG system.
"""

from .wiki_crawler import crawl_wikipedia, crawl_wikipedia_entity
from .mayoclinic_crawler import search_mayo_clinic, crawl_mayoclinic_entity

__all__ = [
    "crawl_wikipedia",
    "crawl_wikipedia_entity",
    "search_mayo_clinic",
    "crawl_mayoclinic_entity"
]
