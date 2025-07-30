# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABC, abstractmethod
from typing import List, Union
import torch


class XAITool(ABC):
    """
    Base class for each XAI tool.
    """
    def __init__(self):
        pass

    def _batch_sanity_check(self, batch: torch.Tensor):
        """
        Checks whether input batch is Tensor and has proper shape.
        """
        if not torch.is_tensor(batch):
            raise ValueError(
                "Expected torch.Tensor object as input batch, "
                f"but got {type(batch)} instead."
            )
        
        if batch.dim() != 4:
            raise ValueError(
                "Expected torch.Tensor to be 4th order (B, C, H, W), "
                f"but got torch.Tensor of shape {batch.shape}"
            )
        
        if batch.size(1) not in [1, 3]:
            raise ValueError(
                "Expected torch.Tensor to have 1 or 3 channels at second position, "
                f"but got torch.Tensor of shape: {batch.shape}"
            )


class ClassDiscriminativeTool(XAITool):
    """
    Base class for all class-discriminative XAI tools used for classification models.
    Each class inheriting from this class have to implement .explain() method with target_idx argument.
    """
    def __init__(self):
        super().__init__()
    
    def _target_sanity_check(self, batch: torch.Tensor, target_idx: Union[int, List[int]])->List[int]:
        B, C, H, W = batch.shape

        if isinstance(target_idx, list) and len(target_idx) != B:
            raise ValueError(
                f"Expected target_idx to have length {B} (matching batch size), "
                f"but got {len(target_idx)} instead."
            )
        elif isinstance(target_idx, int):
            target_idx = [target_idx] * B
        
        return target_idx

    
    @abstractmethod
    def explain(self, batch: torch.Tensor, target_idx: Union[int, List[int]]) -> torch.Tensor:
        pass


class ClassAgnosticTool(XAITool):
    """
    Base class for all class-agnostic XAI tools used for classification models.
    Each class inheriting from this class have to implement .explain method.
    """
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def explain(self, batch: torch.Tensor):
        pass