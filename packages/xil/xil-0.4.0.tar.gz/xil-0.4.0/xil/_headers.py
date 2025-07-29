"""
Shared functionalities for retrieving URLs' data when headers are needed
"""

import http.client
import ssl
import urllib.request

USER_AGENT = "\
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/107.0.0.0 Safari/537.36"

UA_HEADER = {"User-Agent": USER_AGENT}

_DEFAULT_CONTEXT = ssl.create_default_context()
_DEFAULT_CONTEXT.set_ciphers("DEFAULT")


def get_url_response(
    url: str,
    set_context: bool = False,
) -> http.client.HTTPResponse:
    """
    Return the response from a URL with custom headers and SSL context when opening if
    set_context is True.
    """
    context = _DEFAULT_CONTEXT if set_context else None
    request = urllib.request.Request(url)
    return urllib.request.urlopen(  # type: ignore[no-any-return]
        request, context=context
    )
