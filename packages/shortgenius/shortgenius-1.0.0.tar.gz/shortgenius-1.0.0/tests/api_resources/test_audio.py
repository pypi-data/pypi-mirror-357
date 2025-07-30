# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types import AudioListAudioResponse
from shortgenius.types.audio import Audio

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAudio:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_speech(self, client: Shortgenius) -> None:
        audio = client.audio.create_speech(
            text="text",
            voice_id="voice_id",
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_speech_with_all_params(self, client: Shortgenius) -> None:
        audio = client.audio.create_speech(
            text="text",
            voice_id="voice_id",
            locale="af-ZA",
            wait_for_generation=True,
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_speech(self, client: Shortgenius) -> None:
        response = client.audio.with_raw_response.create_speech(
            text="text",
            voice_id="voice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = response.parse()
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_speech(self, client: Shortgenius) -> None:
        with client.audio.with_streaming_response.create_speech(
            text="text",
            voice_id="voice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = response.parse()
            assert_matches_type(Audio, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_audio(self, client: Shortgenius) -> None:
        audio = client.audio.list_audio()
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_audio_with_all_params(self, client: Shortgenius) -> None:
        audio = client.audio.list_audio(
            limit=200,
            page=0,
        )
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_audio(self, client: Shortgenius) -> None:
        response = client.audio.with_raw_response.list_audio()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = response.parse()
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_audio(self, client: Shortgenius) -> None:
        with client.audio.with_streaming_response.list_audio() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = response.parse()
            assert_matches_type(AudioListAudioResponse, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_audio(self, client: Shortgenius) -> None:
        audio = client.audio.retrieve_audio(
            "id",
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_audio(self, client: Shortgenius) -> None:
        response = client.audio.with_raw_response.retrieve_audio(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = response.parse()
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_audio(self, client: Shortgenius) -> None:
        with client.audio.with_streaming_response.retrieve_audio(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = response.parse()
            assert_matches_type(Audio, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_audio(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.audio.with_raw_response.retrieve_audio(
                "",
            )


class TestAsyncAudio:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_speech(self, async_client: AsyncShortgenius) -> None:
        audio = await async_client.audio.create_speech(
            text="text",
            voice_id="voice_id",
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_speech_with_all_params(self, async_client: AsyncShortgenius) -> None:
        audio = await async_client.audio.create_speech(
            text="text",
            voice_id="voice_id",
            locale="af-ZA",
            wait_for_generation=True,
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_speech(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.audio.with_raw_response.create_speech(
            text="text",
            voice_id="voice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = await response.parse()
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_speech(self, async_client: AsyncShortgenius) -> None:
        async with async_client.audio.with_streaming_response.create_speech(
            text="text",
            voice_id="voice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = await response.parse()
            assert_matches_type(Audio, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_audio(self, async_client: AsyncShortgenius) -> None:
        audio = await async_client.audio.list_audio()
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_audio_with_all_params(self, async_client: AsyncShortgenius) -> None:
        audio = await async_client.audio.list_audio(
            limit=200,
            page=0,
        )
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_audio(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.audio.with_raw_response.list_audio()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = await response.parse()
        assert_matches_type(AudioListAudioResponse, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_audio(self, async_client: AsyncShortgenius) -> None:
        async with async_client.audio.with_streaming_response.list_audio() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = await response.parse()
            assert_matches_type(AudioListAudioResponse, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_audio(self, async_client: AsyncShortgenius) -> None:
        audio = await async_client.audio.retrieve_audio(
            "id",
        )
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_audio(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.audio.with_raw_response.retrieve_audio(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = await response.parse()
        assert_matches_type(Audio, audio, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_audio(self, async_client: AsyncShortgenius) -> None:
        async with async_client.audio.with_streaming_response.retrieve_audio(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = await response.parse()
            assert_matches_type(Audio, audio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_audio(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.audio.with_raw_response.retrieve_audio(
                "",
            )
