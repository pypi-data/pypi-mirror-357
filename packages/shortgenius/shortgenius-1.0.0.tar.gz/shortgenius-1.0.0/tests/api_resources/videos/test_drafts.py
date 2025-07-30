# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types.videos import (
    DraftVideo,
    DraftCreateQuizResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDrafts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create(
            duration="60",
            topic="topic",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create(
            duration="60",
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Shortgenius) -> None:
        response = client.videos.drafts.with_raw_response.create(
            duration="60",
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Shortgenius) -> None:
        with client.videos.drafts.with_streaming_response.create(
            duration="60",
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_from_script(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_from_script(
            script="script",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_from_script(self, client: Shortgenius) -> None:
        response = client.videos.drafts.with_raw_response.create_from_script(
            script="script",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_from_script(self, client: Shortgenius) -> None:
        with client.videos.drafts.with_streaming_response.create_from_script(
            script="script",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_from_url(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_from_url(
            url="url",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_from_url_with_all_params(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_from_url(
            url="url",
            locale="af-ZA",
            prompt="prompt",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_from_url(self, client: Shortgenius) -> None:
        response = client.videos.drafts.with_raw_response.create_from_url(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_from_url(self, client: Shortgenius) -> None:
        with client.videos.drafts.with_streaming_response.create_from_url(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_news(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_news(
            topic="topic",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_news_with_all_params(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_news(
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_news(self, client: Shortgenius) -> None:
        response = client.videos.drafts.with_raw_response.create_news(
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_news(self, client: Shortgenius) -> None:
        with client.videos.drafts.with_streaming_response.create_news(
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_quiz(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_quiz(
            topic="topic",
        )
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_quiz_with_all_params(self, client: Shortgenius) -> None:
        draft = client.videos.drafts.create_quiz(
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_quiz(self, client: Shortgenius) -> None:
        response = client.videos.drafts.with_raw_response.create_quiz(
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = response.parse()
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_quiz(self, client: Shortgenius) -> None:
        with client.videos.drafts.with_streaming_response.create_quiz(
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = response.parse()
            assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDrafts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create(
            duration="60",
            topic="topic",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create(
            duration="60",
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.drafts.with_raw_response.create(
            duration="60",
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = await response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.drafts.with_streaming_response.create(
            duration="60",
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = await response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_from_script(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_from_script(
            script="script",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_from_script(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.drafts.with_raw_response.create_from_script(
            script="script",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = await response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_from_script(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.drafts.with_streaming_response.create_from_script(
            script="script",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = await response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_from_url(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_from_url(
            url="url",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_from_url_with_all_params(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_from_url(
            url="url",
            locale="af-ZA",
            prompt="prompt",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_from_url(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.drafts.with_raw_response.create_from_url(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = await response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_from_url(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.drafts.with_streaming_response.create_from_url(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = await response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_news(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_news(
            topic="topic",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_news_with_all_params(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_news(
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_news(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.drafts.with_raw_response.create_news(
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = await response.parse()
        assert_matches_type(DraftVideo, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_news(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.drafts.with_streaming_response.create_news(
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = await response.parse()
            assert_matches_type(DraftVideo, draft, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_quiz(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_quiz(
            topic="topic",
        )
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_quiz_with_all_params(self, async_client: AsyncShortgenius) -> None:
        draft = await async_client.videos.drafts.create_quiz(
            topic="topic",
            locale="af-ZA",
        )
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_quiz(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.drafts.with_raw_response.create_quiz(
            topic="topic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        draft = await response.parse()
        assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_quiz(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.drafts.with_streaming_response.create_quiz(
            topic="topic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            draft = await response.parse()
            assert_matches_type(DraftCreateQuizResponse, draft, path=["response"])

        assert cast(Any, response.is_closed) is True
