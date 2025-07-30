# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import List, Optional, Literal, Callable
from captum.attr import IntegratedGradients
import torch.nn as nn
import torch


from obzai.xai.tools.xai_tool import ClassDiscriminativeTool
from obzai.xai.postprocessing import Regionizer


class IntegratedGradientsTool(ClassDiscriminativeTool):
    def __init__(self, 
                 model: nn.Module,
                 n_steps: int = 50,
                 baseline: Optional[torch.Tensor|float] = None,
                 method: Literal["gausslegendre", "riemann_right", 
                                "riemann_left", "riemann_middle", 
                                "riemann_trapezoid"] = "gausslegendre",
                 internal_batch_size: Optional[int] = None,
                 transform_fn: Optional[Callable] = None,
                 regionizer: Optional[Regionizer] = None
                 ):
        super().__init__()
        self.id = 8
        self.n_steps = n_steps
        self.baseline = baseline
        self.method = method
        self.internal_batch_size = internal_batch_size
        self.transform_fn = transform_fn
        self.regionizer = regionizer

        if not isinstance(self.n_steps, int) or self.n_steps < 1:
            raise ValueError(
                "Expected n_steps argument to be positive integer,"
                f" but got {self.n_steps} instead."
                )
        if self.baseline is not None and (not torch.is_tensor(self.baseline) and not isinstance(self.baseline, float)):
            raise ValueError(
                "Expected baseline argument to be torch.Tensor or float,"
                f" but got {type(self.baseline)} instead."
                )
        if self.method not in ["gausslegendre", "riemann_right", "riemann_left", "riemann_middle", "riemann_trapezoid"]:
            raise ValueError(
                "Expected method argument to be one of: gausslegendre, riemann_right, riemann_left, riemann_middle, riemann_trapezoid"
                f", but got {self.method} instead."
                )
        if self.internal_batch_size is not None and (not isinstance(self.internal_batch_size, int) or self.internal_batch_size < 1):
            raise ValueError(
                "Expected internal_batch_size argument to be positive integer,"
                f" but got {self.internal_batch_size} instead."
                )
        if self.regionizer is not None and not isinstance(self.regionizer, Regionizer):
            raise ValueError(
                "Expected regionizer to be instance of Regionizer class,"
                f" but got {type(self.regionizer)} instead."
            )

        self.model = model.eval()
        self.ig = IntegratedGradients(model)   
    
    def _prepare_xai_maps(self, batch: torch.Tensor, target_idx: int):
        """
        Method implements XAI maps preparation.

        Args:
            batch: Tensor of shape (B, C, H, W).
            target_idx: Integer or list of integers indicating target classes.
                        List is expected to have length equal to the batch size (B).
        
        Returns:
            xai_maps: Tensor of shape (B, 1, H, W)
        """
        if self.transform_fn:
            batch = self.transform_fn(batch)

        # Checks whether provided batch meet requirements
        self._batch_sanity_check(batch)
        # Checks type, length of provided target_idx and if possible return in correct format.
        target_idx = self._target_sanity_check(batch, target_idx)

        if not batch.requires_grad:
            batch.requires_grad_()
        
        scores = self.ig.attribute(batch, 
                                   baselines=self.baseline, 
                                   target=target_idx, 
                                   n_steps=self.n_steps, 
                                   method=self.method,
                                   internal_batch_size=self.internal_batch_size
                                   )
        
        batch.requires_grad_(requires_grad=False)
        scores = torch.sum(scores, dim=1, keepdim=True).detach().cpu()
        xai_maps = torch.clamp(scores, min=torch.quantile(scores, 0.01), max=torch.quantile(scores, 0.99))
        
        return xai_maps


    def explain(self, 
                batch: torch.Tensor,
                target_idx: int | List[int]
                ) -> torch.Tensor:
        """
        Method provides XAI maps to a provided batch of images.

        Args:
            batch: Tensor of shape (B, C, H, W).
            target_idx: Integer or list of integers indicating target classes.
                        List is expected to have length equal to the batch size (B).
        
        Returns:
            xai_maps: Tensor of shape (B, 1, H, W) 
        """
        xai_maps = self._prepare_xai_maps(batch, target_idx)

        if self.regionizer:
            xai_maps = self.regionizer.regionize(batch, xai_maps)

        return xai_maps
    