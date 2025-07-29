"""
Test corpus_matcher functionality using real Wikipedia content.

This test demonstrates the corpus matcher by finding a specific quote
about Napoleon from the Wikipedia page on Napoleon.
"""

import requests
from bs4 import BeautifulSoup
from corpus_matcher import find_best_substring_match, MatchResult


def test_napoleon_wikipedia_text_matching():
    """
    Test corpus matcher by finding a specific Napoleon quote from Wikipedia.

    This test fetches the Napoleon Wikipedia page, extracts the text content,
    and uses corpus_matcher to locate a specific historical quote about
    the Frankfurt proposals of 1813.
    """
    # Target text to find in the Wikipedia page
    target_text = (
        "The Frankfurt proposals were peace offered by the coalition in November 1813 "
        "under which Napoleon would remain emperor but France would be reduced to its natural frontiers."
    )

    # Fetch the Wikipedia page
    url = "https://en.wikipedia.org/wiki/Napoleon"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse HTML and extract text content
    soup = BeautifulSoup(response.content, "html.parser")

    # Remove script and style elements to get clean text
    for script in soup(["script", "style"]):
        script.extract()

    # Get text content from the main article body
    # Wikipedia articles are typically in div with id="mw-content-text"
    content_div = soup.find("div", {"id": "mw-content-text"})
    if content_div:
        corpus_text = content_div.get_text()
    else:
        # Fallback to full page text if specific div not found
        corpus_text = soup.get_text()

    # Clean up text: remove extra whitespace and normalize
    corpus_text = " ".join(corpus_text.split())

    # Use corpus matcher to find the target text
    result: MatchResult = find_best_substring_match(
        query=target_text,
        corpus=corpus_text,
        case_sensitive=False,  # More flexible matching
        step_factor=500,
        n_jobs=1,  # Single threaded for testing
    )

    # Assertions to verify the match quality
    assert isinstance(result, MatchResult), "Result should be a MatchResult object"
    assert len(result.matches) > 0, "Should find at least one match"
    assert result.ratio > 0.8, f"Match ratio should be high (>0.8), got {result.ratio}"
    assert (
        result.distance < 0.3
    ), f"Match distance should be low (<0.3), got {result.distance}"

    # Print results for manual inspection
    print(f"\nCorpus matcher results:")
    print(f"Number of matches found: {len(result.matches)}")
    print(f"Best match ratio: {result.ratio:.3f}")
    print(f"Best match distance: {result.distance:.3f}")
    print(f"Quick match used: {result.quick_match_used}")
    print(f"\nBest match(es):")
    for i, match in enumerate(result.matches[:3]):  # Show first 3 matches
        print(f"  {i+1}: {match[:100]}...")  # Show first 100 chars

    # Verify that the match contains key terms from the target
    best_match = result.matches[0].lower()
    key_terms = [
        "frankfurt",
        "proposals",
        "coalition",
        "november",
        "1813",
        "napoleon",
        "emperor",
    ]

    # At least some key terms should be present in the best match
    terms_found = sum(1 for term in key_terms if term in best_match)
    assert terms_found >= 4, f"Should find at least 4 key terms, found {terms_found}"


if __name__ == "__main__":
    # Allow running the test directly
    test_napoleon_wikipedia_text_matching()
    print("Test passed!")
