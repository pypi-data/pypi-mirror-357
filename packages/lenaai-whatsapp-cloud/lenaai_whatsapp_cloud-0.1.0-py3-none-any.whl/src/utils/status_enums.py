from enum import Enum


class VideoSendStatus(Enum):
    SUCCESS = "success"
    FAILED_TO_CONVERT = "failed_to_convert"
    FAILED_TO_SEND = "failed_to_send"

class MessageSendStatus(Enum):
    SUCCESS = "success"
    FAILED_TO_SEND = "failed_to_send"

class ImageSendStatus(Enum):
    SUCCESS = "success"
    FAILED_TO_SEND = "failed_to_send"
    INVALID_FORMAT = "invalid_format"