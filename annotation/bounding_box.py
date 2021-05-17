import sys
from enum import unique
from typing import Tuple
from annotation.base_annotation import Annotation, AnnotationType, AnnotationFormat


@unique
class BoundingBoxFormat(AnnotationFormat):
    """All available coordinate formats for bounding boxes."""
    COCO = 'coco'
    VOC = 'voc'
    CENTER = 'center'
    RELATIVE_COCO = 'relativeCoco'
    RELATIVE_VOC = 'relativeVoc'
    RELATIVE_CENTER = 'relativeCenter'

    def __repr__(self):
        return 'BoundingBoxFormat.' + self.name

    def __str__(self):
        return self.value

    def get_value_names(self) -> list:
        """Gets a list of the value names of the box. It also defines the order that the box value tuple should have.

        :return: list of box value names
        """
        if self is BoundingBoxFormat.COCO:
            return ['x', 'y', 'width', 'height']
        elif self is BoundingBoxFormat.VOC:
            return ['xMin', 'yMin', 'xMax', 'yMax']
        elif self is BoundingBoxFormat.CENTER:
            return ['xCenter', 'yCenter', 'width', 'height']
        elif self is BoundingBoxFormat.RELATIVE_COCO:
            return ['relX', 'relY', 'relWidth', 'relHeight']
        elif self is BoundingBoxFormat.RELATIVE_VOC:
            return ['relXMin', 'relYMin', 'relXMax', 'relYMax']
        elif self is BoundingBoxFormat.RELATIVE_CENTER:
            return ['relXCenter', 'relYCenter', 'relWidth', 'relHeight']
        else:
            raise ValueError("Format '{}' is not supported".format(self.value))


class BoundingBox(Annotation):
    def __init__(self, box_values: tuple = None, box_format: BoundingBoxFormat = None, **kwargs):
        super().__init__(**kwargs)

        if box_values is not None and len(box_values) != 4:
            raise ValueError('There only must be four box values')

        try:
            self.format = BoundingBoxFormat(kwargs.get('format')) if box_format is None else box_format
        except ValueError as e:
            print(str(e), file=sys.stderr)
            raise

        # get box values from dict if param is None
        if box_values is None:
            box_values = dict_to_box_values(self.format, **kwargs)
            if box_values is None:
                raise ValueError('There are no box values defined')
        # transform every format into coco format
        self.box_values = transform_to_coco(box=box_values, box_format=self.format)

        self.type = AnnotationType.BOUNDING_BOX.value

    def __repr__(self):
        n1, n2, n3, n4 = self.format.get_value_names()
        v1, v2, v3, v4 = self.box_values
        return 'BoundingBox[{},{}:{},{}:{},{}:{},{}:{}]'.format(self.format.value, n1, v1, n2, v2, n3, v3, n4, v4)

    def to_std_dict(self, annotation_format: BoundingBoxFormat = None) -> dict:
        if annotation_format is None:
            annotation_format = self.format
        base_annotation = super().to_std_dict()
        transformed_box_values = transform_from_coco(box=self.box_values, box_format=annotation_format)
        box_values_dict = box_values_to_dict(box=transformed_box_values, box_format=annotation_format)
        return {
            **base_annotation,
            'type': self.type,
            'format': str(annotation_format),
            **box_values_dict
        }


def box_values_to_dict(box: tuple, box_format: BoundingBoxFormat):
    """Converts the box values to a dict.

    :param box: a tuple with the box values in the right order as defined in box formate
    :param box_format: the format of the box values
    :return: a dict of the box values with the format-appropriate keys
    """
    value_names = box_format.get_value_names()
    return dict(zip(value_names, box))  # combines value names and values


def dict_to_box_values(box_format: BoundingBoxFormat, **kwargs) -> tuple:
    """Convert dict values into a tuple of box values.

    :param box_format: format of the box values that are in kwargs
    :param kwargs: dict that has all four box values with the format-appropriate keys
    :return: a tuple of box values with the format-defined order
    """
    keys = box_format.get_value_names()  # get box value keys for dict
    box_values = tuple(kwargs.get(key) for key in keys)  # store box values from dict into a tuple
    return box_values if all([x is not None for x in box_values]) else None  # return tuple if no item is None


def transform_from_coco(box: tuple, box_format: AnnotationFormat, img_wh: Tuple[int, int] = None) -> tuple:
    """Does a transformation from the coco format to any other supported format."""
    if box is None or box_format is None:
        raise ValueError('Box value and format must be present')
    if len(box) != 4:
        raise ValueError('There only must be four box values')

    if box_format is (BoundingBoxFormat.RELATIVE_COCO or BoundingBoxFormat.RELATIVE_VOC
                      or BoundingBoxFormat.RELATIVE_CENTER):
        if img_wh is None or len(img_wh) != 2:
            raise ValueError('Image width and height must be defined if a relative transformation is desired')

    if box_format is BoundingBoxFormat.COCO:
        return box
    elif box_format is BoundingBoxFormat.VOC:
        return coco_to_voc(box)
    elif box_format is BoundingBoxFormat.CENTER:
        return coco_to_center(box)
    elif box_format is BoundingBoxFormat.RELATIVE_COCO:
        return coco_to_relative_coco(box, img_wh[0], img_wh[1])
    elif box_format is BoundingBoxFormat.RELATIVE_VOC:
        return coco_to_relative_voc(box, img_wh[0], img_wh[1])
    elif box_format is BoundingBoxFormat.RELATIVE_CENTER:
        return coco_to_relative_center(box, img_wh[0], img_wh[1])
    else:
        raise ValueError("Box format of type '{}' is not supported".format(box_format.value))


def transform_to_coco(box: tuple, box_format: AnnotationFormat,
                      img_width: int = None, img_height: int = None) -> tuple:
    if box is None or box_format is None:
        raise ValueError('Box value and format must be present')
    if len(box) != 4:
        raise ValueError('There only must be four box values')
    if box_format is (BoundingBoxFormat.RELATIVE_COCO
                      or BoundingBoxFormat.RELATIVE_VOC
                      or BoundingBoxFormat.RELATIVE_CENTER):
        if img_width or img_height is None:
            raise ValueError('Image width and height must be defined if a relative transformation is desired')

    if box_format is BoundingBoxFormat.COCO:
        return box
    elif box_format is BoundingBoxFormat.VOC:
        return voc_to_coco(box)
    elif box_format is BoundingBoxFormat.CENTER:
        return center_to_coco(box)
    elif box_format is BoundingBoxFormat.RELATIVE_COCO:
        return relative_coco_to_coco(box, img_width, img_height)
    elif box_format is BoundingBoxFormat.RELATIVE_VOC:
        return relative_voc_to_coco(box, img_width, img_height)
    elif box_format is BoundingBoxFormat.RELATIVE_CENTER:
        return relative_center_to_coco(box, img_width, img_height)
    else:
        raise ValueError("Box format of type '{}' is not supported".format(box_format.value))


def voc_to_coco(box: tuple) -> tuple:
    if len(box) != 4:
        raise ValueError('There only must be four box values')
    x_min, y_min, x_max, y_max = box
    return x_min, y_min, x_max - x_min, y_max - y_min


def coco_to_voc(box: tuple) -> tuple:
    if len(box) != 4:
        raise ValueError('There only must be four box values')
    x, y, width, height = box
    return x, y, x + width, y + height


def center_to_coco(box: tuple) -> tuple:
    x_center, y_center, width, height = box
    x, y = x_center - (width / 2), y_center - (height / 2)
    return x, y, width, height


def coco_to_center(box: tuple) -> tuple:
    x, y, width, height = box
    x_center, y_center = x + (width / 2), y + (height / 2)
    return x_center, y_center, width, height


def relative_coco_to_coco(box: tuple, img_width: int, img_height: int) -> tuple:
    rel_x, rel_y, rel_width, rel_height = box
    return rel_x * img_width, rel_y * img_height, rel_width * img_width, rel_height * img_height


def coco_to_relative_coco(box: tuple, img_width: int, img_height: int) -> tuple:
    x, y, width, height = box
    return x / img_width, y / img_height, width / img_width, height / img_height


def relative_voc_to_coco(box: tuple, img_width: int, img_height: int) -> tuple:
    rel_x_min, rel_y_min, rel_x_max, rel_y_max = box
    x_min, y_min = rel_x_min * img_width, rel_y_min * img_height
    x_max, y_max = rel_x_max * img_width, rel_y_max * img_height
    return voc_to_coco((x_min, y_min, x_max, y_max))


def coco_to_relative_voc(box: tuple, img_width: int, img_height: int) -> tuple:
    x_min, y_min, x_max, y_max = coco_to_voc(box)
    return x_min / img_width, y_min / img_height, x_max / img_width, y_max / img_height


def relative_center_to_coco(box: tuple, img_width: int, img_height: int) -> tuple:
    rel_x_center, rel_y_center, rel_width, rel_height = box
    x_center, y_center = rel_x_center * img_width, rel_y_center * img_height
    width, height = rel_width * img_width, rel_height * img_height
    return center_to_coco((x_center, y_center, width, height))


def coco_to_relative_center(box: tuple, img_width: int, img_height: int) -> tuple:
    x_center, y_center, width, height = coco_to_center(box)
    return x_center / img_width, y_center / img_height, width / img_width, height / img_height


if __name__ == '__main__':
    transform_from_coco((1, 2, 3, 4), BoundingBoxFormat.RELATIVE_VOC)
