import json
import os
import unittest

import src.utils as util
from src import config
from src.data_loaders import dataset
from src.datagan import DataForGan
from src.random_shapes import generate


class MyTestCase(unittest.TestCase):
    def test_generate(self):
        path = 'generate_test'
        number_of_masks_to_generate = 5
        os.mkdir(path)
        generate(number_of_masks_to_generate=number_of_masks_to_generate, path=path)
        self.assertEqual(len(os.listdir(path)), number_of_masks_to_generate)

    def test_group_data(self):
        conf = config.Config()
        util.group_data()
        self.assertGreater(len(os.listdir(conf.REAL_TRAIN_MRI)), 0)
        self.assertGreater(len(os.listdir(conf.REAL_TRAIN_MASK)), 0)

    def test_generate_boxes(self):
        conf = config.Config()
        util.generate_boxes()
        file = open(conf.FILE_PATH, 'r')
        mask_dict = dict(json.loads(file.read()))
        self.assertEqual(len(mask_dict.keys()), 2)

    def test_dataset(self):
        unet_data = dataset.CustomDataset(mask_rcnn=False)
        mask_rcnn_data = dataset.CustomDataset(mask_rcnn=True)
        self.assertEqual(len(unet_data), len(mask_rcnn_data))
        self.assertEqual(len(unet_data), 3929 + 33000)

    def test_dataloader(self):
        yes = True

    def test_data_augment(self):
        datagan = DataForGan()
        datagan.augmente_data()


if __name__ == '__main__':
    unittest.main()
