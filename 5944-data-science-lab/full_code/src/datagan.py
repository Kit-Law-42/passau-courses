import os
import random
import re

import cv2
import imageio
import imgaug.augmentables.segmaps as sg
from imgaug import augmenters as iaa

import src.config as config

conf = config.Config()


class DataForGan:

    def __init__(self):
        pass

    @staticmethod
    def data_augmenter() -> iaa.Sequential:
        """
        Create a sequence for data augmentation. This one will be used to apply modification to images randomly
        """
        seq = iaa.Sequential([
            iaa.Affine(rotate=(-90, 90),
                       scale={"x": (0.8, 1.2), "y": (0.5, 1.5)},  # rotate image
                       translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}
                       ),
            iaa.AdditiveGaussianNoise(scale=(0, 40)),  # add gaussian noise
            iaa.Crop(percent=(0, 0.1)),  # crop image
            iaa.AddToHueAndSaturation((-50, 50)),  # change their color
            iaa.LinearContrast((0.75, 1.5)),  # strengthens or weakens the contrast
        ], random_order=True)

        return seq

    def _get_file_map(self) -> dict:
        """
        Create a dict of the form { img_path: mask_path, ... }
        """
        result = {}
        file_extension = "(?<!mask).tif$"
        tmp_list = []

        for folder in os.listdir(conf.KAGGLE_3M_DATASET_DIR):
            folder_path = os.path.join(conf.KAGGLE_3M_DATASET_DIR, folder)

            # Check if the path is a folder
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if re.search(file_extension, file):
                        image_path = os.path.join(folder_path, file)
                        mask_path = image_path.replace("_mask", "")

                        # Check if the file exist
                        if os.path.isfile(mask_path):
                            tmp_list.append((image_path, mask_path))
                        else:
                            print(f"This mask does not exist: {mask_path}")

        # Shuffle the list
        random.shuffle(tmp_list)

        # Split into train, test and validation respecting the proportions specified in the config file
        train_set_index_end = int(len(tmp_list) * conf.TRAIN)
        val_set_index_end = int(len(tmp_list) * conf.VAL) + train_set_index_end + 1

        result = {
            "train": tmp_list[0:train_set_index_end],
            "val": tmp_list[train_set_index_end + 1: val_set_index_end],
            "test": tmp_list[val_set_index_end + 1:]
        }

        return result

    def augmente_data(self) -> None:
        """
        Create augmented mask folder and corresponding MRI image folder.
        This function only works the folder structure of this specific database.
        """
        dataset_splits = self._get_file_map()

        # Check if the training data folders exist or not.
        # If yes start preparing the dataset, if no create these folders

        if not os.path.isdir(conf.GAN_TRAIN_DATASET):
            os.mkdir(conf.GAN_TRAIN_DATASET)

        if not os.path.isdir(conf.GAN_TRAIN_MASK):
            os.mkdir(conf.GAN_TRAIN_MASK)
            os.mkdir(os.path.join(conf.GAN_TRAIN_MASK, "train"))
            os.mkdir(os.path.join(conf.GAN_TRAIN_MASK, "test"))
            os.mkdir(os.path.join(conf.GAN_TRAIN_MASK, "val"))

        if not os.path.isdir(conf.GAN_TRAIN_MRI):
            os.mkdir(conf.GAN_TRAIN_MRI)
            os.mkdir(os.path.join(conf.GAN_TRAIN_MRI, "train"))
            os.mkdir(os.path.join(conf.GAN_TRAIN_MRI, "test"))
            os.mkdir(os.path.join(conf.GAN_TRAIN_MRI, "val"))

        if not os.path.isdir(conf.GAN_COMBINED_DATASET):
            os.mkdir(conf.GAN_COMBINED_DATASET)

        # Create mask put it in folder A and corresponding mri in folder B.
        # Both images need to have the same name
        idx = 1

        # Augmentation sequence
        seq = self.data_augmenter()

        for split, image_mask_tuples in dataset_splits.items():
            for mri_path, mask_path in image_mask_tuples:
                mri = cv2.imread(mri_path)
                mask = cv2.imread(mask_path)
                mask = sg.SegmentationMapsOnImage(mask, shape=mask.shape)

                for _ in range(10):
                    mri_i, mask_i = seq(image=mri, segmentation_maps=mask)

                    # Prepare file path to save the images. make sure that the file name of both images is the same.
                    file_name = str(idx) + conf.IMAGE_EXTENSION
                    mri_i_path = os.path.join(conf.GAN_TRAIN_MRI, split, file_name)
                    mask_i_path = os.path.join(conf.GAN_TRAIN_MASK, split, file_name)

                    # Save the images in the corresponding paths
                    imageio.imwrite(mri_i_path, mri_i)
                    imageio.imwrite(mask_i_path, mask_i.arr)

                    # Advance the index
                    idx += 1

                # log something after each 100 images
                if idx % 1000 == 0:
                    print(f"Created {idx} images")
