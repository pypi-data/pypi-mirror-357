"""
Test the _headers module.
"""

import ssl
from collections.abc import Generator
from unittest.mock import Mock, patch
from urllib.request import Request

import pytest

from xil._headers import _DEFAULT_CONTEXT, get_url_response


@pytest.fixture(name="url")
def fixture_url() -> str:
    """A tests URL that can be used (no actual call is made)"""
    return "http://httpbin.org/get"


@pytest.fixture(name="mock_urlopen")
def fixture_mock_urlopen() -> Generator[Mock, None, None]:
    """Mock the call to an external URL"""
    with patch("urllib.request.urlopen", autospec=True) as mock:
        yield mock


def _compare_requests(request1: Request, request2: Request) -> bool:
    """
    This is required since two Request objects with the same data are not equal.
    Compare here only the attributes of interest.
    """
    return (
        request1.full_url == request2.full_url and request1.headers == request2.headers
    )


@pytest.mark.parametrize(
    ("set_context", "expected_context"), [(False, None), (True, _DEFAULT_CONTEXT)]
)
def test_get_url_response_context(
    url: str,
    set_context: bool,
    expected_context: ssl.SSLContext | None,
    mock_urlopen: Mock,
) -> None:
    """Test that get_url_response sets an SSL context when it is asked to"""
    get_url_response(url, set_context=set_context)
    mock_urlopen.assert_called_once()
    assert mock_urlopen.call_args.kwargs == {
        "context": expected_context,
    }, "The context passed to urlopen is different than expected"
