"""Loader for the Kvasir-SEG dataset.
This dataset can be found at https://datasets.simula.no/kvasir-seg.

Created on 2021-02-06.

Dataset dictionary structure is as follows:

- Kvasir-SEG : the root folder
- Kvasir-SEG/images : folder with 1000 images
- Kvasir-SEG/masks : folder with 1000 segmentation masks
- Kvasir-SEG/kavsir_bboxes.json : bounding box coordinates as JSON format
"""

import json
from pathlib import Path
from image import Image
from loader.base_json_loader import BaseLoader
from annotation.bounding_box import BoundingBox, BoundingBoxFormat
from annotation.base_annotation import Annotation


class KvasirSegLoader(BaseLoader):
    def __init__(self, root_folder: str):
        """Class to convert Kvasir-SEG dataset into the base format.

        :param root_folder: path to the root folder of the dataset
        """
        self.folder_path = root_folder
        self.images_folder = Path(root_folder, 'images')
        self.masks_folder = Path(root_folder, 'masks')
        self.json_path = Path(root_folder, 'kavsir_bboxes.json')
        with open(file=self.json_path, mode='r') as f:
            self.boxes_json = json.load(f)

    def convert_to_base_format(self) -> list[Image]:
        def load_bounding_boxes(boxes: list) -> list[Annotation]:
            annotations = []
            for box in boxes:
                values = (box['xmin'], box['ymin'], box['xmax'], box['ymax'])
                bbox = BoundingBox(box_values=values, box_format=BoundingBoxFormat.VOC)
                bbox.label = box['label']
                annotations.append(bbox)
            return annotations

        images = []
        for image_name in self.boxes_json:
            image_filename = image_name + '.jpg'
            img_json = self.boxes_json[image_name]
            img = Image(filename=image_filename, width=img_json['width'], height=img_json['height'])
            img.annotations = load_bounding_boxes(img_json['bbox'])
            images.append(img)
        return images


if __name__ == '__main__':
    kvasir_loader = KvasirSegLoader("D:/Users/kevin/Downloads/Kvasir-SEG")
    images = kvasir_loader.convert_to_base_format()
    import writer.base_json_writer as bjs
    # import yaml
    # with open(file='../config_dsv.yaml', mode='r') as config_file:
    #     args = yaml.load(config_file, Loader=yaml.SafeLoader)
    bjs.write(images)
