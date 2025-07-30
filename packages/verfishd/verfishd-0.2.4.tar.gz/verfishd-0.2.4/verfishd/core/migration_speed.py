# This file should contain several implementations of possible migration speeds
import numpy as np


def migration_speed_with_demographic_noise(E: float, half_saturation_parameter = 0.1) -> float:
    """
    Calculate the migration speed with demographic noise.

    Parameters
    ----------
    E : float
        The evaluation function value.

    Returns
    -------
    float
        The migration speed.
    """
    w_max = 1.0
    # Draw a random number taken out of a normal distribution with mean=0 and standard deviation=0.1
    noise = np.random.normal(loc=0, scale=0.05)

    w_behav = (noise + E) * abs(noise + E) / (half_saturation_parameter + abs(noise + E)**2)

    return w_max * w_behav
