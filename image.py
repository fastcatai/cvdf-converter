from annotation.base_annotation import AnnotationFormat, read_annotations
from abc import ABC, abstractmethod


class BaseImage(ABC):
    def __init__(self, **kwargs):
        self.label = '' if kwargs.get('label') is None else kwargs.get('label')
        self.instance = '' if kwargs.get('instance') is None else kwargs.get('instance')
        self.additional_labels = [] if kwargs.get('additionalLabels') is None else kwargs.get('additionalLabels')
        self.verified = False if kwargs.get('verified') is None else kwargs.get('verified')
        self.auto_created = False if kwargs.get('autoCreated') is None else kwargs.get('autoCreated')

    @abstractmethod
    def to_dict(self, annotation_format: AnnotationFormat = None):
        return {
            'label': self.label,
            "instance": self.instance,
            "additionalLabels": self.additional_labels,
            "verified": self.verified,
            "autoCreated": self.auto_created,
        }


class Image(BaseImage):
    def __init__(self, filename: str = None, width: int = None, height: int = None, **kwargs):
        super().__init__(**kwargs)
        self.filename = kwargs.get('filename') if filename is None else filename
        if self.filename is None:
            raise ValueError('Image filename is required')
        self.width = kwargs.get('width') if width is None else width
        if self.width is None:
            raise ValueError('Image filename is required')
        self.height = kwargs.get('height') if height is None else height
        if self.height is None:
            raise ValueError('Image filename is required')
        self.annotations = read_annotations(kwargs.get('annotations'))
        self.path = kwargs.get('path')

    def __repr__(self):
        return 'Image[{},{},{}]'.format(self.filename, self.width, self.height)

    def to_dict(self, annotation_format: AnnotationFormat = None):
        base_image = super().to_dict()
        annotation_dicts = [annotation.to_std_dict(annotation_format) for annotation in self.annotations]
        return {
            'filename': self.filename,
            'width': self.width,
            'height': self.height,
            'annotations': annotation_dicts,
            **base_image
        }
