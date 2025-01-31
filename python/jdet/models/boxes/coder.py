from .box_ops import delta2bbox,bbox2delta,delta2bbox_rotated,bbox2delta_rotated
from jdet.utils.registry import BOXES

@BOXES.register_module()
class DeltaXYWHBBoxCoder:
    """Delta XYWH BBox coder used in MMDet V1.x.

    Following the practice in R-CNN [1]_, this coder encodes bbox (x1, y1, x2,
    y2) into delta (dx, dy, dw, dh) and decodes delta (dx, dy, dw, dh)
    back to original bbox (x1, y1, x2, y2).

    References:
        .. [1] https://arxiv.org/abs/1311.2524

    Args:
        target_means (Sequence[float]): denormalizing means of target for
            delta coordinates
        target_stds (Sequence[float]): denormalizing standard deviation of
            target for delta coordinates
    """

    def __init__(self,
                 target_means=(0., 0., 0., 0.),
                 target_stds=(1., 1., 1., 1.),
                 weights=None):
        self.means = target_means
        self.stds = target_stds
        self.weights = None

    def encode(self, bboxes, gt_bboxes):
        """Get box regression transformation deltas that can be used to
        transform the ``bboxes`` into the ``gt_bboxes``.

        Args:
            bboxes (jt.Var): source boxes, e.g., object proposals.
            gt_bboxes (jt.Var): target of the transformation, e.g.,
                ground-truth boxes.

        Returns:
            jt.Var: Box transformation deltas
        """
        assert bboxes.size(0) == gt_bboxes.size(0)
        assert bboxes.size(-1) == gt_bboxes.size(-1) == 4
        encoded_bboxes = bbox2delta(bboxes, gt_bboxes, self.means,
                                    self.stds,weights=self.weights)
        return encoded_bboxes

    def decode(self,
               bboxes,
               pred_bboxes,
               max_shape=None,
               wh_ratio_clip=16 / 1000):
        """Apply transformation `pred_bboxes` to `boxes`.

        Args:
            boxes (jt.Var): Basic boxes.
            pred_bboxes (jt.Var): Encoded boxes with shape
            max_shape (tuple[int], optional): Maximum shape of boxes.
                Defaults to None.
            wh_ratio_clip (float, optional): The allowed ratio between
                width and height.

        Returns:
            jt.Var: Decoded boxes.
        """
        assert pred_bboxes.size(0) == bboxes.size(0)
        decoded_bboxes = delta2bbox(bboxes, pred_bboxes, self.means,
                                    self.stds, max_shape, wh_ratio_clip,weights=self.weights)

        return decoded_bboxes

@BOXES.register_module()
class DeltaXYWHABBoxCoder:
    """Delta XYWHA BBox coder.

    Following the practice in `R-CNN <https://arxiv.org/abs/1311.2524>`_,
    this coder encodes bbox (x,y,w,h,a) into delta (dx, dy, dw, dh,da) and
    decodes delta (dx, dy, dw, dh,da) back to original bbox (x, y, w, h, a).

    Args:
        target_means (Sequence[float]): Denormalizing means of target for
            delta coordinates
        target_stds (Sequence[float]): Denormalizing standard deviation of
            target for delta coordinates
        clip_border (bool, optional): Whether clip the objects outside the
            border of the image. Defaults to True.
    """

    def __init__(self,
                 target_means=(0., 0., 0., 0., 0.),
                 target_stds=(1., 1., 1., 1., 1.),
                 clip_border=True):
        self.means = target_means
        self.stds = target_stds
        self.clip_border = clip_border

    def encode(self, bboxes, gt_bboxes):
        """Get box regression transformation deltas that can be used to
        transform the ``bboxes`` into the ``gt_bboxes``.

        Args:
            bboxes (jt.Var): Source boxes, e.g., object proposals.
            gt_bboxes (jt.Var): Target of the transformation, e.g.,
                ground-truth boxes.

        Returns:
            jt.Var: Box transformation deltas
        """

        assert bboxes.size(0) == gt_bboxes.size(0)
        assert bboxes.size(-1) == gt_bboxes.size(-1) == 5
        encoded_bboxes = bbox2delta_rotated(bboxes, gt_bboxes, self.means, self.stds)
        return encoded_bboxes

    def decode(self,
               bboxes,
               pred_bboxes,
               max_shape=None,
               wh_ratio_clip=16 / 1000):
        """Apply transformation `pred_bboxes` to `boxes`.

        Args:
            boxes (jt.Var): Basic boxes.
            pred_bboxes (jt.Var): Encoded boxes with shape
            max_shape (tuple[int], optional): Maximum shape of boxes.
                Defaults to None.
            wh_ratio_clip (float, optional): The allowed ratio between
                width and height.

        Returns:
            jt.Var: Decoded boxes.
        """
        assert pred_bboxes.size(0) == bboxes.size(0)
        decoded_bboxes = delta2bbox_rotated(bboxes, pred_bboxes, self.means, self.stds,
                                            max_shape, wh_ratio_clip, self.clip_border)

        return decoded_bboxes