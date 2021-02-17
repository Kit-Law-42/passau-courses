import os
import torch


class Config:
    PROJECT_DIR = 'C:\\Users\\dhiae\\data_science_lab'
    WORKING_DIR = os.path.join(PROJECT_DIR, "src")

    # directory where all data will be put.
    DATASET_DIR = os.path.join(WORKING_DIR, "data")

    # the path of the original Kaggle dataset. Change it according to where you have put the dataset and what you have named the folder containing it.
    KAGGLE_3M_DATASET_DIR = os.path.join(DATASET_DIR, "lgg-mri-segmentation/kaggle_3m")

    # Real data paths
    REAL_DATA_DIR = os.path.join(DATASET_DIR, 'real_dataset')
    REAL_TRAIN_MASK = os.path.join(REAL_DATA_DIR, "mask")
    REAL_TRAIN_MRI = os.path.join(REAL_DATA_DIR, "mri")

    GAN_TRAIN_DATASET = os.path.join(DATASET_DIR, "gan_dataset")
    GAN_TRAIN_MASK = os.path.join(GAN_TRAIN_DATASET, "A")
    GAN_TRAIN_MRI = os.path.join(GAN_TRAIN_DATASET, "B")
    GAN_COMBINED_DATASET = os.path.join(GAN_TRAIN_DATASET, "mask_mri")

    IMAGE_EXTENSION = ".jpg"

    # K-Folds. The split will be 1/K_fold for validation and the same for test and the rest is for the training.
    K_FOLD = 10

    # The path to the folder where to save the generated masks
    GAN_GENERATED_IMG = os.path.join(DATASET_DIR, "gan_generated_img")
    GAN_GENERATED_MASKS = os.path.join(GAN_GENERATED_IMG, "gan_generated_masks")
    GAN_GENERATED_MRI = os.path.join(GAN_GENERATED_IMG, "gan_generated_mri")

    # GAN model name
    GAN_MODEL_NAME = "mri_pix2pix"

    # Dict containing boxes data
    FILE_PATH = os.path.join(DATASET_DIR, 'boxes_classes.json')

    # Checkpoint root folder
    CHECKPOINT_FOLDER = os.path.join(WORKING_DIR, 'checkpoints')

    # Training parameter
    BATCH_SIZE = 8
    EPOCHS_SEG = 100
    NUM_WORKERS = 2
    FILTER_THRESHOLD = 0.5

    # The mean and std of the dataset. you can get these using utils.calc_mean_std
    DATASET_MEAN = torch.tensor([0.0875, 0.0833, 0.0919])
    DTATSET_STD = torch.tensor([0.1229, 0.1182, 0.1217])


