# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types import (
    Series,
    SeriesListResponse,
    SeriesRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSeries:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Shortgenius) -> None:
        series = client.series.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Shortgenius) -> None:
        series = client.series.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            aspect_ratio="9:16",
            content_type="Custom",
            duration=0,
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locale="af-ZA",
            parent_topic="parent_topic",
            schedule={
                "times": [
                    {
                        "day_of_week": 0,
                        "time_of_day": 0,
                    }
                ],
                "time_zone": "Pacific/Pago_Pago",
            },
            soundtrack_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            soundtrack_playback_rate=50,
            soundtrack_volume=0,
            topics=[{"topic": "x"}],
            voice_ids=["string"],
            voice_playback_rate=50,
            voice_volume=0,
        )
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Shortgenius) -> None:
        response = client.series.with_raw_response.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = response.parse()
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Shortgenius) -> None:
        with client.series.with_streaming_response.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = response.parse()
            assert_matches_type(Series, series, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Shortgenius) -> None:
        series = client.series.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Shortgenius) -> None:
        response = client.series.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = response.parse()
        assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Shortgenius) -> None:
        with client.series.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = response.parse()
            assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.series.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Shortgenius) -> None:
        series = client.series.list()
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Shortgenius) -> None:
        series = client.series.list(
            limit=200,
            page=0,
        )
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Shortgenius) -> None:
        response = client.series.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = response.parse()
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Shortgenius) -> None:
        with client.series.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = response.parse()
            assert_matches_type(SeriesListResponse, series, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSeries:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncShortgenius) -> None:
        series = await async_client.series.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncShortgenius) -> None:
        series = await async_client.series.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            aspect_ratio="9:16",
            content_type="Custom",
            duration=0,
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            locale="af-ZA",
            parent_topic="parent_topic",
            schedule={
                "times": [
                    {
                        "day_of_week": 0,
                        "time_of_day": 0,
                    }
                ],
                "time_zone": "Pacific/Pago_Pago",
            },
            soundtrack_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            soundtrack_playback_rate=50,
            soundtrack_volume=0,
            topics=[{"topic": "x"}],
            voice_ids=["string"],
            voice_playback_rate=50,
            voice_volume=0,
        )
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.series.with_raw_response.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = await response.parse()
        assert_matches_type(Series, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncShortgenius) -> None:
        async with async_client.series.with_streaming_response.create(
            connection_ids=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = await response.parse()
            assert_matches_type(Series, series, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncShortgenius) -> None:
        series = await async_client.series.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.series.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = await response.parse()
        assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        async with async_client.series.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = await response.parse()
            assert_matches_type(SeriesRetrieveResponse, series, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.series.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncShortgenius) -> None:
        series = await async_client.series.list()
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncShortgenius) -> None:
        series = await async_client.series.list(
            limit=200,
            page=0,
        )
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.series.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        series = await response.parse()
        assert_matches_type(SeriesListResponse, series, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncShortgenius) -> None:
        async with async_client.series.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            series = await response.parse()
            assert_matches_type(SeriesListResponse, series, path=["response"])

        assert cast(Any, response.is_closed) is True
