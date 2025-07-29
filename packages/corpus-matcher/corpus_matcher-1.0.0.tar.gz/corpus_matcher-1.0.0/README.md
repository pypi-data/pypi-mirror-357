# Corpus Matcher

Fast substring matching in large text corpora using optimized Levenshtein distance algorithms.

This library provides efficient fuzzy string matching capabilities, particularly useful for finding the best matching substring within large text corpora. It implements both a quick heuristic approach and a thorough search algorithm to balance speed and accuracy.

## Features

- **Dual Algorithm Approach**: Quick heuristic matching for speed, with fallback to thorough search for accuracy
- **Parallel Processing**: Leverages joblib for multi-threaded processing
- **Caching**: Built-in result caching using joblib Memory
- **Case Sensitivity Control**: Optional case-sensitive or case-insensitive matching
- **Configurable Parameters**: Adjustable step factors and search granularity

## Installation

```bash
pip install corpus-matcher
```

## Quick Start

```python
from corpus_matcher import find_best_substring_match

# Basic usage
query = "machine learning algorithms"
corpus = "This document discusses various machine learning algorithms and their applications in data science."

result = find_best_substring_match(query, corpus)

print(f"Best matches: {result.matches}")
print(f"Similarity ratio: {result.ratio}")
print(f"Distance: {result.distance}")
print(f"Quick match used: {result.quick_match_used}")
```

## Advanced Usage

```python
from corpus_matcher import find_best_substring_match

# Case-insensitive matching with custom parameters
result = find_best_substring_match(
    query="PYTHON programming",
    corpus="Learn python programming from basics to advanced concepts",
    case_sensitive=False,
    step_factor=300,  # Higher step factor for more thorough search
    n_jobs=4  # Use 4 parallel jobs
)

print(f"Matches: {result.matches}")
print(f"Ratio: {result.ratio:.3f}")
```

## API Reference

### `find_best_substring_match(query, corpus, case_sensitive=True, step_factor=500, n_jobs=-1)`

Find the best matching substring(s) in a corpus for a given query.

**Parameters:**
- `query` (str): The text to search for
- `corpus` (str): The text to search within
- `case_sensitive` (bool, optional): Whether matching should be case-sensitive. Default: True
- `step_factor` (int, optional): Controls search resolution. Higher values = more thorough search. Default: 500
- `n_jobs` (int, optional): Number of parallel jobs (-1 for all available cores). Default: -1

**Returns:**
- `MatchResult`: Object containing matches, ratio, distance, and algorithm info

### `MatchResult`

A dataclass containing the results of the matching operation:

- `matches` (List[str]): List of best matching substrings
- `ratio` (float): Levenshtein similarity ratio (0-100)
- `distance` (float): Normalized Levenshtein distance (0-1)
- `quick_match_used` (bool): Whether the quick algorithm was sufficient

## Algorithm Details

The library uses a two-stage approach:

1. **Quick Match**: Identifies potential regions using word-based heuristics, then performs localized search
2. **Thorough Search**: Falls back to comprehensive n-gram analysis if quick match fails

This approach provides good performance for most use cases while maintaining accuracy.

## Requirements

- Python ≥ 3.8
- joblib
- rapidfuzz

## Development

This project was developed with assistance from [aider.chat](https://github.com/Aider-AI/aider/).

## License

GPL-v3
