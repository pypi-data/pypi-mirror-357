import os

from pydantic import Field, IPvAnyAddress
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, SettingsConfigDict


class GalleryConfig(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)

    GALLERY_HOST: IPvAnyAddress = Field(default='127.0.0.1')
    GALLERY_PORT: int = Field(default=8080, gt=0)
    GALLERY_DIRECTORY: str = Field(default_factory=os.getcwd)
    GALLERY_IMAGE_DATE_FORMAT: str = '%m/%d/%Y %I:%M %p'
    GALLERY_IMAGE_DATE_TIMEZONE: TimeZoneName = Field(default='UTC', description='Timezone for image dates')
    GALLERY_BRAND_NAME: str = 'SimpleImageGallery'
    GALLERY_HEADER: str = 'my gallery'
    GALLERY_SLIDESHOW_MIN_BATCH_SIZE: int = Field(default=5, gt=0)
