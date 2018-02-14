"""
This module facilitates the creation of DiTTo layerstacks (https://github.com/Smart-DS/layerstack).
"""


import logging

logger = logging.getLogger(__name__)

from layerstack.layer import ModelLayerBase
from .core.exceptions import DiTToNotImplementedError


class DiTToLayerBase(ModelLayerBase):
    @classmethod
    def _check_model_type(cls,model):
        # Check to make sure model is of the proper type
        pass

    @classmethod
    def _load_model(cls, model_path):
        # Method to load model
        logger.error("DiTTo models cannot be loaded. Start your stack with a load-model layer.")
        raise DiTToNotImplementedError("DiTTo models cannot be loaded.")

    @classmethod
    def _save_model(cls, model_path):
        # Method to save model
        logger.error("DiTTo models cannot be saved. End your stack with a save-model layer.")
        raise DiTToNotImplementedError("DiTTo models cannot be saved.")
