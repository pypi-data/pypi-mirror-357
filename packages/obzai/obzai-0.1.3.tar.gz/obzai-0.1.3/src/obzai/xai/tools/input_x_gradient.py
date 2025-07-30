# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import List, Union, Optional, Callable
from captum.attr import InputXGradient
import torch.nn as nn
import torch


from obzai.xai.tools.xai_tool import ClassDiscriminativeTool
from obzai.xai.postprocessing import Regionizer


class InputXGradientTool(ClassDiscriminativeTool):
    def __init__(self, 
                 model: nn.Module,
                 transform_fn: Optional[Callable] = None,
                 regionizer: Optional[Regionizer] = None
                 ):
        super().__init__()
        self.id = 7

        self.transform_fn = transform_fn
        self.regionizer = regionizer

        self.model = model.eval()
        self.inputXgradient = InputXGradient(model)

        if self.regionizer is not None and not isinstance(self.regionizer, Regionizer):
            raise ValueError(
                "Expected regionizer to be instance of Regionizer class,"
                f" but got {type(self.regionizer)} instead."
            )
    
    def _prepare_xai_maps(self, batch: torch.Tensor, target_idx: Union[int, List[int]]):
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
        
        scores = self.inputXgradient.attribute(batch,target=target_idx)
        
        batch.requires_grad_(requires_grad=False)
        scores = torch.sum(scores, dim=1, keepdim=True).detach().cpu()
        xai_maps = torch.clamp(scores, min=torch.quantile(scores, 0.01), max=torch.quantile(scores, 0.99))

        return xai_maps.detach().cpu()
    
    def explain(self, 
                batch: torch.Tensor,
                target_idx: Union[int, List[int]]
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

    