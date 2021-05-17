import sys
from enum import Enum, unique
from abc import ABC, abstractmethod
from typing import Optional


@unique
class AnnotationType(Enum):
    BOUNDING_BOX = 'boundingBox'
    POLYGON = 'polygon'


@unique
class AnnotationFormat(Enum):
    pass


class Annotation(ABC):
    def __init__(self, **kwargs):
        self.label = '' if kwargs.get('label') is None else kwargs.get('label')
        self.instance = '' if kwargs.get('instance') is None else kwargs.get('instance')
        self.additional_labels = [] if kwargs.get('additionalLabels') is None else kwargs.get('additionalLabels')
        self.verified = False if kwargs.get('verified') is None else kwargs.get('verified')
        self.auto_created = False if kwargs.get('autoCreated') is None else kwargs.get('autoCreated')

    @abstractmethod
    def to_std_dict(self, annotation_format: AnnotationFormat = None) -> dict:
        return {
            'label': self.label,
            "instance": self.instance,
            "additionalLabels": self.additional_labels,
            "verified": self.verified,
            "autoCreated": self.auto_created,
        }


def read_annotations(annotations: list[dict]) -> list[Annotation]:
    if annotations is None:
        return []
    annotation_list = []
    for annotation in annotations:
        a = read_annotation(annotation)
        if a is not None:
            annotation_list.append(a)
    return annotation_list


def read_annotation(annotation: dict) -> Optional[Annotation]:
    annotation_type = annotation['type']
    if annotation_type is not None:  # annotation must have a type
        # compare annotation types an create appropriate object
        if annotation_type == AnnotationType.BOUNDING_BOX.value:
            from annotation.bounding_box import BoundingBox
            return BoundingBox(**annotation)
        else:
            print("Annotation was skipped because type '{}' is not supported", file=sys.stderr)
    else:
        print('Annotation was skipped because it has no type', file=sys.stderr)
    return None
