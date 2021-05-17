"""Writes delimiter separated annotation values into files.

- delimiter: separation character between annotation values
- lineTerminator: separation between lines or annotations if 'annotationPerLine' is true
- ignoreEmptyClass: no space is occupied of this is set to true
- defaultClass: placed if class is empty and 'ignoreEmptyClass' was set to false
- classAtEnd: defines if the class is placed at the beginning or before the annotation values
- quoting: defines if values should be quoted if there are spaces or delimiters within the string
- quoteChar: character used to quote fields containing spaces or delimiters
- withPath: if images path should be inserted to the annotation
- pathAtEnd: defines if the path is placed in front or at the beginning of the annotation values
- defaultPath: default path to the image if no path is defined
- annotationPerLine: if annotations of an image are saved in a single line
- annotationDelimiter: character between annotations
- filePerImage: if image annotations are saved in separate file
- outputFolder: folder in which the files are saved if 'filePerImage' is true
- fileExtension: file extensions of the saved files if 'filePerImage' is true
- outputFile: file path for all images if 'filePerImage' is false
- boundingBox: output annotation format for bounding boxes
"""
from typing import Tuple

import yaml

from annotation.base_annotation import Annotation, AnnotationType
from annotation.bounding_box import BoundingBox, BoundingBoxFormat, transform_from_coco
from image import Image


def quote_if_necessary(value: str, **kwargs) -> str:
    quoting = kwargs.get('quoting')
    if not quoting:
        return value
    quote_char = kwargs.get('quoteChar')
    delimiter = kwargs.get('delimiter')
    line_terminator = kwargs.get('lineTerminator')
    annotation_delimiter = kwargs.get('annotationDelimiter')
    value = value.strip()
    if ' ' in value or delimiter in value or line_terminator in value or annotation_delimiter in value:
        value = quote_char + value + quote_char
    return value


def bounding_box_sv(annotation: BoundingBox, annotation_format: BoundingBoxFormat, img_wh: Tuple[int, int] = None,
                    class_mapping: dict = None, **kwargs) -> tuple:
    if img_wh is None or len(img_wh) != 2:
        raise ValueError('No valid image dimension defined')

    line = list(transform_from_coco(box=annotation.box_values, box_format=annotation_format, img_wh=img_wh))
    # config: empty class
    ignore_empty_class = kwargs.get('ignoreEmptyClass')
    default_class = kwargs.get('defaultClass')
    is_box_class_empty = annotation.label is None or annotation.label.strip() == ''
    if is_box_class_empty:
        box_class = None if ignore_empty_class else default_class
    else:
        box_class = annotation.label.strip()
    # apply class mapping
    class_map = kwargs.get('classMapping', class_mapping)
    if class_map is not None and box_class is not None and box_class in class_map:
        box_class = str(class_map[box_class])
    # config: class position if class exists
    if box_class is not None:
        class_at_end = kwargs.get('classAtEnd')
        box_class = quote_if_necessary(box_class)
        line.append(box_class) if class_at_end else line.insert(0, box_class)
    return tuple(line)


def annotation_sv(annotation: Annotation, img_wh: Tuple[int, int] = None, class_mapping: dict = None, **kwargs) -> tuple:
    if annotation is None:
        raise ValueError('Annotation must not be None')
    if img_wh is None or len(img_wh) != 2:
        raise ValueError('No valid image dimension defined')

    if isinstance(annotation, BoundingBox):
        box_output_format = kwargs.get(AnnotationType.BOUNDING_BOX.value)
        box_format = BoundingBoxFormat(box_output_format)
        return bounding_box_sv(annotation=annotation, annotation_format=box_format, img_wh=img_wh, class_mapping=class_mapping, **kwargs)
    else:
        raise ValueError('Annotation of type {} is not supported'.format(annotation))


def image_sv(image: Image, path: str = None, class_mapping: dict = None, **kwargs) -> list[list[tuple]]:
    if image is None:
        raise ValueError('Image must not be None')

    annotation_per_line = kwargs.get('annotationPerLine')
    with_path = kwargs.get('withPath')
    path_at_end = kwargs.get('pathAtEnd')

    # config: path + image name
    folder_path = image.path if path is None else path
    if folder_path is not None:
        if folder_path != '' and not folder_path.endswith('/'):
            folder_path += '/'
        image_path = folder_path + image.filename
        image_path = quote_if_necessary(image_path)
    else:
        image_path = None

    sv_annotations = []
    for annotation in image.annotations:
        # get annotation values as tuple
        annotation_values = annotation_sv(annotation, (image.width, image.height), class_mapping, **kwargs)
        # add path when with_path and annotation_per_line is true
        if with_path and image_path is not None and annotation_per_line:
            annotation_values = annotation_values + tuple([image_path]) if path_at_end \
                else tuple([image_path]) + annotation_values
        # pack every annotation into a 'line' (=list)
        if annotation_per_line:
            annotation_values = [annotation_values]
        # append to image annotation list
        sv_annotations.append(annotation_values)

    # add image path to line if annotation should be in the same line
    if not annotation_per_line and with_path and image_path is not None:
        image_path = tuple([image_path])
        sv_annotations.append(image_path) if path_at_end else sv_annotations.insert(0, image_path)
    # pack every annotation into a 'line' (=list) if annotation should be in the same line
    if not annotation_per_line:
        sv_annotations = [sv_annotations]
    return sv_annotations


def dsv_image_str(image_lines: list[list[tuple]], **kwargs) -> str:
    delimiter = kwargs.get('delimiter')
    annotation_delimiter = kwargs.get('annotationDelimiter')
    line_terminator = kwargs.get('lineTerminator')
    lines = []
    for line in image_lines:
        blocks = [delimiter.join(map(str, block)) for block in line]
        lines.append(annotation_delimiter.join(blocks))
    return line_terminator.join(lines)


def dsv_writer(images: list[Image], path: str = None, class_mapping: dict = None, **kwargs):
    file_per_image = kwargs.get('filePerImage')
    output_folder = kwargs.get('outputFolder')

    # output folder for separate image annotation files
    if file_per_image:
        output_folder += '/' if not output_folder.endswith('/') else ''
        from pathlib import Path  # create folder path if not existent
        Path(output_folder).mkdir(parents=True, exist_ok=True)

    annotation_file_lines = []
    for image in images:
        image_annotations_list = image_sv(image, path, class_mapping, **kwargs)
        image_annotations = dsv_image_str(image_annotations_list, **kwargs)
        # write annotation file for every image
        if file_per_image:
            # image annotation file name
            file_extension = kwargs.get('fileExtension')
            image_annotation_filename = image.filename[:image.filename.rindex('.')] + '.' + file_extension
            # write file
            image_annotation_file_path = output_folder + image_annotation_filename
            with open(file=image_annotation_file_path, mode='wb') as file:
                file.write(bytes(image_annotations, 'UTF-8'))
        else:
            # append to list if all images should be in one file
            annotation_file_lines.append(image_annotations)

    # write annotation file if all images should be in one file
    if not file_per_image:
        line_terminator = kwargs.get('lineTerminator')
        output_file = kwargs.get('outputFile')
        with open(output_file, mode='wb') as file:
            file.write(bytes(line_terminator.join(annotation_file_lines), 'UTF-8'))

    return


# TODO: Make Base Json writer and remove dict in each class
# TODO: class mapping inside yaml config or load separately
if __name__ == '__main__':

    with open(file='../config_dsv.yaml', mode='r') as config_file:
        args = yaml.load(config_file, Loader=yaml.SafeLoader)


    # updated_args = default_config.copy()
    # updated_args.update(args)

    # csv_string = annotation_sv(annotation=BoundingBox((1, 2, 3, 4), BoundingBoxFormat.COCO), **args)

    img = Image(filename='1001.png', width=512, height=256)
    bb1 = BoundingBox((12, 256, 34, 454), BoundingBoxFormat.COCO)
    bb1.label = 'Polyp1'
    img.annotations = [bb1,
                       BoundingBox((9, 10, 21, 47), BoundingBoxFormat.COCO),
                       BoundingBox((45, 6, 3, 4), BoundingBoxFormat.COCO)]

    img1 = Image(filename='1020.png', width=512, height=256)
    bb1 = BoundingBox((142, 123, 5, 78), BoundingBoxFormat.COCO)
    bb1.label = 'Polyp 2'
    img1.annotations = [bb1,
                       BoundingBox((75, 444, 666, 77), BoundingBoxFormat.COCO),
                       BoundingBox((66, 2, 3, 8), BoundingBoxFormat.COCO)]

    # csv_string = image_sv(image=img, path='/to/', **args)
    # print(csv_string)
    # print(dsv_image_writer(csv_string, **args))
    dsv_writer(images=[img, img1], path='', **args)
