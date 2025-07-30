# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types.audio import Voice, VoiceListVoicesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVoices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_voices(self, client: Shortgenius) -> None:
        voice = client.audio.voices.list_voices()
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_voices_with_all_params(self, client: Shortgenius) -> None:
        voice = client.audio.voices.list_voices(
            limit=10000000,
            locale="af-ZA",
            page=0,
        )
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_voices(self, client: Shortgenius) -> None:
        response = client.audio.voices.with_raw_response.list_voices()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = response.parse()
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_voices(self, client: Shortgenius) -> None:
        with client.audio.voices.with_streaming_response.list_voices() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = response.parse()
            assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_voice(self, client: Shortgenius) -> None:
        voice = client.audio.voices.retrieve_voice(
            "id",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_voice(self, client: Shortgenius) -> None:
        response = client.audio.voices.with_raw_response.retrieve_voice(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = response.parse()
        assert_matches_type(Voice, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_voice(self, client: Shortgenius) -> None:
        with client.audio.voices.with_streaming_response.retrieve_voice(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = response.parse()
            assert_matches_type(Voice, voice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_voice(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.audio.voices.with_raw_response.retrieve_voice(
                "",
            )


class TestAsyncVoices:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_voices(self, async_client: AsyncShortgenius) -> None:
        voice = await async_client.audio.voices.list_voices()
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_voices_with_all_params(self, async_client: AsyncShortgenius) -> None:
        voice = await async_client.audio.voices.list_voices(
            limit=10000000,
            locale="af-ZA",
            page=0,
        )
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_voices(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.audio.voices.with_raw_response.list_voices()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = await response.parse()
        assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_voices(self, async_client: AsyncShortgenius) -> None:
        async with async_client.audio.voices.with_streaming_response.list_voices() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = await response.parse()
            assert_matches_type(VoiceListVoicesResponse, voice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_voice(self, async_client: AsyncShortgenius) -> None:
        voice = await async_client.audio.voices.retrieve_voice(
            "id",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_voice(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.audio.voices.with_raw_response.retrieve_voice(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = await response.parse()
        assert_matches_type(Voice, voice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_voice(self, async_client: AsyncShortgenius) -> None:
        async with async_client.audio.voices.with_streaming_response.retrieve_voice(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = await response.parse()
            assert_matches_type(Voice, voice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_voice(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.audio.voices.with_raw_response.retrieve_voice(
                "",
            )
