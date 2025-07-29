from __future__ import annotations

from typing import cast

from qermod.noise import AbstractNoise, CompositeNoise
from qermod.protocols import *

TYPE_TO_PROTOCOLS: dict = {
    "PrimitiveNoise": PrimitiveNoise,
    "Bitflip": Bitflip,
    "Phaseflip": Phaseflip,
    "PauliChannel": PauliChannel,
    "AmplitudeDamping": AmplitudeDamping,
    "PhaseDamping": PhaseDamping,
    "DigitalDepolarizing": DigitalDepolarizing,
    "GeneralizedAmplitudeDamping": GeneralizedAmplitudeDamping,
    "AnalogDepolarizing": AnalogDepolarizing,
    "Dephasing": Dephasing,
    "IndependentReadout": IndependentReadout,
    "CorrelatedReadout": CorrelatedReadout,
}


def serialize(noise: AbstractNoise) -> dict:
    """Serialize noise.

    Args:
        noise (AbstractNoise): A noise configuration

    Returns:
        dict: Dictionary for serialization.
    """
    type_noise = str(type(noise)).split(".")[-1][:-2]
    return cast(dict, noise.model_dump()) | {"type": type_noise}


def deserialize(noise: dict) -> AbstractNoise:
    """Deserialize the noise dictionary back to an instance.

    Args:
        noise (dict): Dictionary of noise specifications.

    Returns:
        AbstractNoise: Instance.
    """
    if "blocks" in noise:
        blocks: tuple = tuple()
        for i in range(len(noise["blocks"])):
            options = noise["blocks"][str(i)]
            type_noise_i = TYPE_TO_PROTOCOLS[options["type"]]
            optionsnotype = options.copy()
            optionsnotype.pop("type")
            blocks += type_noise_i(
                **optionsnotype,
            )
        return CompositeNoise(blocks=blocks)
    else:
        type_noise_i = TYPE_TO_PROTOCOLS[noise["type"]]
        optionsnotype = noise.copy()
        optionsnotype.pop("type")
        noise_instance: AbstractNoise = type_noise_i(**optionsnotype)
        return noise_instance
