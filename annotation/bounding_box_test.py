from unittest import TestCase
from annotation.bounding_box import BoundingBoxFormat, transform_from_coco


class TestBoundingBox(TestCase):

    def test_transform_from_coco(self):
        # TODO: test random values

        # test some concrete values
        coco_box = [(128, 216, 201, 35)]
        # one list element are the results for coco, voc and center
        results = [[(128, 216, 201, 35), (128, 216, 329, 251), (228.5, 233.5, 201, 35)]]
        # different images dimensions
        img_wh = [(960, 540)]

        for idx, box in enumerate(coco_box):
            res_coco, res_voc, res_center = results[idx]
            same_coco_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.COCO)
            self.assertEqual(same_coco_box, res_coco)
            voc_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.VOC)
            self.assertEqual(voc_box, res_voc)
            center_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.CENTER)
            self.assertEqual(center_box, res_center)
            wh = img_wh[idx]
            rel_coco_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.RELATIVE_COCO, img_wh=wh)
            self.assertEqual(rel_coco_box, ((same_coco_box[0] / wh[0]), (same_coco_box[1] / wh[1]),
                                            (same_coco_box[2] / wh[0]), (same_coco_box[3] / wh[1])))
            rel_voc_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.RELATIVE_VOC, img_wh=img_wh[idx])
            self.assertEqual(rel_voc_box, ((voc_box[0] / wh[0]), (voc_box[1] / wh[1]),
                                           (voc_box[2] / wh[0]), (voc_box[3] / wh[1])))
            rel_center_box = transform_from_coco(box=box, box_format=BoundingBoxFormat.RELATIVE_CENTER, img_wh=img_wh[idx])
            self.assertEqual(rel_center_box, ((center_box[0] / wh[0]), (center_box[1] / wh[1]),
                                              (center_box[2] / wh[0]), (center_box[3] / wh[1])))

