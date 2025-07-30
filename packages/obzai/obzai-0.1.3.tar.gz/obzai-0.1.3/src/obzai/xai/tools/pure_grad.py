# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import Literal, Union, List, Optional, Callable
import torch.nn as nn
import numpy as np
import contextlib
import warnings
import torch


from obzai.xai.tools.xai_tool import ClassDiscriminativeTool
from obzai.xai.postprocessing import Regionizer


class PureGradTool(ClassDiscriminativeTool):
    """
    Implementation of PureGrad method for Vision Transformers.
    """
    def __init__(
        self,
        model: nn.Module,
        gradient_type: Literal["from_logits", "from_probabilities"] = "from_logits",
        activation_type: Optional[Literal["sigmoid", "softmax"]] = None,
        ommit_tokens: int = 1,
        transform_fn: Optional[Callable] = None,
        regionizer: Optional[Regionizer] = None
    ):
        super().__init__()
        self.id = 4
        self.model = model.eval()
        self.gradient_type = gradient_type
        self.activation_type = activation_type
        self.ommit_tokens = ommit_tokens
        self.transform_fn = transform_fn
        self.regionizer = regionizer

        if self.gradient_type not in ["from_logits", "from_probabilities"]:
            raise ValueError(
                "Expected gradient_type argument to be equal: 'from_logits' or 'from_probabilities',"
                f"but got {self.gradient_type} instead."
            ) 
        if self.gradient_type == "from_probabilities" and self.activation_type not in ["sigmoid", "softmax"]:
            raise ValueError(
                f"Expect activation type to be provided when gradient type is set to {self.gradient_type},"
                f"but got {self.activation_type} instead."
            )
        if self.ommit_tokens < 1:
            raise ValueError(
                "Expected ommit_tokens argument to be greater than 1,"
                f"but got {self.ommit_tokens} instead"
            )
        if self.regionizer is not None and not isinstance(self.regionizer, Regionizer):
            raise ValueError(
                "Expected regionizer to be instance of Regionizer class,"
                f" but got {type(self.regionizer)} instead."
            )

        self.gradients = {}
        self.created_hooks = False
        self.run_hook = False
        self.layer_name = None
        self.gradient_hook = None

    def _check_if_images_are_square(self, batch: torch.Tensor):
        B, C, H, W = batch.shape
        if H != W:
            raise ValueError("Expected input images to be squares, ",
                             f"but got images of height {H} and width {W}.")

    @contextlib.contextmanager
    def hook_manager(self):
        """Enable hooks for a single forward/backward pass."""
        self.run_hook = True
        try:
            yield
        finally:
            self.run_hook = False

    def create_hooks(self, layer_name: str):
        """Register backward hook that capture raw gradients."""
        if self.created_hooks:
            raise RuntimeError("Hooks already exist.")
        self.layer_name = layer_name
        layer = dict(self.model.named_modules())[layer_name]

        def backward_hook(module, grad_input, grad_output):
            if self.run_hook:
                self.gradients[layer_name] = grad_output[0]

        self.gradient_hook = layer.register_full_backward_hook(backward_hook)
        self.created_hooks = True

    def remove_hooks(self):
        """Remove any registered hooks."""
        if self.created_hooks:
            self.gradient_hook.remove()
            self.created_hooks = False
        else:
            raise RuntimeWarning("No hooks to remove.")
        
    def _prepare_xai_maps(self, batch: torch.Tensor, target_idx: Union[int, List[int]]):
        """
        This method performs core operation i.e. computes average of gradients.

        Args:
            batch: Tensor of shape (B, C, H, W). It assumes that H == W.
            target_idx: Integer or list of integers indicating target classes.
                        List is expected to have length equal to the batch size (B).
        
        Returns:
            pure_grad_map: Tensor of shape (B, 1, H, W)
        """
        if not self.created_hooks:
            raise RuntimeError("Hooks must be created before computing CDAM.")
        
        if self.transform_fn:
            batch = self.transform_fn(batch)
        
        B, C, H, W = batch.shape

        # Checks whether provided batch meet requirements
        self._batch_sanity_check(batch)
        self._check_if_images_are_square(batch)
        # Checks type, length of provided target_idx and if possible return in correct format.
        target_idx = self._target_sanity_check(batch, target_idx)

        with self.hook_manager():
            outputs = self.model(batch)
            self.model.zero_grad()

            if self.gradient_type == "from_logits":
                outputs[range(B), target_idx].sum().backward()
            else:
                if self.activation_type == "sigmoid":
                    probs = torch.sigmoid(outputs)
                else:
                    probs = torch.softmax(outputs, dim=1)
                probs[range(B), target_idx].sum().backward()

        grads = self.gradients[self.layer_name][:, self.ommit_tokens:, :]

        # Averaging raw gradients
        scores = torch.mean(grads, dim=2)

        side = int(np.sqrt(grads.size(1)))
        maps = scores.reshape(B, side, side)

        # clamp extremes and upscale to input resolution
        maps = torch.clamp(
            maps,
            min=torch.quantile(maps, 0.01),
            max=torch.quantile(maps, 0.99)
        )
        return torch.nn.functional.interpolate(
            maps.unsqueeze(1), scale_factor=H/side, mode="nearest"
        ).cpu()
    
    def explain(self, batch: torch.Tensor, target_idx: Union[int, List[int]]) -> torch.Tensor:
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


