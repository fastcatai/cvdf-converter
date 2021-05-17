import yaml
from image import Image
from annotation.base_annotation import Annotation, AnnotationType
from annotation.bounding_box import BoundingBox, BoundingBoxFormat, transform_from_coco, box_values_to_dict
from pathlib import Path


# with open(file=Path(__file__).parent.joinpath('config_default_base_json.yaml'), mode='r') as file:
#     default_config = yaml.load(file, Loader=yaml.FullLoader)


def write_bounding_box(bounding_box: BoundingBox, annotation_format: BoundingBoxFormat) -> dict:
    if annotation_format is None:
        raise ValueError('Bounding box format is not defined')
    transformed_box_values = transform_from_coco(box=bounding_box.box_values, box_format=annotation_format)
    box_values_dict = box_values_to_dict(box=transformed_box_values, box_format=annotation_format)
    json_annotation = {
        'label': bounding_box.label,
        "instance": bounding_box.instance,
        "additionalLabels": bounding_box.additional_labels,
        "verified": bounding_box.verified,
        "autoCreated": bounding_box.auto_created,
        'type': bounding_box.type,
        'format': str(annotation_format),
        **box_values_dict
    }
    return json_annotation


def write_annotation(annotation: Annotation, **kwargs) -> dict:
    if isinstance(annotation, BoundingBox):
        box_output_format = kwargs.get(AnnotationType.BOUNDING_BOX.value)
        return write_bounding_box(annotation, BoundingBoxFormat(box_output_format))
    else:
        raise ValueError('Annotation {} is not supported'.format(annotation))


def write(images: list[Image], **kwargs):
    """Main function to write a JSON with the base format.

    :param images: list of image objects
    :param annotation_format: desired annotation format
    """
    json_images = []
    for image in images:
        json_annotations = []
        for annotation in image.annotations:
            json_annotation = write_annotation(annotation, **kwargs)
            json_annotations.append(json_annotation)
        json_image = {
            'filename': image.filename,
            'label': image.label,
            "instance": image.instance,
            "additionalLabels": image.additional_labels,
            "verified": image.verified,
            "autoCreated": image.auto_created,
            'width': image.width,
            'height': image.height,
            'annotations': json_annotations,
        }
        json_images.append(json_image)

    json_dict = {'images': json_images}

    import json
    from pathlib import Path  # create folder path if not existent
    output_file = kwargs.get('outputFile')
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(file=output_file, mode='w') as file:
        json.dump(obj=json_dict, fp=file, indent=2)


if __name__ == '__main__':
    img = Image(filename='1001.png', width=512, height=256)
    bb1 = BoundingBox((12, 256, 34, 454), BoundingBoxFormat.COCO)
    bb1.label = 'Polyp1'
    img.annotations = [bb1,
                       BoundingBox((9, 10, 21, 47), BoundingBoxFormat.COCO),
                       BoundingBox((45, 6, 3, 4), BoundingBoxFormat.COCO)]

    img1 = Image(filename='1020.png', width=512, height=256)
    bb1 = BoundingBox((142, 123, 5, 78), BoundingBoxFormat.COCO)
    bb1.label = 'Polyp2'
    img1.annotations = [bb1,
                        BoundingBox((75, 444, 666, 77), BoundingBoxFormat.COCO),
                        BoundingBox((66, 2, 3, 8), BoundingBoxFormat.COCO)]

    write(images=[img, img1], annotation_format=BoundingBoxFormat.VOC)
