import argparse
from pathlib import Path
from typing import Union
from image import Image
from annotation.bounding_box import BoundingBox, BoundingBoxFormat
from writer.base_json_writer import write

import yaml


def try_convert_to_number(value: str) -> Union[int, float, str]:
    """Converts string to float or int if possible, otherwise return same value"""
    if value.isnumeric():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def read_line(line: str, **kwargs):
    """Reads the line with annotations an returns all values separately."""
    value_delimiter = kwargs.get('delimiter')
    annotation_per_line = kwargs.get('annotationPerLine')
    annotation_delimiter = kwargs.get('annotationDelimiter')
    with_path = kwargs.get('withPath')
    path_at_end = kwargs.get('pathAtEnd')
    class_at_end = kwargs.get('classAtEnd')
    class_map = kwargs.get('classMapping')

    line_values = []

    if annotation_per_line:
        # only split path from value if path is within line
        annotations = line.split(value_delimiter, 1 if with_path else 0)
    else:
        # split into individual annotations
        annotations = line.split(annotation_delimiter)

    if with_path:
        # delete path from annotations
        path = annotations.pop(len(annotations) - 1 if path_at_end else 0)
        line_values.append(path)

    for annotation in annotations:
        annotation_values = [try_convert_to_number(v) for v in annotation.strip('\r\n').split(value_delimiter)]
        # write label if it is defined in map
        class_idx = len(annotation_values) - 1 if class_at_end else 0
        label_number = annotation_values[class_idx]
        if class_map is not None and label_number in class_map:
            annotation_values[class_idx] = class_map[label_number]
        # add annotation to line
        line_values.append(tuple(annotation_values))

    return line_values


def load_images(path: Path, **kwargs) -> dict[str, list[tuple]]:
    file_per_image = bool(kwargs.get('filePerImage'))
    with_path = kwargs.get('withPath')
    image_extension = '.' + kwargs.get('imageExtension') if kwargs.get('imageExtension') is not None else ''

    def read_file(annotation_file: Path, images: dict) -> None:
        with annotation_file.open(mode='r') as f:
            for line in f:  # read line by line
                line_values = read_line(line, **kwargs)
                image_path = line_values.pop(0) if with_path else annotation_file.name.split('.')[0] + image_extension
                # check if image is in dict
                annotation_values = images[image_path] if image_path in images else []
                annotation_values = annotation_values + line_values  # merge lists
                images[image_path] = annotation_values  # add extended list dict
        return

    def file_per_image_true():
        images = {}
        for image_file in path.iterdir():
            if not image_file.is_file():
                continue
            read_file(annotation_file=image_file, images=images)
        # delete empty entries
        images = dict(filter(lambda e: len(e[1]) > 0, images.items()))
        return images

    def file_per_image_false():
        images = {}
        if not path.is_file():
            return images
        read_file(annotation_file=path, images=images)
        # delete empty entries
        images = dict(filter(lambda e: len(e[1]) > 0, images.items()))
        return images

    if file_per_image:
        return file_per_image_true()
    else:
        return file_per_image_false()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delimiter Separated Values Loader')
    parser.add_argument('path', type=Path,
                        help='Path to file or folder, depended on config')
    parser.add_argument('--config', type=Path, metavar='{CONFIG-PATH, yolo}',
                        help='path to config file or a pre-defined config')

    args = parser.parse_args()

    # Load default configs
    with open(file='configs/config_dsv_default.yaml', mode='r') as file:
        default_config = yaml.load(file, Loader=yaml.FullLoader)

    if args.config is not None:
        # user-specific config YAML file
        yaml_file = '../configs/config_dsv_yolo.yaml' if args.config == 'yolo' else args.config
        # Load YAML file
        with open(file=yaml_file, mode='r') as file:
            config_params = yaml.load(file, Loader=yaml.SafeLoader)
        # Merge default config with user config
        config_params = {**default_config, **config_params}

    # otherwise only take default config
    else:
        config_params = default_config

    images = load_images(args.path, **config_params)

    class_at_end = config_params.get('classAtEnd')
    box_format = config_params.get('boundingBox')
    image_width = config_params.get('imageWidth')
    image_height = config_params.get('imageHeight')
    keys = list(images.keys())
    keys.sort(key=lambda x: int(x.split('.')[0]))
    image_objects = []
    for k in keys:
        img = Image(filename=k, width=image_width, height=image_height)
        annotations = []
        for annotation in images[k]:
            label = annotation[4] if class_at_end else annotation[0]
            box_values = annotation[0:4] if class_at_end else annotation[1:5]
            a = BoundingBox(box_values=box_values, box_format=BoundingBoxFormat(box_format))
            a.label = label
            annotations.append(a)
        img.annotations = annotations
        image_objects.append(img)

    write(images=image_objects, annotation_format=BoundingBoxFormat.COCO, **config_params)





