import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sktime.performance_metrics.forecasting import mean_absolute_error

from ml.exception.exception import CallForecastException
from ml.logger.logger import logging


class Model:
    def __init__(
        self,
        trained_model_object: object,
        training_data: pd.DataFrame,
        test_data: pd.DataFrame,
    ):
        """
        :param preprocessing_object: Input Object of preprocesser
        :param trained_model_object: Input Object of trained model
        :param training_data: Input training data
        :param test_data: Input test data

        """
        self.trained_model_object = trained_model_object
        self.training_data = training_data
        self.test_data = test_data

    def predict(self, fh: int):
        """
        Predict the output using the trained model
        :param data: Input data to be predicted
        """
        try:
            fh_pred = np.arange(1, fh + 1)
            self.prediction = self.trained_model_object.predict(fh=fh_pred)
            logging.info("Prediction successful from estimator")
            return self.prediction
        except Exception as e:
            raise CallForecastException(e, sys)

    def model_metrics(self):
        try:
            test_fh = np.arange(1, len(self.test_data) + 1)
            y_pred = self.trained_model_object.predict(fh=test_fh)

            # Compute Mean Absolute Error (MAE)
            mae = mean_absolute_error(self.test_data["Healthcare"], y_pred)
            print("MAE: ", mae)
            y_pred = pd.Series(y_pred, index=self.test_data.index)

            # Compute Directional Accuracy (DA)
            y_test_diff = (
                self.test_data["Healthcare"].diff().dropna().reset_index(drop=True)
            )
            y_pred_diff = y_pred.diff().dropna().reset_index(drop=True)
            da = np.mean(np.sign(y_test_diff) == np.sign(y_pred_diff))
            logging.info("Metrics calculated successfully")
            return mae, da
        except Exception as e:
            raise CallForecastException(e, sys)
