import json
import os
import random
import time

import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optimizer
from torch.nn import DataParallel
from torch.utils.data import SubsetRandomSampler, DataLoader

import config as config
import data_loaders.dataset as dataset
from metrics.metrics import PixelAccuracy, DiceScore, IoUScore
from models.mask_rcnn import MaskRCNN
from models.u_net import UNet

conf = config.Config()


def get_dataset_split(real_indexes: list, gan_data_indexes: list, augmented: bool = False,
                      val_fold: int = None) -> tuple:
    """
    Split the data into train, validation and test.
    make sure that the gan generated data is not included in the validation and test dataset.
    :param augmented: controls if the gan generated data are included or not.
    :param number_of_folds: The number of folds we have or the k variable in k-fold
    :param val_fold: the validation split fold number. The test fold will be the index just before
    :param gan_generated_dataset_size: size of the gan generated dataset.
    :param real_dataset_size: real dataset size.
    :return:
    """
    assert 0 < val_fold <= conf.K_FOLD, f'Validation fold index should be in [1, {conf.K_FOLD}], got {val_fold}'

    real_dataset_size = len(real_indexes)
    fold_size = real_dataset_size // conf.K_FOLD

    val_index_start = fold_size * ((val_fold - 1) % conf.K_FOLD)
    val_index_end = fold_size + val_index_start
    test_index_start = fold_size * (val_fold % conf.K_FOLD)
    test_index_end = test_index_start + fold_size

    # Assign to each split the corresponding indexes
    if val_fold == 10:
        train_indexes = real_indexes[test_index_end:val_index_start] + real_indexes[
                                                                       val_index_end:] + gan_data_indexes if augmented else \
            real_indexes[test_index_end:val_index_start] + real_indexes[val_index_end:]

    else:
        train_indexes = real_indexes[:val_index_start] + real_indexes[
                                                         test_index_end:] + gan_data_indexes if augmented else \
            real_indexes[:val_index_start] + real_indexes[test_index_end:]

    val_indexes = real_indexes[val_index_start: val_index_end]
    test_indexes = real_indexes[test_index_start: test_index_end]

    return SubsetRandomSampler(train_indexes), SubsetRandomSampler(val_indexes), SubsetRandomSampler(test_indexes)


def create_model_dict() -> dict:
    return {
        'unet': {
            'model': UNet(),
            'data': {
                'real_data': {
                    'train': DataLoader(dataset=unet_dataset_train, sampler=train_sampler, batch_size=conf.BATCH_SIZE,
                                        num_workers=4),
                    'val': DataLoader(dataset=test_dataset, sampler=val_sampler, batch_size=conf.BATCH_SIZE,
                                      num_workers=4),
                    'test': DataLoader(dataset=test_dataset, sampler=test_sampler, batch_size=conf.BATCH_SIZE,
                                       num_workers=4)
                },
                'gan_data': {
                    'train': DataLoader(dataset=unet_dataset_train, sampler=train_sampler_augmented,
                                        batch_size=conf.BATCH_SIZE, num_workers=4),
                    'val': DataLoader(dataset=test_dataset, sampler=val_sampler_augmented,
                                      batch_size=conf.BATCH_SIZE, num_workers=4),
                    'test': DataLoader(dataset=test_dataset, sampler=test_sampler_augmented,
                                       batch_size=conf.BATCH_SIZE, num_workers=4)
                }
            },
            'ref_model': torch.hub.load('mateuszbuda/brain-segmentation-pytorch', 'unet',
                                        in_channels=3, out_channels=1, init_features=32, pretrained=True),
            'ref_test': DataLoader(dataset=ref_model_test_dataset, sampler=test_sampler,
                                   batch_size=conf.BATCH_SIZE, num_workers=4)

        }
    }


def invert_dict_of_tensors(target):
    """
    Change dict{ 'a': Tensor, 'b': Tensor ...} to list[ Dict {'a': Tensor ...}]
    :param target: dictionary to change
    :return:
    """
    result = []
    for idx in range(len(target['boxes'])):
        dictionary = {
            'masks': target['masks'][idx],
            'boxes': target['boxes'][idx],
            'labels': target['labels'][idx]
        }
        result.append(dictionary)

    return result


def train(target_model: nn.Module, data_loader: DataLoader, opt: optimizer.Optimizer, epoch: int,
          model_name: str, data_type: str, k_iteration: int) -> float:
    """
    Trains the model and logs the training result in a file.
    :param data_type: the name of the data loader wither it is real or gan augmented
    :param target_model: the model to train
    :param opt: the optimizer
    :param epoch: the current number of epochs
    :param model_name: the model name
    :return: this training loss
    """
    target_model.train()

    # Initiate the loss
    loss_sum = 0.0

    # Open Log file
    file_name = os.path.join(conf.CHECKPOINT_FOLDER, f'{model_name}_{data_type}_training_loss_{k_iteration}.log')
    log_file = open(file_name, 'a+')

    start_time_epoch = time.time()
    for batch_idx, (data, target) in enumerate(data_loader):
        # Move data to gpu
        data = data.to('cuda')
        opt.zero_grad()

        # Invert the dict of tensors you get from the MaskRCNN
        if type(target_model.module) == MaskRCNN:
            inverted_target_output = invert_dict_of_tensors(target)
            output = target_model(data, inverted_target_output)
            loss = torch.stack([loss for key, loss in output.items()]).sum()

        else:
            # Move target to gpu. This is done here because this piece of code is related to UNet while the other one is
            # for mask_rcnn
            target = target.to('cuda')
            output = target_model(data)
            loss = f.binary_cross_entropy_with_logits(output, target)

        loss_sum += float(loss)

        loss.backward()
        opt.step()

        if batch_idx and batch_idx % 10 == 0:
            message = f'Epoch: {epoch} | Iteration number: [{batch_idx}/{len(data_loader)}] {batch_idx * 100 // len(data_loader)}% | Training loss: {loss_sum / batch_idx}\n'
            log_file.writelines([message])

    message = f'End of epoch: {epoch} | Train Loss: {loss_sum / len(data_loader)} | Training Time: {int(time.time() - start_time_epoch)}'
    log_file.write(f'\n {message} \n')
    log_file.close()

    return loss_sum / len(data_loader)


def validate(target_model: nn.Module, data_loader: DataLoader, epoch: int,
             model_name: str, data_type: str, k_iteration: int) -> float:
    """
    validate the model.
    :param model_name: the model name
    :param data_loader: the data loader
    :param epoch: the epoch number
    :param data_type: real data or gan generated data
    :param target_model: the model instance
    :param k_iteration: iteration number
    :return: this epoch validation loss
    """
    target_model.eval()
    global best_eval_loss

    # Initiate the loss
    loss_sum = 0.0

    # Open Log file
    file_name = os.path.join(conf.CHECKPOINT_FOLDER, f'{model_name}_{data_type}_training_loss_{k_iteration}.log')
    log_file = open(file_name, 'a+')

    start_time_epoch = time.time()

    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(data_loader):
            # Copy data to gpu
            data, target = data.to('cuda'), target.to('cuda')
            output = target_model(data)

            if type(target_model.module) == MaskRCNN:
                # Get the tensors from the output and concat for each image the masks using max
                # The result would be like putting all the masks on top of each other.
                list_of_masks = []
                for dictionary in output:
                    # Check if there is no maks generated, If so make an empty mask
                    if dictionary['masks'].size()[0] == 0:
                        list_of_masks.append(torch.zeros(size=(1, 256, 256), dtype=torch.float32, device='cuda'))

                    else:
                        list_of_masks.append(torch.max(dictionary['masks'], dim=0)[0])

                # Stack the list of tensors
                inverted_output = torch.stack(list_of_masks)
                loss = f.binary_cross_entropy_with_logits(inverted_output, target)

            else:
                output = target_model(data)
                loss = f.binary_cross_entropy_with_logits(output, target)

            loss_sum += float(loss)

    message = f'End of epoch: {epoch} | Eval Loss: {loss_sum / len(data_loader)} | Evaluating Time: {int(time.time() - start_time_epoch)}'
    log_file.write(f'\n {message} \n')
    log_file.close()

    if loss_sum / len(data_loader) < best_eval_loss:
        best_eval_loss = loss_sum / len(data_loader)
        torch.save(target_model,
                   os.path.join(conf.CHECKPOINT_FOLDER, f'{model_name}_{data_type}_best_model_{k_iteration}.pth'))

    return loss_sum / len(data_loader)


def test(target_model: nn.Module, data_loader: DataLoader,
         model_name: str, data_type: str, k_iteration: int) -> dict:
    """
    validate the model.
    :param model_name: the model name
    :param data_loader: the data loader
    :param data_type: real data or gan generated data
    :param target_model: the model instance
    :return: return different test results
    """
    target_model.eval()
    global best_eval_loss

    # Initiate the loss
    bcewl_loss_sum = 0.0
    dice_score_sum = 0.0
    mean_iou_sum = 0.0
    pixel_accuracy_sum = 0.0

    # Open Log file
    file_name = os.path.join(conf.CHECKPOINT_FOLDER, f'{model_name}_{data_type}_training_loss_{k_iteration}.log')
    log_file = open(file_name, 'a+')

    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(data_loader):
            # copy data to gpu
            data, target = data.to('cuda'), target.to('cuda')
            filter = nn.Threshold(conf.FILTER_THRESHOLD, 0.0)
            negative_filter = nn.Threshold(-conf.FILTER_THRESHOLD, -1.0)

            output = target_model(data)

            if type(target_model.module) == MaskRCNN:
                # Get the tensors from the output and concat for each image the masks using max
                # The result would be like putting all the masks on top of each other.
                list_of_masks = []
                for dictionary in output:
                    # Check if there is no maks generated, If so make an empty mask
                    if dictionary['masks'].size()[0] == 0:
                        list_of_masks.append(torch.zeros(size=(1, 256, 256), dtype=torch.float32, device='cuda'))

                    else:
                        list_of_masks.append(torch.max(dictionary['masks'], dim=0)[0])

                # Stack the list of tensors
                inverted_output = torch.stack(list_of_masks)
                # Filter the matrix. every value <= 0.5 will be turned to 0 and those who are > 0.5 will be turned to 1
                filtered_output = -negative_filter(-filter(inverted_output))

            else:
                output = target_model(data)
                # Filter output
                filtered_output = -negative_filter(-filter(output))

            bcewl_loss = f.binary_cross_entropy_with_logits(filtered_output, target)
            dice_score = DiceScore()(inputs=filtered_output, targets=target)
            mean_iou_score = IoUScore()(inputs=filtered_output, targets=target)
            pixel_accuracy = PixelAccuracy()(predicted=filtered_output, target=target)

            # Sum the losses
            bcewl_loss_sum += float(bcewl_loss)
            dice_score_sum += float(dice_score)
            mean_iou_sum += float(mean_iou_score)
            pixel_accuracy_sum += float(pixel_accuracy)

    message = f'End of Test | Dice Loss: {dice_score_sum / len(data_loader)} | Binary Cross Entropy With Logits Loss: {bcewl_loss_sum / len(data_loader)}'
    log_file.write(f'\n {message} \n')
    log_file.close()

    return {'bcewl_loss': bcewl_loss_sum / len(data_loader),
            'dice_score': dice_score_sum / len(data_loader),
            'mean_iou': mean_iou_sum / len(data_loader),
            'pixel_accuracy': pixel_accuracy_sum / len(data_loader)}


if __name__ == "__main__":
    # Check if checkpoint folder are there
    if not os.path.isdir(conf.CHECKPOINT_FOLDER):
        os.mkdir(conf.CHECKPOINT_FOLDER)

    unet_dataset_train = dataset.CustomDataset(mask_rcnn=False, train=True, mean=conf.DATASET_MEAN,
                                               std=conf.DTATSET_STD)
    mask_rcnn_dataset_train = dataset.CustomDataset(mask_rcnn=True, train=True, mean=conf.DATASET_MEAN,
                                                    std=conf.DTATSET_STD)
    test_dataset = dataset.CustomDataset(train=False, mean=conf.DATASET_MEAN, std=conf.DTATSET_STD)
    ref_model_test_dataset = dataset.CustomDataset(train=False, ref_model=True)

    # Make list of indexes
    real_indexes = list(range(test_dataset.real_data_size()))
    gan_data_indexes = list(range(test_dataset.gan_generated_data_size()))

    # Shuffle list indexes
    random.shuffle(gan_data_indexes)
    random.shuffle(real_indexes)

    k_fold_dict = {}

    for k_iteration in range(1, conf.K_FOLD + 1):
        # Make train sampler for gan augmented data and real_data
        train_sampler, val_sampler, test_sampler = get_dataset_split(real_indexes=real_indexes,
                                                                     gan_data_indexes=gan_data_indexes,
                                                                     val_fold=k_iteration)
        train_sampler_augmented, val_sampler_augmented, test_sampler_augmented = get_dataset_split(
            real_indexes=real_indexes, gan_data_indexes=gan_data_indexes, augmented=True, val_fold=k_iteration)

        # Prepare data loaders for different models
        models_dict = create_model_dict()
        # Initiate result dict
        model_data = {}
        for model_name, value in models_dict.items():
            # Get the model to work in a multi-gpu environment
            model = DataParallel(value['model'])
            ref_model = DataParallel(value['ref_model'])
            # Prepare optimizer
            opt = optimizer.Adam(lr=0.0001, params=model.parameters())

            model_data[model_name] = {}
            # Iterate through both kind of datasets:
            for data_type, dataloader_dict in value['data'].items():
                model_data[model_name][data_type] = {
                    'training_loss': [],
                    'eval_loss': [],
                    'test_loss': {}
                }
                global best_eval_loss
                best_eval_loss = 100
                for epoch in range(1, conf.EPOCHS_SEG + 1):
                    training_loss = train(target_model=model, data_loader=dataloader_dict['train'], opt=opt,
                                          epoch=epoch,
                                          model_name=model_name, data_type=data_type, k_iteration=k_iteration)
                    model_data[model_name][data_type]['training_loss'].append(training_loss)

                    eval_loss = validate(target_model=model, data_loader=dataloader_dict['val'], epoch=epoch,
                                         model_name=model_name, data_type=data_type, k_iteration=k_iteration)
                    model_data[model_name][data_type]['eval_loss'].append(eval_loss)

                test_loss = test(target_model=model, data_loader=dataloader_dict['test'], model_name=model_name,
                                 data_type=data_type, k_iteration=k_iteration)

                model_data[model_name][data_type]['test_loss'] = test_loss

            # Test the ref model on the test set after finishing the iteration for both other data types
            ref_model_test_loss = test(target_model=ref_model, data_loader=value['ref_test'],
                                       model_name=model_name, data_type='test_model_data', k_iteration=k_iteration)
            model_data[model_name]['ref_test_loss'] = ref_model_test_loss

        k_fold_dict[k_iteration] = model_data

    final_result_file = open(os.path.join(conf.CHECKPOINT_FOLDER, 'final_result.json'), 'w')
    final_result_file.write(json.dumps(k_fold_dict))
    final_result_file.close()
