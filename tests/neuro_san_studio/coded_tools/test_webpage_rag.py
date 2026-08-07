# Copyright © 2025-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT

"""Unit tests for the WebpageRag coded tool."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from aiohttp import ClientError
from aiohttp import ClientResponseError

from neuro_san_studio.coded_tools.webpage_rag import WebpageRag


@pytest.mark.asyncio
async def test_load_documents_returns_documents_with_source_metadata():
    """A successful fetch yields a Document with the URL as metadata source."""
    with patch("neuro_san_studio.coded_tools.base_rag.OpenAIEmbeddings"):
        tool = WebpageRag()

    html = "<html><body><p>Hello world</p></body></html>"
    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "Hello world"

    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.text = AsyncMock(return_value=html)

    response_cm = MagicMock()
    response_cm.__aenter__ = AsyncMock(return_value=response)
    response_cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=response_cm)

    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("neuro_san_studio.coded_tools.webpage_rag.aiohttp.ClientSession", return_value=session_cm),
        patch("neuro_san_studio.coded_tools.webpage_rag.BeautifulSoup", return_value=mock_soup) as mock_bs,
    ):
        docs = await tool.load_documents({"urls": ["http://example.com"]})

    assert len(docs) == 1
    assert docs[0].page_content == "Hello world"
    assert docs[0].metadata["source"] == "http://example.com"
    mock_bs.assert_called_once()
    mock_soup.get_text.assert_called_once_with(separator=" ", strip=True)


@pytest.mark.asyncio
async def test_load_documents_skips_urls_with_http_error():
    """HTTP errors are logged and do not produce documents."""
    with patch("neuro_san_studio.coded_tools.base_rag.OpenAIEmbeddings"):
        tool = WebpageRag()

    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "ignored"

    exc = ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=404,
    )
    response = MagicMock()
    response.raise_for_status = MagicMock(side_effect=exc)
    response.text = AsyncMock(return_value="<html></html>")

    response_cm = MagicMock()
    response_cm.__aenter__ = AsyncMock(return_value=response)
    response_cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=response_cm)

    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("neuro_san_studio.coded_tools.webpage_rag.aiohttp.ClientSession", return_value=session_cm),
        patch("neuro_san_studio.coded_tools.webpage_rag.BeautifulSoup", return_value=mock_soup) as mock_bs,
    ):
        docs = await tool.load_documents({"urls": ["http://example.com"]})

    assert docs == []
    mock_bs.assert_not_called()


@pytest.mark.asyncio
async def test_load_documents_skips_urls_with_client_error():
    """Client connection errors are logged and do not produce documents."""
    with patch("neuro_san_studio.coded_tools.base_rag.OpenAIEmbeddings"):
        tool = WebpageRag()

    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "ignored"

    response_cm = MagicMock()
    response_cm.__aenter__ = AsyncMock(side_effect=ClientError("connection reset"))
    response_cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=response_cm)

    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("neuro_san_studio.coded_tools.webpage_rag.aiohttp.ClientSession", return_value=session_cm),
        patch("neuro_san_studio.coded_tools.webpage_rag.BeautifulSoup", return_value=mock_soup) as mock_bs,
    ):
        docs = await tool.load_documents({"urls": ["http://example.com"]})

    assert docs == []
    mock_bs.assert_not_called()
