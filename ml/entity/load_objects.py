import sys
from pathlib import Path

import mlflow
import pandas as pd

from ml.entity.estimator import Model
from ml.exception.exception import CallForecastException
from ml.logger.logger import logging


class LoadObjects:
    def __init__(
        self,
        tracking_uri: str,
        model_name: str,
        training_data_name: str,
        test_data_name: str,
    ):
        self.tracking_uri: str = tracking_uri
        self.model_name: str = model_name
        self.training_data_name: str = training_data_name
        self.test_data_name: str = test_data_name
        self.loaded_model: Model = None
        self.loaded_training_data: pd.Dataframe = None

    def load_model(self):
        try:
            mlflow.set_tracking_uri(self.tracking_uri)

            # Load the model directly from MLflow
            model_uri = f"models:/{self.model_name}@lat"
            self.loaded_model = mlflow.sklearn.load_model(model_uri)
            logging.info("Model loaded successfully")
            return self.loaded_model
        except Exception as e:
            raise CallForecastException(e, sys)

    def load_training_data(self):
        try:
            training_data_path = (
                Path(__file__).parent.parent.parent
                / "artifacts"
                / self.training_data_name
            )
            training_data = (
                pd.read_csv(training_data_path)
                .rename(columns={"Unnamed: 0": "Date"})
                .assign(Date=lambda x: pd.to_datetime(x["Date"]))
                .set_index("Date")
            )
            logging.info("Training data loaded successfully")
            return training_data
        except Exception as e:
            raise CallForecastException(e, sys)

    def load_test_data(self):
        try:
            test_data_path = (
                Path(__file__).parent.parent.parent / "artifacts" / self.test_data_name
            )
            test_data = (
                pd.read_csv(test_data_path)
                .rename(columns={"Unnamed: 0": "Date"})
                .assign(Date=lambda x: pd.to_datetime(x["Date"]))
                .set_index("Date")
            )
            logging.info("Test data loaded successfully")
            return test_data
        except Exception as e:
            raise CallForecastException(e, sys)
