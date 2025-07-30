# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types.music import GenreListResponse, GenreRetrieveTracksResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGenres:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Shortgenius) -> None:
        genre = client.music.genres.list()
        assert_matches_type(GenreListResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Shortgenius) -> None:
        response = client.music.genres.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        genre = response.parse()
        assert_matches_type(GenreListResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Shortgenius) -> None:
        with client.music.genres.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            genre = response.parse()
            assert_matches_type(GenreListResponse, genre, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_tracks(self, client: Shortgenius) -> None:
        genre = client.music.genres.retrieve_tracks(
            "id",
        )
        assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_tracks(self, client: Shortgenius) -> None:
        response = client.music.genres.with_raw_response.retrieve_tracks(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        genre = response.parse()
        assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_tracks(self, client: Shortgenius) -> None:
        with client.music.genres.with_streaming_response.retrieve_tracks(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            genre = response.parse()
            assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_tracks(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.music.genres.with_raw_response.retrieve_tracks(
                "",
            )


class TestAsyncGenres:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncShortgenius) -> None:
        genre = await async_client.music.genres.list()
        assert_matches_type(GenreListResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.music.genres.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        genre = await response.parse()
        assert_matches_type(GenreListResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncShortgenius) -> None:
        async with async_client.music.genres.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            genre = await response.parse()
            assert_matches_type(GenreListResponse, genre, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_tracks(self, async_client: AsyncShortgenius) -> None:
        genre = await async_client.music.genres.retrieve_tracks(
            "id",
        )
        assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_tracks(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.music.genres.with_raw_response.retrieve_tracks(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        genre = await response.parse()
        assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_tracks(self, async_client: AsyncShortgenius) -> None:
        async with async_client.music.genres.with_streaming_response.retrieve_tracks(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            genre = await response.parse()
            assert_matches_type(GenreRetrieveTracksResponse, genre, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_tracks(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.music.genres.with_raw_response.retrieve_tracks(
                "",
            )
