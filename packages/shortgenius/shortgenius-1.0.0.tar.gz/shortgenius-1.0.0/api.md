# Music

## Genres

Types:

```python
from shortgenius.types.music import GenreListResponse, GenreRetrieveTracksResponse
```

Methods:

- <code title="get /music/genres">client.music.genres.<a href="./src/shortgenius/resources/music/genres.py">list</a>() -> <a href="./src/shortgenius/types/music/genre_list_response.py">GenreListResponse</a></code>
- <code title="get /music/genres/{id}">client.music.genres.<a href="./src/shortgenius/resources/music/genres.py">retrieve_tracks</a>(id) -> <a href="./src/shortgenius/types/music/genre_retrieve_tracks_response.py">GenreRetrieveTracksResponse</a></code>

# Videos

Types:

```python
from shortgenius.types import DraftScene, Video, VideoListResponse, VideoGenerateTopicsResponse
```

Methods:

- <code title="post /videos">client.videos.<a href="./src/shortgenius/resources/videos/videos.py">create</a>(\*\*<a href="src/shortgenius/types/video_create_params.py">params</a>) -> <a href="./src/shortgenius/types/video.py">Video</a></code>
- <code title="get /videos/{id}">client.videos.<a href="./src/shortgenius/resources/videos/videos.py">retrieve</a>(id) -> <a href="./src/shortgenius/types/video.py">Video</a></code>
- <code title="get /videos">client.videos.<a href="./src/shortgenius/resources/videos/videos.py">list</a>(\*\*<a href="src/shortgenius/types/video_list_params.py">params</a>) -> <a href="./src/shortgenius/types/video_list_response.py">VideoListResponse</a></code>
- <code title="post /videos/topics">client.videos.<a href="./src/shortgenius/resources/videos/videos.py">generate_topics</a>(\*\*<a href="src/shortgenius/types/video_generate_topics_params.py">params</a>) -> <a href="./src/shortgenius/types/video_generate_topics_response.py">VideoGenerateTopicsResponse</a></code>

## Drafts

Types:

```python
from shortgenius.types.videos import DraftVideo, DraftCreateQuizResponse
```

Methods:

- <code title="post /videos/drafts">client.videos.drafts.<a href="./src/shortgenius/resources/videos/drafts.py">create</a>(\*\*<a href="src/shortgenius/types/videos/draft_create_params.py">params</a>) -> <a href="./src/shortgenius/types/videos/draft_video.py">DraftVideo</a></code>
- <code title="post /videos/drafts/script">client.videos.drafts.<a href="./src/shortgenius/resources/videos/drafts.py">create_from_script</a>(\*\*<a href="src/shortgenius/types/videos/draft_create_from_script_params.py">params</a>) -> <a href="./src/shortgenius/types/videos/draft_video.py">DraftVideo</a></code>
- <code title="post /videos/drafts/url">client.videos.drafts.<a href="./src/shortgenius/resources/videos/drafts.py">create_from_url</a>(\*\*<a href="src/shortgenius/types/videos/draft_create_from_url_params.py">params</a>) -> <a href="./src/shortgenius/types/videos/draft_video.py">DraftVideo</a></code>
- <code title="post /videos/drafts/news">client.videos.drafts.<a href="./src/shortgenius/resources/videos/drafts.py">create_news</a>(\*\*<a href="src/shortgenius/types/videos/draft_create_news_params.py">params</a>) -> <a href="./src/shortgenius/types/videos/draft_video.py">DraftVideo</a></code>
- <code title="post /videos/drafts/quiz">client.videos.drafts.<a href="./src/shortgenius/resources/videos/drafts.py">create_quiz</a>(\*\*<a href="src/shortgenius/types/videos/draft_create_quiz_params.py">params</a>) -> <a href="./src/shortgenius/types/videos/draft_create_quiz_response.py">DraftCreateQuizResponse</a></code>

# Series

Types:

```python
from shortgenius.types import Series, SeriesRetrieveResponse, SeriesListResponse
```

Methods:

- <code title="post /series">client.series.<a href="./src/shortgenius/resources/series.py">create</a>(\*\*<a href="src/shortgenius/types/series_create_params.py">params</a>) -> <a href="./src/shortgenius/types/series.py">Series</a></code>
- <code title="get /series/{id}">client.series.<a href="./src/shortgenius/resources/series.py">retrieve</a>(id) -> <a href="./src/shortgenius/types/series_retrieve_response.py">SeriesRetrieveResponse</a></code>
- <code title="get /series">client.series.<a href="./src/shortgenius/resources/series.py">list</a>(\*\*<a href="src/shortgenius/types/series_list_params.py">params</a>) -> <a href="./src/shortgenius/types/series_list_response.py">SeriesListResponse</a></code>

# Connections

Types:

```python
from shortgenius.types import Connection, ConnectionListResponse
```

Methods:

- <code title="get /connections">client.connections.<a href="./src/shortgenius/resources/connections.py">list</a>() -> <a href="./src/shortgenius/types/connection_list_response.py">ConnectionListResponse</a></code>

# Health

Types:

```python
from shortgenius.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/shortgenius/resources/health.py">check</a>() -> <a href="./src/shortgenius/types/health_check_response.py">HealthCheckResponse</a></code>

# Images

Types:

```python
from shortgenius.types import (
    Image,
    ImageRetrieveResponse,
    ImageListResponse,
    ImageListStylesResponse,
)
```

Methods:

- <code title="post /images">client.images.<a href="./src/shortgenius/resources/images.py">create</a>(\*\*<a href="src/shortgenius/types/image_create_params.py">params</a>) -> <a href="./src/shortgenius/types/image.py">Image</a></code>
- <code title="get /images/{id}">client.images.<a href="./src/shortgenius/resources/images.py">retrieve</a>(id) -> <a href="./src/shortgenius/types/image_retrieve_response.py">ImageRetrieveResponse</a></code>
- <code title="get /images">client.images.<a href="./src/shortgenius/resources/images.py">list</a>(\*\*<a href="src/shortgenius/types/image_list_params.py">params</a>) -> <a href="./src/shortgenius/types/image_list_response.py">ImageListResponse</a></code>
- <code title="get /images/styles">client.images.<a href="./src/shortgenius/resources/images.py">list_styles</a>() -> <a href="./src/shortgenius/types/image_list_styles_response.py">ImageListStylesResponse</a></code>

# Audio

Types:

```python
from shortgenius.types import Audio, AudioListAudioResponse
```

Methods:

- <code title="post /audio/speech">client.audio.<a href="./src/shortgenius/resources/audio/audio.py">create_speech</a>(\*\*<a href="src/shortgenius/types/audio_create_speech_params.py">params</a>) -> <a href="./src/shortgenius/types/audio/audio.py">Audio</a></code>
- <code title="get /audio">client.audio.<a href="./src/shortgenius/resources/audio/audio.py">list_audio</a>(\*\*<a href="src/shortgenius/types/audio_list_audio_params.py">params</a>) -> <a href="./src/shortgenius/types/audio_list_audio_response.py">AudioListAudioResponse</a></code>
- <code title="get /audio/{id}">client.audio.<a href="./src/shortgenius/resources/audio/audio.py">retrieve_audio</a>(id) -> <a href="./src/shortgenius/types/audio/audio.py">Audio</a></code>

## Voices

Types:

```python
from shortgenius.types.audio import Voice, VoiceListVoicesResponse
```

Methods:

- <code title="get /audio/voices">client.audio.voices.<a href="./src/shortgenius/resources/audio/voices.py">list_voices</a>(\*\*<a href="src/shortgenius/types/audio/voice_list_voices_params.py">params</a>) -> <a href="./src/shortgenius/types/audio/voice_list_voices_response.py">VoiceListVoicesResponse</a></code>
- <code title="get /audio/voices/{id}">client.audio.voices.<a href="./src/shortgenius/resources/audio/voices.py">retrieve_voice</a>(id) -> <a href="./src/shortgenius/types/audio/voice.py">Voice</a></code>

# Credits

Types:

```python
from shortgenius.types import CreditListResponse
```

Methods:

- <code title="get /credits">client.credits.<a href="./src/shortgenius/resources/credits.py">list</a>() -> <a href="./src/shortgenius/types/credit_list_response.py">CreditListResponse</a></code>
