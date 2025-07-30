# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

from scipy.stats import skew, kurtosis
import numpy as np
import torch

from obzai.data_inspector.extractors.extractor import Extractor


class FirstOrderExtractor(Extractor):
    """
    Extracts first-order statistical features from images, inspired by PyRadiomics.
    """
    def __init__(self):        
        # Feature extraction methods
        self.feature_functions = {
            "entropy": self.get_entropy,
            "min": self.get_min_value,
            "max": self.get_max_value,
            "10th_percentile": self.get_10th_percentile,
            "90th_percentile": self.get_90th_percentile,
            "mean": self.mean,
            "median": self.median,
            "interquartile_range": self.get_interquartile_range,
            "range": self.get_range,
            "mean_absolute_deviation": self.get_mean_absolute_deviation,
            "robust_mean_absolute_deviation": self.get_robust_mean_absolute_deviation,
            "root_mean_square": self.get_root_mean_square,
            "skewness": self.get_skewness,
            "kurtosis": self.get_kurtosis,
            "variance": self.get_variance,
            "uniformity": self.get_uniformity
        }
        self.feature_names = list(self.feature_functions.keys())
        self.feat_ids = [i for i in range(1,17)]
        self.id = 1
        self.name = self.__class__.__name__

    def get_entropy(self, image: torch.Tensor) -> torch.Tensor:
        hist = torch.histc(image, bins=256, min=0, max=1)
        hist = hist / hist.sum()
        return -(hist * torch.log2(hist + 1e-6)).sum()
    
    def get_min_value(self, image: torch.Tensor) -> torch.Tensor:
        return image.min()

    def get_max_value(self, image: torch.Tensor) -> torch.Tensor:
        return image.max()

    def get_10th_percentile(self, image: torch.Tensor) -> torch.Tensor:
        return torch.quantile(image.flatten(), 0.1)

    def get_90th_percentile(self, image: torch.Tensor) -> torch.Tensor:
        return torch.quantile(image.flatten(), 0.9)
    
    def mean(self, image: torch.Tensor) -> torch.Tensor:
        return torch.mean(image)
    
    def median(self, image: torch.Tensor) -> torch.Tensor:
        return torch.median(image)

    def get_interquartile_range(self, image: torch.Tensor) -> torch.Tensor:
        q3 = torch.quantile(image.flatten(), 0.75)
        q1 = torch.quantile(image.flatten(), 0.25)
        return q3 - q1

    def get_range(self, image: torch.Tensor) -> torch.Tensor:
        return image.max() - image.min()

    def get_mean_absolute_deviation(self, image: torch.Tensor) -> torch.Tensor:
        mean = torch.mean(image)
        return torch.mean(torch.abs(image - mean))

    def get_robust_mean_absolute_deviation(self, image: torch.Tensor) -> torch.Tensor:
        prcnt10 = self.get_10th_percentile(image)
        prcnt90 = self.get_90th_percentile(image)
        arr_subset = image[(image >= prcnt10) & (image <= prcnt90)]
        return torch.mean(torch.abs(arr_subset - torch.mean(arr_subset)))
    
    def get_root_mean_square(self, image: torch.Tensor) -> torch.Tensor:
        return torch.sqrt(torch.mean(image ** 2))

    def get_skewness(self, image: torch.Tensor) -> torch.Tensor:
        res = skew(image.flatten().detach().cpu().numpy())
        return torch.tensor(res)

    def get_kurtosis(self, image: torch.Tensor) -> torch.Tensor:
        res = kurtosis(image.flatten().detach().cpu().numpy())
        return torch.tensor(res)

    def get_variance(self, image: torch.Tensor) -> torch.Tensor:
        return torch.var(image)
    
    def get_uniformity(self, image: torch.Tensor) -> torch.Tensor:
        hist = torch.histc(image, bins=256, min=0, max=1)
        hist = hist / hist.sum()
        return (hist ** 2).sum()

    def _compute_features_for_image(self, image: torch.Tensor) -> torch.Tensor:
        """
        Compute all first-order statistical features for a single image.
        """
        features = [func(image) for func in self.feature_functions.values()]
        return torch.stack(features)

    def extract(self, image_batch: torch.Tensor) -> np.ndarray:
        """
        Extracts features during production.
        """
        image_batch = self._process_batch(image_batch, ensure_grayscale=True, ensure_scale=True)
        features = []
        for idx in range(len(image_batch)):
            feat = self._compute_features_for_image(image_batch[idx])
            features.append(feat)
        return torch.stack(features, dim=0).numpy()