import sys

import numpy as np
import pandas as pd

from ml.entity.config_entity import PredictionConfig
from ml.entity.estimator import Model
from ml.entity.load_objects import LoadObjects
from ml.exception.exception import CallForecastException
from ml.logger.logger import logging


class Predictor:
    def __init__(self, prediction_pipeline_config=PredictionConfig()):
        """
        Predictor constructor
        Input: prediction configuration
        """
        try:
            self.prediction_pipeline_config = prediction_pipeline_config
            self.load_objects = LoadObjects(
                tracking_uri=self.prediction_pipeline_config.tracking_uri,
                model_name=self.prediction_pipeline_config.model_name,
                training_data_name=self.prediction_pipeline_config.training_data_name,
                test_data_name=self.prediction_pipeline_config.test_data_name,
            )
            self.loaded_model = self.load_objects.load_model()
            self.training_data = self.load_objects.load_training_data()
            self.test_data = self.load_objects.load_test_data()
            self.model = Model(
                trained_model_object=self.loaded_model,
                training_data=self.training_data,
                test_data=self.test_data,
            )

            logging.info("Prediction configuration set")
        except Exception as e:
            raise CallForecastException(e, sys)

    def predict(self, fh: int) -> float:
        """
        Predict the output using the trained model
        Input: dataframe of all features of the trained model for prediction
        Output: predicted price
        """
        try:
            prediction = self.model.predict(fh=fh)
            logging.info("Prediction successful from predictor")
            return prediction
        except Exception as e:
            raise CallForecastException(e, sys)

    def get_train_dataframe(self):
        """
        Get the training data
        Output: training data
        """
        try:
            return self.training_data
        except Exception as e:
            raise CallForecastException(e, sys)

    def model_metrics(self):
        try:
            mae, da = self.model.model_metrics()
            logging.info("Model metrics successful from predictor")
            return mae, da
        except Exception as e:
            raise CallForecastException(e, sys)
