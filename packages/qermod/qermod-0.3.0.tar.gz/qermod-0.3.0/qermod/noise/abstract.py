from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from qermod.types import Noise, NoiseType

# to handle torch Tensor
BaseModel.model_config["arbitrary_types_allowed"] = True


class AbstractNoise(ABC, BaseModel):
    """Base class for noise."""

    model_config = ConfigDict(extra="forbid")

    def __or__(self, other: AbstractNoise) -> AbstractNoise:
        from qermod.noise.utils import chain

        if not isinstance(other, AbstractNoise):
            raise TypeError(f"Can only add a block to another block. Got {type(other)}.")
        return chain(self, other)

    def __ior__(self, other: AbstractNoise) -> AbstractNoise:
        from qermod.noise.composite import CompositeNoise
        from qermod.noise.utils import chain

        if not isinstance(other, AbstractNoise):
            raise TypeError(f"Can only add a block to another block. Got {type(other)}.")

        # We make sure to unroll any CompositeNoise, because for ior we
        # assume the user expected in-place addition
        return chain(
            *self.blocks if isinstance(self, CompositeNoise) else (self,),
            *other.blocks if isinstance(other, CompositeNoise) else (other,),
        )

    @abstractmethod
    def filter(self, noise_type: type[Noise] | NoiseType) -> list[AbstractNoise]:
        """Filter by `noise_type`.

        Args:
            noise_type (type[Noise] | NoiseSubType): Type of noise to keep.

        Returns:
            list[AbstractNoise]: Filtered noise with `noise_type`.
        """
        pass
