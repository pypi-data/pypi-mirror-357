import argparse

import keras_tuner as kt
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from seg_tgce.data.crowd_seg.tfds_builder import get_processed_data_baseline
from seg_tgce.experiments.plot_utils import plot_training_history, print_test_metrics
from seg_tgce.models.builders import (
    build_baseline_model_from_hparams,
)
from seg_tgce.models.ma_model import BaselineVisualizationCallback

TARGET_SHAPE = (32, 32)
BATCH_SIZE = 32
NUM_CLASSES = 6
TRAIN_EPOCHS = 20
TUNER_EPOCHS = 2
MAX_TRIALS = 5

DEFAULT_HPARAMS = {
    "q": 0.6,
    "noise_tolerance": 0.2,
    "dropout_rate": 0.2,
}


def build_model(hp=None):
    if hp is None:
        params = DEFAULT_HPARAMS
    else:
        params = {
            "q": hp.Float("q", min_value=0.1, max_value=0.9, step=0.1),
            "noise_tolerance": hp.Float(
                "noise_tolerance", min_value=0.1, max_value=0.9, step=0.1
            ),
            "dropout_rate": hp.Float(
                "dropout_rate", min_value=0.0, max_value=0.5, step=0.1
            ),
        }

    return build_baseline_model_from_hparams(
        learning_rate=1e-3,
        q=params["q"],
        noise_tolerance=params["noise_tolerance"],
        num_classes=NUM_CLASSES,
        target_shape=TARGET_SHAPE,
        dropout_rate=params["dropout_rate"],
    )


def train_with_tuner(train_gen, val_gen):
    tuner = kt.BayesianOptimization(
        build_model,
        objective=kt.Objective("val_dice_coefficient", direction="max"),
        max_trials=MAX_TRIALS,
        directory="tuner_results",
        project_name="histology_scalar_tuning",
    )

    print("Starting hyperparameter search...")
    tuner.search(
        train_gen.take(10),
        epochs=TUNER_EPOCHS,
        validation_data=val_gen,
    )

    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    print("\nBest hyperparameters:")
    for param, value in best_hps.values.items():
        print(f"{param}: {value}")

    return build_model(best_hps)


def train_directly():
    return build_model()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train histology scalar model with or without hyperparameter tuning"
    )
    parser.add_argument(
        "--use-tuner",
        action="store_true",
        help="Use Keras Tuner for hyperparameter optimization",
    )
    args = parser.parse_args()

    processed_train, processed_validation, processed_test = get_processed_data_baseline(
        image_size=TARGET_SHAPE,
        batch_size=BATCH_SIZE,
        # use_augmentation=True,
        # augmentation_factor=2,
    )

    if args.use_tuner:
        print("Using Keras Tuner for hyperparameter optimization...")
        model = train_with_tuner(processed_train, processed_validation)
    else:
        print("Training with default hyperparameters...")
        model = train_directly()

    vis_callback = BaselineVisualizationCallback(processed_validation)

    lr_scheduler = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=4,
        min_lr=1e-6,
        mode="min",
        verbose=1,
    )

    print("\nTraining final model...")

    history = model.fit(
        processed_train,
        epochs=TRAIN_EPOCHS,
        validation_data=processed_validation,
        callbacks=[
            vis_callback,
            lr_scheduler,
            EarlyStopping(
                monitor="val_dice_coefficient",
                patience=3,
                mode="max",
                restore_best_weights=True,
            ),
        ],
    )

    plot_training_history(
        history,
        "Histology Baseline Model Training History",
        ["loss", "dice_coefficient", "jaccard_coefficient"],
    )
    print_test_metrics(
        model,
        processed_test,
        "Histology Baseline Model",
    )
