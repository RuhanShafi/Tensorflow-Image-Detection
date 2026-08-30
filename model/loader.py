import numpy as np
import tensorflow as tf

CLASS_NAMES = ['Man', 'Boys', 'Woman', 'Girls']
IMG_HEIGHT = 180
IMG_WIDTH = 180


class Predictor:
    """Loads the trained CNN once and exposes a simple predict() call."""

    def __init__(self, model_path, class_names=None):
        self.class_names = class_names or CLASS_NAMES
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from '{model_path}': {e}") from e

    def predict(self, image: np.ndarray):
        """
        image: RGB uint8 numpy array, any size, shape (H, W, 3).
        Returns (label: str, confidence: float 0-1).
        """
        batch = self._preprocess(image)

        logits = self.model.predict(batch, verbose=0)[0]
        probs = tf.nn.softmax(logits).numpy()

        idx = int(np.argmax(probs))
        label = self.class_names[idx]
        confidence = float(probs[idx])

        return label, confidence

    def predict_all(self, image: np.ndarray):
        """Returns dict of {class_name: probability} for all classes, useful if
        the result panel wants to show a full breakdown rather than just top-1."""
        batch = self._preprocess(image)
        logits = self.model.predict(batch, verbose=0)[0]
        probs = tf.nn.softmax(logits).numpy()
        return {name: float(p) for name, p in zip(self.class_names, probs)}

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected an RGB image (H, W, 3), got shape {image.shape}")

        resized = tf.image.resize(image, (IMG_HEIGHT, IMG_WIDTH))
        # Model's first layer is Rescaling(1./255), so keep values in 0-255 here.
        batch = tf.expand_dims(resized, axis=0)
        return batch