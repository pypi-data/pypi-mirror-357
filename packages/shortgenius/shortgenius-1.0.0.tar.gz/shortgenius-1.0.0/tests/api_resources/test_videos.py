# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types import (
    Video,
    VideoListResponse,
    VideoGenerateTopicsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVideos:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Shortgenius) -> None:
        video = client.videos.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Shortgenius) -> None:
        video = client.videos.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
            aspect_ratio="9:16",
            content_type="Custom",
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locale="af-ZA",
            publish_at="publish_at",
            quiz={
                "questions": [
                    {
                        "options": [
                            {
                                "correct": True,
                                "text": "text",
                            }
                        ],
                        "question": "question",
                    }
                ],
                "results": {
                    "categories": [
                        {
                            "score_range": "score_range",
                            "title": "title",
                        }
                    ],
                    "explanation": "explanation",
                    "header": "header",
                },
            },
            scenes=[
                {
                    "caption": "caption",
                    "first_image_description": "first_image_description",
                    "second_image_description": "second_image_description",
                    "title": "title",
                }
            ],
            soundtrack_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            soundtrack_playback_rate=50,
            soundtrack_volume=0,
            voice_id="voice_id",
            voice_playback_rate=50,
            voice_volume=0,
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Shortgenius) -> None:
        response = client.videos.with_raw_response.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Shortgenius) -> None:
        with client.videos.with_streaming_response.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Shortgenius) -> None:
        video = client.videos.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Shortgenius) -> None:
        response = client.videos.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Shortgenius) -> None:
        with client.videos.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.videos.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Shortgenius) -> None:
        video = client.videos.list()
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Shortgenius) -> None:
        video = client.videos.list(
            limit=100,
            page=0,
        )
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Shortgenius) -> None:
        response = client.videos.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Shortgenius) -> None:
        with client.videos.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(VideoListResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_topics(self, client: Shortgenius) -> None:
        video = client.videos.generate_topics()
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_topics_with_all_params(self, client: Shortgenius) -> None:
        video = client.videos.generate_topics(
            content_type="Custom",
            locale="af-ZA",
            number_of_topics=100,
            parent_topic="parent_topic",
        )
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_generate_topics(self, client: Shortgenius) -> None:
        response = client.videos.with_raw_response.generate_topics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_generate_topics(self, client: Shortgenius) -> None:
        with client.videos.with_streaming_response.generate_topics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncVideos:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
            aspect_ratio="9:16",
            content_type="Custom",
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locale="af-ZA",
            publish_at="publish_at",
            quiz={
                "questions": [
                    {
                        "options": [
                            {
                                "correct": True,
                                "text": "text",
                            }
                        ],
                        "question": "question",
                    }
                ],
                "results": {
                    "categories": [
                        {
                            "score_range": "score_range",
                            "title": "title",
                        }
                    ],
                    "explanation": "explanation",
                    "header": "header",
                },
            },
            scenes=[
                {
                    "caption": "caption",
                    "first_image_description": "first_image_description",
                    "second_image_description": "second_image_description",
                    "title": "title",
                }
            ],
            soundtrack_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            soundtrack_playback_rate=50,
            soundtrack_volume=0,
            voice_id="voice_id",
            voice_playback_rate=50,
            voice_volume=0,
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.with_raw_response.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = await response.parse()
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.with_streaming_response.create(
            caption="caption",
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = await response.parse()
        assert_matches_type(Video, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.videos.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.list()
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.list(
            limit=100,
            page=0,
        )
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = await response.parse()
        assert_matches_type(VideoListResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(VideoListResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_topics(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.generate_topics()
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_topics_with_all_params(self, async_client: AsyncShortgenius) -> None:
        video = await async_client.videos.generate_topics(
            content_type="Custom",
            locale="af-ZA",
            number_of_topics=100,
            parent_topic="parent_topic",
        )
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_generate_topics(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.videos.with_raw_response.generate_topics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = await response.parse()
        assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_generate_topics(self, async_client: AsyncShortgenius) -> None:
        async with async_client.videos.with_streaming_response.generate_topics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(VideoGenerateTopicsResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True
