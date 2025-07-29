"""
Corpus Matcher - Fast substring matching in large text corpora.

This library provides efficient fuzzy string matching capabilities using
optimized Levenshtein distance algorithms.
"""

from .corpus_matcher import find_best_substring_match, MatchResult

__version__ = "1.0.0"
__all__ = ["find_best_substring_match", "MatchResult"]
