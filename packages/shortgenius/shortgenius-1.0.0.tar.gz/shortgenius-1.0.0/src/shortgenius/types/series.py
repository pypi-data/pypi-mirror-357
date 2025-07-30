# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .audio import voice
from .._models import BaseModel
from .connection import Connection

__all__ = [
    "Series",
    "ImageStyle",
    "ImageStyleRecommendation",
    "Schedule",
    "ScheduleTime",
    "Soundtrack",
    "SoundtrackRecommendation",
    "SoundtrackTrack",
    "Styles",
    "Voice",
    "CustomWatermark",
    "Thumbnail",
    "ThumbnailMedia",
    "ThumbnailMediaUnionMember0",
    "ThumbnailMediaUnionMember0Data",
    "ThumbnailMediaUnionMember0DataImage",
    "ThumbnailMediaUnionMember1",
    "ThumbnailMediaUnionMember1Data",
    "ThumbnailMediaUnionMember1DataSrc",
    "ThumbnailMediaUnionMember2",
    "ThumbnailMediaUnionMember2Data",
    "ThumbnailMediaUnionMember2DataUser",
    "ThumbnailMediaUnionMember2DataVideoFile",
    "ThumbnailMediaUnionMember2DataVideoPicture",
    "ThumbnailMediaUnionMember3",
    "ThumbnailMediaUnionMember3Data",
    "ThumbnailMediaUnionMember4",
    "ThumbnailMediaUnionMember4Data",
    "ThumbnailMediaUnionMember4DataVideos",
    "ThumbnailMediaUnionMember4DataVideosLarge",
    "ThumbnailMediaUnionMember4DataVideosMedium",
    "ThumbnailMediaUnionMember4DataVideosSmall",
    "ThumbnailMediaUnionMember4DataVideosTiny",
    "ThumbnailMediaUnionMember5",
    "ThumbnailMediaUnionMember5Data",
    "ThumbnailMediaUnionMember5DataLinks",
    "ThumbnailMediaUnionMember5DataURLs",
    "ThumbnailMediaUnionMember5DataUser",
    "ThumbnailMediaUnionMember5DataUserLinks",
    "ThumbnailMediaUnionMember5DataUserProfileImage",
    "ThumbnailMediaUnionMember6",
    "ThumbnailMediaUnionMember6Data",
    "ThumbnailMediaUnionMember6DataImageinfo",
    "ThumbnailMediaUnionMember7",
    "ThumbnailMediaUnionMember7Data",
    "ThumbnailMediaUnionMember7DataArtifact",
    "ThumbnailMediaUnionMember7DataResults",
    "ThumbnailMediaUnionMember7DataResultsImage",
    "ThumbnailMediaUnionMember7Metadata",
    "ThumbnailMediaUnionMember8",
    "ThumbnailMediaUnionMember8Data",
    "ThumbnailMediaUnionMember8DataResult",
    "ThumbnailMediaUnionMember8DataResultVideo",
    "ThumbnailMediaUnionMember8Metadata",
    "ThumbnailMediaUnionMember9",
    "ThumbnailMediaUnionMember9Data",
    "ThumbnailMediaUnionMember9Metadata",
    "ThumbnailMediaUnionMember10",
    "ThumbnailMediaUnionMember10Data",
    "ThumbnailMediaUnionMember10Metadata",
    "ThumbnailMediaUnionMember11",
    "ThumbnailMediaUnionMember11Data",
    "ThumbnailMediaUnionMember11Metadata",
    "ThumbnailMediaUnionMember12",
    "ThumbnailMediaUnionMember12Data",
    "ThumbnailMediaUnionMember12DataSourceMedia",
    "ThumbnailMediaUnionMember12DataResults",
    "ThumbnailMediaUnionMember12DataResultsImage",
    "ThumbnailMediaUnionMember12DataResultsMaskImage",
    "ThumbnailMediaUnionMember12Metadata",
    "ThumbnailMediaUnionMember13",
    "ThumbnailMediaUnionMember13Data",
    "ThumbnailMediaUnionMember13Metadata",
    "ThumbnailMediaUnionMember14",
    "ThumbnailMediaUnionMember14Data",
    "ThumbnailMediaUnionMember14DataData",
    "ThumbnailMediaUnionMember14DataResults",
    "ThumbnailMediaUnionMember14DataResultsImage",
    "ThumbnailMediaUnionMember14DataResultsMaskImage",
    "ThumbnailMediaUnionMember14Metadata",
    "ThumbnailMediaUnionMember15",
    "ThumbnailMediaUnionMember15Data",
    "ThumbnailMediaUnionMember15Metadata",
    "ThumbnailMediaUnionMember16",
    "ThumbnailMediaUnionMember16Data",
    "ThumbnailMediaUnionMember17",
    "ThumbnailMediaUnionMember17Data",
    "ThumbnailMediaUnionMember17Metadata",
    "TiktokSettings",
    "XSettings",
    "YoutubeSettings",
]


class ImageStyleRecommendation(BaseModel):
    id: str
    """Unique ID of the recommended image style."""

    reason: str
    """Reason for the recommended image style."""


class ImageStyle(BaseModel):
    id: Optional[str] = None
    """Unique ID of the current image style."""

    recommendations: Optional[List[ImageStyleRecommendation]] = None


class ScheduleTime(BaseModel):
    day_of_week: float

    time_of_day: float


class Schedule(BaseModel):
    time_zone: Literal[
        "Pacific/Pago_Pago",
        "America/Adak",
        "Pacific/Honolulu",
        "Pacific/Marquesas",
        "America/Anchorage",
        "America/Tijuana",
        "America/Los_Angeles",
        "America/Phoenix",
        "America/Denver",
        "America/Guatemala",
        "America/Chicago",
        "America/Chihuahua",
        "Pacific/Easter",
        "America/Mexico_City",
        "America/Regina",
        "America/Bogota",
        "America/Cancun",
        "America/New_York",
        "America/Port-au-Prince",
        "America/Havana",
        "America/Fort_Wayne",
        "America/Asuncion",
        "America/Halifax",
        "America/Caracas",
        "America/Cuiaba",
        "America/La_Paz",
        "America/Santiago",
        "America/Grand_Turk",
        "America/St_Johns",
        "America/Araguaina",
        "America/Sao_Paulo",
        "America/Cayenne",
        "America/Argentina/Buenos_Aires",
        "America/Godthab",
        "America/Montevideo",
        "America/Miquelon",
        "America/Bahia",
        "America/Noronha",
        "Atlantic/Azores",
        "Atlantic/Cape_Verde",
        "Europe/London",
        "Africa/Abidjan",
        "Europe/Berlin",
        "Europe/Belgrade",
        "Europe/Brussels",
        "Africa/Lagos",
        "Africa/Casablanca",
        "Africa/Windhoek",
        "Europe/Bucharest",
        "Asia/Beirut",
        "Africa/Cairo",
        "Asia/Damascus",
        "Asia/Gaza",
        "Africa/Maputo",
        "Europe/Kiev",
        "Asia/Jerusalem",
        "Europe/Kaliningrad",
        "Africa/Tripoli",
        "Asia/Amman",
        "Asia/Baghdad",
        "Europe/Istanbul",
        "Asia/Riyadh",
        "Europe/Minsk",
        "Europe/Moscow",
        "Africa/Nairobi",
        "Asia/Tehran",
        "Asia/Dubai",
        "Europe/Volgograd",
        "Asia/Baku",
        "Europe/Samara",
        "Indian/Mauritius",
        "Asia/Tbilisi",
        "Asia/Yerevan",
        "Asia/Kabul",
        "Asia/Tashkent",
        "Asia/Yekaterinburg",
        "Asia/Karachi",
        "Asia/Almaty",
        "Asia/Kolkata",
        "Asia/Colombo",
        "Asia/Kathmandu",
        "Asia/Dhaka",
        "Asia/Rangoon",
        "Asia/Novosibirsk",
        "Asia/Bangkok",
        "Asia/Barnaul",
        "Asia/Hovd",
        "Asia/Krasnoyarsk",
        "Asia/Tomsk",
        "Asia/Shanghai",
        "Asia/Irkutsk",
        "Asia/Kuala_Lumpur",
        "Australia/Perth",
        "Asia/Taipei",
        "Asia/Ulaanbaatar",
        "Asia/Pyongyang",
        "Australia/Eucla",
        "Asia/Chita",
        "Asia/Tokyo",
        "Asia/Seoul",
        "Asia/Yakutsk",
        "Australia/Adelaide",
        "Australia/Darwin",
        "Australia/Brisbane",
        "Australia/Sydney",
        "Pacific/Port_Moresby",
        "Australia/Hobart",
        "Asia/Vladivostok",
        "Australia/Lord_Howe",
        "Pacific/Bougainville",
        "Asia/Srednekolymsk",
        "Asia/Magadan",
        "Pacific/Norfolk",
        "Asia/Sakhalin",
        "Pacific/Noumea",
        "Asia/Anadyr",
        "Pacific/Auckland",
        "Pacific/Fiji",
        "Pacific/Chatham",
        "Pacific/Tongatapu",
        "Pacific/Apia",
        "Pacific/Kiritimati",
    ]

    times: List[ScheduleTime]


class SoundtrackRecommendation(BaseModel):
    reason: str
    """Reason for the recommended soundtrack."""

    url: str
    """URL of the recommended soundtrack."""

    id: Optional[str] = None
    """Unique ID of the recommended soundtrack."""


class SoundtrackTrack(BaseModel):
    url: str
    """URL of the soundtrack."""

    id: Optional[str] = None
    """Unique ID of the soundtrack."""


class Soundtrack(BaseModel):
    playback_rate: float
    """Soundtrack playback rate."""

    recommendations: List[SoundtrackRecommendation]

    tracks: List[SoundtrackTrack]
    """Soundtracks for the series."""

    volume: float
    """Soundtrack volume."""


class Styles(BaseModel):
    caption_active_word_background_color: Union[Literal["transparent"], List[str], None] = None

    caption_active_word_color: Union[Literal["transparent"], List[str], None] = None

    caption_active_word_stroke_color: Optional[str] = None

    caption_active_word_stroke_width: Optional[float] = None

    caption_alignment: Optional[
        Literal[
            "top-left",
            "top-center",
            "top-right",
            "middle-left",
            "middle-center",
            "middle-right",
            "bottom-left",
            "bottom-center",
            "bottom-right",
        ]
    ] = None

    caption_animation: Optional[Literal["ZoomIn"]] = None

    caption_background_color: Union[Literal["transparent"], List[str], None] = None

    caption_color: Union[Literal["transparent"], List[str], None] = None

    caption_display: Optional[Literal["karaoke", "phrase", "word", "none"]] = None

    caption_font_family: Optional[str] = None

    caption_font_size: Optional[float] = None

    caption_keyword_color: Union[Literal["transparent"], List[str], None] = None

    caption_rotate_occasionally: Optional[bool] = None

    caption_stroke_color: Optional[str] = None

    caption_stroke_width: Optional[float] = None

    caption_text_transform: Optional[Literal["lowercase", "none", "uppercase"]] = None


class Voice(BaseModel):
    playback_rate: float
    """Voice playback rate."""

    voices: List[voice.Voice]
    """Voices for the series."""

    volume: float
    """Voice volume."""


class CustomWatermark(BaseModel):
    text: str

    caption_alignment: Optional[
        Literal[
            "top-left",
            "top-center",
            "top-right",
            "middle-left",
            "middle-center",
            "middle-right",
            "bottom-left",
            "bottom-center",
            "bottom-right",
        ]
    ] = None

    caption_color: Union[Literal["transparent"], List[str], None] = None

    caption_font_family: Optional[str] = None

    caption_font_size: Optional[float] = None

    caption_stroke_color: Optional[str] = None

    caption_text_transform: Optional[Literal["lowercase", "none", "uppercase"]] = None


class ThumbnailMediaUnionMember0DataImage(BaseModel):
    byte_size: float

    context_link: str

    height: float

    thumbnail_height: float

    thumbnail_link: str

    thumbnail_width: float

    width: float


class ThumbnailMediaUnionMember0Data(BaseModel):
    display_link: str

    file_format: str

    html_snippet: str

    html_title: str

    image: ThumbnailMediaUnionMember0DataImage

    kind: str

    link: str

    mime: str

    snippet: str

    title: str


class ThumbnailMediaUnionMember0(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember0Data

    source: Literal["Google"]

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember1DataSrc(BaseModel):
    landscape: str

    large: str

    large2x: str

    medium: str

    original: str

    portrait: str

    small: str

    tiny: str


class ThumbnailMediaUnionMember1Data(BaseModel):
    id: float

    alt: Optional[str] = None

    avg_color: Optional[str] = None

    height: float

    liked: bool

    photographer: str

    photographer_id: float

    photographer_url: str

    src: ThumbnailMediaUnionMember1DataSrc

    url: str

    width: float


class ThumbnailMediaUnionMember1(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember1Data

    source: Literal["Pexels"]

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember2DataUser(BaseModel):
    id: float

    name: str

    url: str


class ThumbnailMediaUnionMember2DataVideoFile(BaseModel):
    id: float

    file_type: str

    fps: Optional[float] = None

    height: Optional[float] = None

    link: str

    quality: Optional[Literal["hd", "sd", "uhd"]] = None

    width: Optional[float] = None


class ThumbnailMediaUnionMember2DataVideoPicture(BaseModel):
    id: float

    nr: float

    picture: str


class ThumbnailMediaUnionMember2Data(BaseModel):
    id: float

    duration: float

    full_res: Optional[str] = None

    height: float

    image: str

    tags: List[str]

    url: str

    user: ThumbnailMediaUnionMember2DataUser

    video_files: List[ThumbnailMediaUnionMember2DataVideoFile]

    video_pictures: List[ThumbnailMediaUnionMember2DataVideoPicture]

    width: float


class ThumbnailMediaUnionMember2(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember2Data

    source: Literal["Pexels"]

    state: Literal["completed"]

    type: Literal["Video"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember3Data(BaseModel):
    id: float

    comments: float

    downloads: float

    large_image_u_r_l: str

    likes: float

    page_u_r_l: str

    preview_u_r_l: str

    user: str

    user_id: float

    user_image_u_r_l: str

    views: float

    webformat_u_r_l: str

    full_h_d_u_r_l: Optional[str] = None

    image_u_r_l: Optional[str] = None

    tags: Optional[str] = None

    vector_u_r_l: Optional[str] = None


class ThumbnailMediaUnionMember3(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember3Data

    source: Literal["Pixabay"]

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember4DataVideosLarge(BaseModel):
    height: float

    size: float

    thumbnail: str

    url: str

    width: float


class ThumbnailMediaUnionMember4DataVideosMedium(BaseModel):
    height: float

    size: float

    thumbnail: str

    url: str

    width: float


class ThumbnailMediaUnionMember4DataVideosSmall(BaseModel):
    height: float

    size: float

    thumbnail: str

    url: str

    width: float


class ThumbnailMediaUnionMember4DataVideosTiny(BaseModel):
    height: float

    size: float

    thumbnail: str

    url: str

    width: float


class ThumbnailMediaUnionMember4DataVideos(BaseModel):
    large: ThumbnailMediaUnionMember4DataVideosLarge

    medium: ThumbnailMediaUnionMember4DataVideosMedium

    small: ThumbnailMediaUnionMember4DataVideosSmall

    tiny: ThumbnailMediaUnionMember4DataVideosTiny


class ThumbnailMediaUnionMember4Data(BaseModel):
    id: float

    comments: float

    downloads: float

    likes: float

    page_u_r_l: str

    user: str

    user_id: float

    user_image_u_r_l: str

    videos: ThumbnailMediaUnionMember4DataVideos

    views: float

    duration: Optional[float] = None

    tags: Optional[str] = None


class ThumbnailMediaUnionMember4(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember4Data

    source: Literal["Pixabay"]

    state: Literal["completed"]

    type: Literal["Video"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember5DataLinks(BaseModel):
    download: str

    download_location: str

    html: str

    self: str


class ThumbnailMediaUnionMember5DataURLs(BaseModel):
    full: str

    raw: str

    regular: str

    small: str

    thumb: str


class ThumbnailMediaUnionMember5DataUserLinks(BaseModel):
    followers: str

    following: str

    html: str

    likes: str

    photos: str

    portfolio: str

    self: str


class ThumbnailMediaUnionMember5DataUserProfileImage(BaseModel):
    large: str

    medium: str

    small: str


class ThumbnailMediaUnionMember5DataUser(BaseModel):
    id: str

    bio: Optional[str] = None

    first_name: str

    instagram_username: Optional[str] = None

    last_name: Optional[str] = None

    links: ThumbnailMediaUnionMember5DataUserLinks

    location: Optional[str] = None

    name: str

    portfolio_url: Optional[str] = None

    profile_image: ThumbnailMediaUnionMember5DataUserProfileImage

    total_collections: float

    total_likes: float

    total_photos: float

    twitter_username: Optional[str] = None

    updated_at: str

    username: str


class ThumbnailMediaUnionMember5Data(BaseModel):
    id: str

    alt_description: Optional[str] = None

    blur_hash: Optional[str] = None

    color: Optional[str] = None

    created_at: str

    description: Optional[str] = None

    height: float

    likes: float

    links: ThumbnailMediaUnionMember5DataLinks

    promoted_at: Optional[str] = None

    updated_at: str

    urls: ThumbnailMediaUnionMember5DataURLs

    user: ThumbnailMediaUnionMember5DataUser

    width: float


class ThumbnailMediaUnionMember5(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember5Data

    source: Literal["Unsplash"]

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember6DataImageinfo(BaseModel):
    descriptionshorturl: str

    descriptionurl: str

    url: str


class ThumbnailMediaUnionMember6Data(BaseModel):
    imageinfo: List[ThumbnailMediaUnionMember6DataImageinfo]

    imagerepository: str

    index: float

    ns: float

    pageid: float

    title: str


class ThumbnailMediaUnionMember6(BaseModel):
    category: Literal["Stock"]

    data: ThumbnailMediaUnionMember6Data

    source: Literal["Wikimedia"]

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember7DataArtifact(BaseModel):
    finish_reason: Optional[str] = None

    seed: Optional[float] = None


class ThumbnailMediaUnionMember7DataResultsImage(BaseModel):
    content_type: str

    height: float

    url: str

    width: float


class ThumbnailMediaUnionMember7DataResults(BaseModel):
    has_nsfw_concepts: List[bool]

    images: List[ThumbnailMediaUnionMember7DataResultsImage]

    prompt: str

    seed: float

    timings: object


class ThumbnailMediaUnionMember7Data(BaseModel):
    artifacts: Optional[List[ThumbnailMediaUnionMember7DataArtifact]] = None

    path: Optional[str] = None

    result: Optional[str] = None

    results: Optional[ThumbnailMediaUnionMember7DataResults] = None


class ThumbnailMediaUnionMember7Metadata(BaseModel):
    prompt: str

    aspect_ratio: Optional[Literal["Portrait 9:16", "Landscape 16:9", "Square 1:1"]] = None

    image_style_preset_id: Optional[str] = None

    rephrased_prompt: Optional[str] = None

    translated_prompt: Optional[str] = None


class ThumbnailMediaUnionMember7(BaseModel):
    id: str

    category: Literal["AIGenerated"]

    data: Optional[ThumbnailMediaUnionMember7Data] = None

    metadata: ThumbnailMediaUnionMember7Metadata

    source: Optional[
        Literal[
            "dall-e-3",
            "stability.stable-diffusion-xl-v1",
            "fal-ai/flux-pro",
            "fal-ai/flux-pro/v1.1",
            "fal-ai/flux-pro/v1.1-ultra",
            "fal-ai/flux-realism",
        ]
    ] = None

    state: Literal["pending", "generating", "completed", "error", "request_smart_motion", "placeholder"]

    type: Literal["GeneratedImage"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember8DataResultVideo(BaseModel):
    url: str

    content_type: Optional[str] = None

    file_data: Optional[str] = None

    file_name: Optional[str] = None

    file_size: Optional[float] = None


class ThumbnailMediaUnionMember8DataResult(BaseModel):
    seed: float

    video: ThumbnailMediaUnionMember8DataResultVideo


class ThumbnailMediaUnionMember8Data(BaseModel):
    path: Optional[str] = None

    result: Optional[ThumbnailMediaUnionMember8DataResult] = None


class ThumbnailMediaUnionMember8Metadata(BaseModel):
    parent_media_id: Optional[str] = None

    source_image_url: Optional[str] = None


class ThumbnailMediaUnionMember8(BaseModel):
    id: str

    category: Literal["AIGenerated"]

    data: Optional[ThumbnailMediaUnionMember8Data] = None

    metadata: ThumbnailMediaUnionMember8Metadata

    source: Optional[Literal["fal-ai/stable-video"]] = None

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["GeneratedVideo"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember9Data(BaseModel):
    luma_id: Optional[str] = None


class ThumbnailMediaUnionMember9Metadata(BaseModel):
    prompt: str

    parent_media_id: Optional[str] = None

    source_image_url: Optional[str] = None


class ThumbnailMediaUnionMember9(BaseModel):
    id: str

    category: Literal["AIGenerated"]

    data: Optional[ThumbnailMediaUnionMember9Data] = None

    metadata: ThumbnailMediaUnionMember9Metadata

    source: Optional[Literal["luma-ai"]] = None

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["LumaGeneratedVideo"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember10Data(BaseModel):
    alt: Optional[str] = None

    key: str

    upload_id: str

    uploaded_at: Optional[str] = None


class ThumbnailMediaUnionMember10Metadata(BaseModel):
    content_type: Optional[str] = None


class ThumbnailMediaUnionMember10(BaseModel):
    id: str

    category: Literal["UserUploaded"]

    data: ThumbnailMediaUnionMember10Data

    metadata: ThumbnailMediaUnionMember10Metadata

    source: Literal["Upload", "ImagePicker"]

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserImage"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember11Data(BaseModel):
    alt: Optional[str] = None

    key: str

    upload_id: str

    uploaded_at: Optional[str] = None


class ThumbnailMediaUnionMember11Metadata(BaseModel):
    content_type: Optional[str] = None


class ThumbnailMediaUnionMember11(BaseModel):
    id: str

    category: Literal["UserUploaded"]

    data: ThumbnailMediaUnionMember11Data

    metadata: ThumbnailMediaUnionMember11Metadata

    source: Literal["Upload", "ImagePicker"]

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserVideo"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember12DataSourceMedia(BaseModel):
    id: str

    url: Optional[str] = None


class ThumbnailMediaUnionMember12DataResultsImage(BaseModel):
    url: str

    content_type: Optional[str] = None

    file_data: Optional[str] = None

    file_name: Optional[str] = None

    file_size: Optional[float] = None

    height: Optional[float] = None

    width: Optional[float] = None


class ThumbnailMediaUnionMember12DataResultsMaskImage(BaseModel):
    url: str

    content_type: Optional[str] = None

    file_data: Optional[str] = None

    file_name: Optional[str] = None

    file_size: Optional[float] = None

    height: Optional[float] = None

    width: Optional[float] = None


class ThumbnailMediaUnionMember12DataResults(BaseModel):
    image: ThumbnailMediaUnionMember12DataResultsImage

    mask_image: Optional[ThumbnailMediaUnionMember12DataResultsMaskImage] = None


class ThumbnailMediaUnionMember12Data(BaseModel):
    source_media: ThumbnailMediaUnionMember12DataSourceMedia

    results: Optional[ThumbnailMediaUnionMember12DataResults] = None


class ThumbnailMediaUnionMember12Metadata(BaseModel):
    content_type: Optional[str] = None


class ThumbnailMediaUnionMember12(BaseModel):
    id: str

    category: Literal["UserUploaded"]

    data: ThumbnailMediaUnionMember12Data

    metadata: ThumbnailMediaUnionMember12Metadata

    source: Literal["Upload", "ImagePicker"]

    state: Literal["pending", "generating", "error", "completed"]

    type: Literal["UserImageSegmentation"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember13Data(BaseModel):
    source_image: Optional[object] = None


class ThumbnailMediaUnionMember13Metadata(BaseModel):
    content_type: Optional[str] = None


class ThumbnailMediaUnionMember13(BaseModel):
    id: str

    category: Literal["UserUploaded"]

    data: ThumbnailMediaUnionMember13Data

    metadata: ThumbnailMediaUnionMember13Metadata

    source: Literal["Upload", "ImagePicker"]

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserImageFromPicker"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember14DataData(BaseModel):
    height: float

    width: float


class ThumbnailMediaUnionMember14DataResultsImage(BaseModel):
    url: str

    content_type: Optional[str] = None

    file_data: Optional[str] = None

    file_name: Optional[str] = None

    file_size: Optional[float] = None

    height: Optional[float] = None

    width: Optional[float] = None


class ThumbnailMediaUnionMember14DataResultsMaskImage(BaseModel):
    url: str

    content_type: Optional[str] = None

    file_data: Optional[str] = None

    file_name: Optional[str] = None

    file_size: Optional[float] = None

    height: Optional[float] = None

    width: Optional[float] = None


class ThumbnailMediaUnionMember14DataResults(BaseModel):
    image: ThumbnailMediaUnionMember14DataResultsImage

    mask_image: Optional[ThumbnailMediaUnionMember14DataResultsMaskImage] = None


class ThumbnailMediaUnionMember14Data(BaseModel):
    data: Optional[ThumbnailMediaUnionMember14DataData] = None

    path: Optional[str] = None

    results: Optional[ThumbnailMediaUnionMember14DataResults] = None

    url: Optional[str] = None


class ThumbnailMediaUnionMember14Metadata(BaseModel):
    source_media: Optional[object] = None


class ThumbnailMediaUnionMember14(BaseModel):
    id: str

    category: Literal["AIGenerated", "Stock"]

    data: ThumbnailMediaUnionMember14Data

    metadata: ThumbnailMediaUnionMember14Metadata

    source: Literal["GeneratedImage", "Image", "UserImage"]

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["Segmentation"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember15Data(BaseModel):
    id: str

    collection_id: str


class ThumbnailMediaUnionMember15Metadata(BaseModel):
    duration_till_end: Optional[float] = None

    end_time: Optional[float] = None

    mux_playback_id: Optional[str] = None

    start_time: Optional[float] = None


class ThumbnailMediaUnionMember15(BaseModel):
    category: Literal["Gameplay"]

    data: ThumbnailMediaUnionMember15Data

    metadata: ThumbnailMediaUnionMember15Metadata

    source: Optional[Literal["Gameplay"]] = None

    state: Literal["completed"]

    type: Literal["VideoClip"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


class ThumbnailMediaUnionMember16Data(BaseModel):
    id: str


class ThumbnailMediaUnionMember16(BaseModel):
    category: Literal["Ugc"]

    data: ThumbnailMediaUnionMember16Data

    source: Optional[Literal["Ugc"]] = None

    state: Literal["completed"]

    type: Literal["UgcCreator"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None

    metadata: Optional[object] = None


class ThumbnailMediaUnionMember17Data(BaseModel):
    id: str

    created_at: str

    ugc_creator_id: str

    ugc_preset_id: str


class ThumbnailMediaUnionMember17Metadata(BaseModel):
    mux_playback_id: Optional[str] = None

    source_image_url: str


class ThumbnailMediaUnionMember17(BaseModel):
    category: Literal["Ugc"]

    data: ThumbnailMediaUnionMember17Data

    metadata: ThumbnailMediaUnionMember17Metadata

    source: Optional[Literal["Ugc"]] = None

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["UgcVideo"]

    url: Optional[str] = None

    deleted_at: Optional[str] = None

    last_error: Optional[str] = None


ThumbnailMedia: TypeAlias = Union[
    ThumbnailMediaUnionMember0,
    ThumbnailMediaUnionMember1,
    ThumbnailMediaUnionMember2,
    ThumbnailMediaUnionMember3,
    ThumbnailMediaUnionMember4,
    ThumbnailMediaUnionMember5,
    ThumbnailMediaUnionMember6,
    ThumbnailMediaUnionMember7,
    ThumbnailMediaUnionMember8,
    ThumbnailMediaUnionMember9,
    ThumbnailMediaUnionMember10,
    ThumbnailMediaUnionMember11,
    ThumbnailMediaUnionMember12,
    ThumbnailMediaUnionMember13,
    ThumbnailMediaUnionMember14,
    ThumbnailMediaUnionMember15,
    ThumbnailMediaUnionMember16,
    ThumbnailMediaUnionMember17,
    None,
]


class Thumbnail(BaseModel):
    media: Optional[ThumbnailMedia] = None

    text: Optional[str] = None

    theme: Literal["None", "Photo", "TikTokTint", "TikTokGlitch"]

    caption_alignment: Optional[
        Literal[
            "top-left",
            "top-center",
            "top-right",
            "middle-left",
            "middle-center",
            "middle-right",
            "bottom-left",
            "bottom-center",
            "bottom-right",
        ]
    ] = None

    caption_color: Union[Literal["transparent"], List[str], None] = None

    caption_font_family: Optional[str] = None

    caption_font_size: Optional[float] = None

    caption_stroke_color: Optional[str] = None

    caption_text_transform: Optional[Literal["lowercase", "none", "uppercase"]] = None


class TiktokSettings(BaseModel):
    brand_content_toggle: Optional[bool] = None

    brand_organic_toggle: Optional[bool] = None

    consent_to_use: Optional[bool] = None

    disable_comment: Optional[bool] = None

    disable_duet: Optional[bool] = None

    disable_stitch: Optional[bool] = None

    disclose_video_content: Optional[bool] = None

    privacy_level: Optional[
        Literal["PUBLIC_TO_EVERYONE", "FOLLOWER_OF_CREATOR", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"]
    ] = None


class XSettings(BaseModel):
    post_as_a_thread: Optional[bool] = None


class YoutubeSettings(BaseModel):
    privacy_level: Optional[Literal["public", "unlisted", "private"]] = None

    self_declared_made_for_kids: Optional[bool] = None


class Series(BaseModel):
    id: str
    """Unique ID of the series."""

    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    """Aspect ratio of the series videos."""

    connections: List[Connection]
    """Publishing connections for the series."""

    created_at: str
    """Date and time (ISO 8601) when the series was created."""

    image_style: ImageStyle
    """Image style for series."""

    locale: Literal[
        "af-ZA",
        "id-ID",
        "ms-MY",
        "ca-ES",
        "cs-CZ",
        "da-DK",
        "de-DE",
        "en-US",
        "es-ES",
        "es-419",
        "fr-CA",
        "fr-FR",
        "hr-HR",
        "it-IT",
        "hu-HU",
        "nl-NL",
        "no-NO",
        "pl-PL",
        "pt-BR",
        "pt-PT",
        "ro-RO",
        "sk-SK",
        "fi-FI",
        "sv-SE",
        "vi-VN",
        "tr-TR",
        "el-GR",
        "ru-RU",
        "sr-SP",
        "uk-UA",
        "hy-AM",
        "he-IL",
        "ur-PK",
        "ar-SA",
        "hi-IN",
        "th-TH",
        "ko-KR",
        "ja-JP",
        "zh-CN",
        "zh-TW",
    ]
    """Locale of the video series."""

    next_posting_at: Optional[str] = None
    """Date and time (ISO 8601) when the next video will be posted."""

    schedule: Optional[Schedule] = None
    """The publishing schedule for the video series."""

    soundtrack: Soundtrack
    """Soundtrack configuration for the series."""

    soundtrack_behavior: Literal["MutedAfter60s", "FullMusic", "NoMusic"]
    """Behavior of the soundtrack."""

    styles: Optional[Styles] = None
    """Styles for the series videos."""

    type: Literal["SingleVideo", "Series"]
    """Type of the series (e.g., automatically generated)."""

    voice: Voice
    """Voice configuration for the series."""

    content_type: Optional[
        Literal[
            "Custom",
            "News",
            "Quiz",
            "History",
            "Scary",
            "Motivational",
            "Bedtime",
            "FunFacts",
            "LifeTips",
            "ELI5",
            "Philosophy",
        ]
    ] = None
    """Indicates the type of content in this series."""

    custom_watermark: Optional[CustomWatermark] = None
    """Custom watermark for the series (paid plans only)."""

    hashtags: Optional[str] = None
    """List of custom hashtags for the series."""

    name: Optional[str] = None
    """User-friendly name for the series."""

    prompt: Optional[str] = None
    """A custom topic for the series."""

    thumbnail: Optional[Thumbnail] = None
    """Thumbnail for the series."""

    tiktok_settings: Optional[TiktokSettings] = None
    """Settings for the TikTok platform."""

    updated_at: Optional[str] = None
    """Date and time (ISO 8601) when the series was last updated."""

    x_settings: Optional[XSettings] = None
    """Settings for the X/Twitter platform."""

    youtube_settings: Optional[YoutubeSettings] = None
    """Settings for the YouTube platform."""
