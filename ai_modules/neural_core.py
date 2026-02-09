"""Neural network core - model management and inference"""
import torch
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NeuralCore:
    """Manages model loading and inference"""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize neural core
        
        Args:
            device: 'cpu' or 'cuda', defaults to 'cuda' if available
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        self.models = {}
    
    def load_model(self, model_name: str, model_class, **kwargs):
        """
        Load a model and cache it
        
        Args:
            model_name: Name/identifier for the model
            model_class: The model class to instantiate
            **kwargs: Arguments to pass to model_class
        
        Returns:
            Loaded model on the configured device
        """
        if model_name not in self.models:
            logger.info(f"Loading model: {model_name}")
            model = model_class(**kwargs)
            model.to(self.device)
            model.eval()
            self.models[model_name] = model
        
        return self.models[model_name]
    
    def clear_cache(self):
        """Clear all cached models to free memory"""
        self.models.clear()
        torch.cuda.empty_cache() if self.device == 'cuda' else None
        logger.info("Model cache cleared")
    
    def get_device(self) -> torch.device:
        """Get the torch device object"""
        return torch.device(self.device)
    
    @staticmethod
    def check_cuda():
        """Check CUDA availability and print info"""
        print(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            print(f"PyTorch Version: {torch.__version__}")
