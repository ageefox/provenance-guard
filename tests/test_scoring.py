import os

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-key")

from app import score_to_attribution


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.0, "likely_human"),
        (0.3999, "likely_human"),
        (0.4, "uncertain"),
        (0.6999, "uncertain"),
        (0.7, "likely_ai"),
        (1.0, "likely_ai"),
    ],
)
def test_attribution_threshold_boundaries(score, expected):
    assert score_to_attribution(score) == expected
