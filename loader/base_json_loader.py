import json
from image import Image
from abc import ABC, abstractmethod


def read_json(filepath: str) -> dict:
    with open(file=filepath, mode='r') as f:
        return json.load(f)


class BaseLoader(ABC):
    @abstractmethod
    def convert_to_base_format(self) -> list[Image]:
        """Converts the dataset into the base format and returns a list of images.

        :rtype: list[Image]
        """
        raise NotImplementedError


class BaseJsonLoaderV1(BaseLoader):
    def __init__(self ,filepath: str):
        self.json_root = read_json(filepath)
        self.images = self.convert_to_base_format()

    def convert_to_base_format(self) -> list[Image]:
        images_json = self.json_root['images']
        return [Image(**image) for image in images_json]
