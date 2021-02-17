import torchvision
from torch import nn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


class MaskRCNN(nn.Module):
    def __init__(self):
        super(MaskRCNN, self).__init__()
        # All the layers are trainable
        self.mask_rcnn = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True,
                                                                            trainable_backbone_layers=5)
        # replace the classifier with a new one, that has
        # num_classes which is user-defined
        num_classes = 2  # 1 class (cancer) + background

        # get number of input features for the classifier
        in_features = self.mask_rcnn.roi_heads.box_predictor.cls_score.in_features

        # replace the pre-trained head with a new one
        self.mask_rcnn.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    def forward(self, data, target=None):
        if target is not None:
            return self.mask_rcnn(data, target)
        else:
            return self.mask_rcnn(data)
