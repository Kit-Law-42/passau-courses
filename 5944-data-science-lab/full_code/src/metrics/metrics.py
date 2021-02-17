import torch
from torch import nn

"""
https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch/comments
"""


class IoUScore(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(IoUScore, self).__init__()

    def forward(self, inputs, targets, smooth=1):
        # flatten label and prediction tensors
        inputs = inputs.view(-1)
        targets = targets.view(-1)

        # intersection is equivalent to True Positive count
        # union is the mutually inclusive area of all labels & predictions
        intersection = (inputs * targets).sum()
        total = (inputs + targets).sum()
        union = total - intersection

        IoU = (intersection + smooth) / (union + smooth)

        return IoU


class PixelAccuracy(nn.Module):
    """
    This supposes that the matrix has only 0 and 1 values
    """

    def __init__(self):
        super(PixelAccuracy, self).__init__()

    def forward(self, predicted, target):
        """
        Careful that forward here only considers images that are 4 dim and has only 0 and 1 values
        :param predicted: predicted images
        :param target: target images
        :return:
        """
        if target.shape != predicted.shape:
            print("target has dimension", target.shape, ", predicted values have shape", predicted.shape)
            return

        if target.dim() != 4:
            print("target has dim", target.dim(), ", Must be 4.")
            return

        output = predicted.view(-1, )
        reshaped_target = target.view(-1, ).float()

        tp = torch.sum(output * reshaped_target)  # TP
        fp = torch.sum(output * (1 - reshaped_target))  # FP
        fn = torch.sum((1 - output) * reshaped_target)  # FN
        tn = torch.sum((1 - output) * (1 - reshaped_target))  # TN

        pixel_acc = (tp + tn) / (tp + tn + fp + fn)

        return pixel_acc


class DiceScore(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(DiceScore, self).__init__()

    def forward(self, inputs, targets, smooth=1):
        # flatten label and prediction tensors
        inputs = inputs.view(-1)
        targets = targets.view(-1)

        intersection = (inputs * targets).sum()
        dice = (2. * intersection + smooth) / (inputs.sum() + targets.sum() + smooth)

        return dice
