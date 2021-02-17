import json

import src.config as config
import cv2
import os
import shutil
import numpy as np


def generate_boxes():
    """
    Generate boxes coordinates for each mask
    :return:
    """
    # First generate masks for the generated shapes
    conf = config.Config()
    mask_dict = {
        'real_data': {
            'data_path': conf.REAL_TRAIN_MASK,
            'mask_boxes_and_classes': []
        },
        'gan_generated_data': {
            'data_path': conf.GAN_GENERATED_MASKS,
            'mask_boxes_and_classes': []
        }
    }

    # Get the gan mask dict and real data mask dict
    for key, value in mask_dict.items():
        for image_name in os.listdir(value['data_path']):
            if not os.path.isfile(os.path.join(value['data_path'], image_name)):
                continue
            try:
                image_path = os.path.join(value['data_path'], image_name)
                img = cv2.imread(image_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                thresh = 100
                ret, thresh_img = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
                contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                bounding_rec = []
                if len(contours) != 0:
                    x, y, w, h = cv2.boundingRect(contours[0])
                    bounding_rec = [x, y, x + w, y + h]

                value['mask_boxes_and_classes'].append({
                    'name': image_name,
                    'box': bounding_rec,
                    'class': 'cancer'
                })

            except Exception as e:
                print(f'Error processing {image_name}')
                raise

    file = open(conf.FILE_PATH, 'w')
    file.write(json.dumps(mask_dict))


def group_data():
    """
    Move real masks and real mri to corresponding directories
    :return:
    """
    conf = config.Config()
    if not os.path.isdir(conf.REAL_DATA_DIR):
        os.mkdir(conf.REAL_DATA_DIR)

    if not os.path.isdir(conf.REAL_TRAIN_MRI):
        os.mkdir(conf.REAL_TRAIN_MRI)

    if not os.path.isdir(conf.REAL_TRAIN_MASK):
        os.mkdir(conf.REAL_TRAIN_MASK)

    idx = 0
    for patient_folder in os.listdir(conf.KAGGLE_3M_DATASET_DIR):
        dir_path = os.path.join(conf.KAGGLE_3M_DATASET_DIR, patient_folder)
        if os.path.isdir(dir_path):
            for image in os.listdir(dir_path):
                # Get a mask
                if image.find("_mask") != -1:
                    # Copy real mask
                    current_mask_path = os.path.join(dir_path, image)
                    target_mask_path = os.path.join(conf.REAL_TRAIN_MASK, str(idx) + ".png")
                    shutil.copyfile(current_mask_path, target_mask_path)

                    # Copy image
                    current_image_path = os.path.join(conf.KAGGLE_3M_DATASET_DIR, patient_folder,
                                                      image.replace("_mask", ""))
                    target_image_path = os.path.join(conf.REAL_TRAIN_MRI, str(idx) + ".png")
                    shutil.copyfile(current_image_path, target_image_path)

                    # Advance counter
                    idx += 1
