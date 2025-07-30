import matplotlib.cm as cm
import numpy as np
import pandas as pd

from .physical_factor import PhysicalFactor
from .physical_stimuli_profile import StimuliProfile
from collections.abc import  Callable
from itertools import repeat
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from os import PathLike
from rich import print
from typing import List, cast


class VerFishDModel:
    """
    A class representing a model that manages multiple PhysicalFactors.
    """

    name: str
    steps: pd.DataFrame
    result: pd.Series

    def __init__(
            self,
            name: str,
            stimuli_profile: StimuliProfile,
            migration_speed: Callable[[float], float],
            factors: list[PhysicalFactor]
    ):
        """
        A class representing a model that manages multiple PhysicalFactors.

        Parameters
        ----------
        stimuli_profile : pandas.DataFrame
            A dataframe with depth-specific physical stimuli information.
        migration_speed : Callable[[float], float]
            The migration speed function for the current model. For example:

            .. math::

                w_{fin} = w_{max} * w_{beh} = \\frac{{(\\zeta_d + E)|\\zeta_d + E|}}{{h + (\\zeta_d + E)^2}}

        factors : list of PhysicalFactor, optional
            A list of PhysicalFactor instances (optional).
        """
        self.name = name
        self.migration_speed = migration_speed
        self.__check_factors(factors, stimuli_profile)
        self.__init_steps()
        self.weighted_sum = self.__calculate_weighted_sum()

    def __init_steps(self):
        self.steps = pd.DataFrame(index=self.stimuli_profile.data.index)
        self.steps['t=0'] = 1.0

    def __check_factors(self, factors: list[PhysicalFactor], stimuli_profile: StimuliProfile):
        """
        Validate factors and initialize the stimuli profile.

        Parameters
        ----------
        factors : List[PhysicalFactor]
            A list of PhysicalFactor instances.
        stimuli_profile : StimuliProfile
            The stimuli profile containing relevant data.

        Raises
        ------
        TypeError
            If any element in 'factors' is not an instance of PhysicalFactor.
        ValueError
            If the factor names are not in the stimuli profile columns.
        ValueError
            If the sum of all factor weights is not equal to 1.
        """
        if not all(isinstance(factor, PhysicalFactor) for factor in factors):
            print("[red]All elements in 'factors' must be instances of PhysicalFactor.[/red]")
            raise TypeError("All elements in 'factors' must be instances of PhysicalFactor.")

        if not all(factor.name in stimuli_profile.columns for factor in factors):
            column_list = '\n'.join(stimuli_profile.columns.map('- {}'.format))
            print(f"[red]All factor names must be present in the stimuli profile columns.\nPresent columns:\n[bold]{column_list}[/bold][/red]")
            raise ValueError(f"All factor names must be present in the stimuli profile columns. Present columns: {stimuli_profile.columns}")

        total_weight = sum(factor.weight for factor in factors)
        if not abs(total_weight - 1.0) < 1e-6:  # floating point comparison
            print(f"[red]The sum of all factor weights must be 1.0, but got {total_weight:.6f}.[/red]")
            raise ValueError(f"The sum of all factor weights must be 1.0, but got {total_weight:.6f}.")

        self.factors = factors
        self.stimuli_profile = stimuli_profile

    def __calculate_weighted_sum(self):
        """
        Calculate the weighted sum of the factors for each depth.

        Returns
        -------
        pd.Series
            The weighted sum for each depth.
        """
        factor_influence = self.__calculate_factor_influence()
        weighted_sum = factor_influence.sum(axis=1)
        return weighted_sum

    def __calculate_factor_influence(self):
        """
        Calculate the influence of each factor on the weighted sum.

        Returns
        -------
        pd.DataFrame
            The influence of each factor on the weighted sum.
        """
        factor_influence = pd.DataFrame(index=self.stimuli_profile.data.index)

        for factor in self.factors:
            calc = np.vectorize(factor.calculate)
            # Use `display_name` here to simplify the plot legend
            factor_influence[factor.display_name] = calc(self.stimuli_profile.data[factor.name]) * factor.weight

        return factor_influence

    def simulate(self, number_of_steps: int = 1000):
        """
        Simulate the model for a given number of steps, continuing from the last recorded step.

        Parameters
        ----------
        number_of_steps: int, optional
            The number of steps to simulate the model for.
        """
        if not hasattr(self, 'steps') or self.steps.empty:
            raise ValueError("Simulation cannot continue without initial state.")

        # Determine starting point
        last_step_index = self.steps.shape[1] - 1
        steps_list = [self.steps.iloc[:, -1].copy()]

        # Precompute migration speeds for all depths
        migration_speeds = np.vectorize(self.migration_speed)(self.weighted_sum.values)

        for _ in repeat(None, number_of_steps):
            current = steps_list[-1]
            next_step = pd.Series(0.0, index=current.index)

            # Compute migration changes first
            migrated_up = np.zeros_like(current.values)
            migrated_down = np.zeros_like(current.values)

            up_mask = (migration_speeds > 0)
            down_mask = (migration_speeds < 0)

            migrated_values = np.abs(migration_speeds) * current.values

            migrated_up[:-1] += migrated_values[1:] * up_mask[1:]
            migrated_up[1:] -= migrated_values[1:] * up_mask[1:]

            migrated_down[1:] += migrated_values[:-1] * down_mask[:-1]
            migrated_down[:-1] -= migrated_values[:-1] * down_mask[:-1]

            # Apply migration
            next_step += current + migrated_up + migrated_down

            # Normalize total mass to conserve population
            total_current = next_step.sum()
            if total_current > 0:
                next_step *= current.sum() / total_current

            steps_list.append(next_step)

        # Append results to existing DataFrame
        new_steps = pd.concat(steps_list[1:], axis=1)
        new_steps.columns = [f"t={t}" for t in range(last_step_index + 1, last_step_index + number_of_steps + 1)]

        self.steps = pd.concat([self.steps, new_steps], axis=1)

        self.result = self.steps.iloc[:, -1]
        self.result.name = "Fish Probability"

    def plot(self) -> List[Axes]:
        """
        Plot the simulation results including the stimuli profile and evaluation function.
        """
        axs: List[ Axes ]


        _, axs = plt.subplots(1, 3, figsize=(12, 8), )

        # Plot Simulation Result
        self.plot_simulation_result(axs[0])

        # Plot Stimuli Profile
        self.plot_stimuli(axs[1])

        # Plot Evaluation Function
        self.plot_evaluation_function(axs[2])

        return axs

    def plot_simulation_result(self, ax: Axes | None = None) -> Axes | None:
        """
        Plot the simulation result.
        """
        if ax is None:
            ax = plt.gca()

        simulation_result = self.result
        points_for_plot = cast(pd.Series, simulation_result[simulation_result > 0.1])
        ax.plot(points_for_plot.to_numpy() ,points_for_plot.index, 'o', label='_nolegend_', data=points_for_plot, markersize=4)
        ax.plot(simulation_result.to_numpy(), simulation_result.index, label="Fish Probability")
        ax.set_ylabel("Depth")
        ax.set_xlabel("Fish Share")
        ax.invert_yaxis()
        ax.legend(loc="lower right")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.set_title("Vertical Fish Distribution")

        return ax


    def plot_stimuli(self, ax = None) -> Axes | None:
        """
        Plot the Stimuli Profile for the given Physical Factors
        """
        if ax is None:
            ax = plt.gca()
            ax.set_title("Stimuli Profile")
            ax.set_ylabel("Depth")

        lines = []
        for factor in self.factors:
            data = self.stimuli_profile.data[factor.name]

            # Todo: Refactor this into the PhysicalFactor class instead of hardcoding it here
            if factor.name == "light":
                ax2 = ax.twiny()
                line = ax2.plot(data, self.stimuli_profile.data.index, 'y--', label=factor.display_name, alpha=1)
                ax2.set_xlabel("Light")

                # Thresholds for the Light Factor -> Needs to go into the PhysicalFactor class
                thresholds = [200, 10, 0.01]

                # colour gradient from orange to yellow
                colors = cm.get_cmap("autumn")(np.linspace(0, 0.5, len(thresholds)))

                # First occurence of threshold values
                for i, threshold in enumerate(thresholds):
                    mask = data < threshold
                    if mask.any():
                        y_value = cast(float, self.stimuli_profile.data.index[mask.argmax()])
                        threshold_line = ax2.axhline(y=y_value, color=colors[i], linestyle=':', alpha=0.7, label=fr"$\theta_l={threshold}$")
                        line.append(threshold_line)

            else:
                line = ax.plot(data, self.stimuli_profile.data.index, linestyle="dashed", label=factor.display_name, alpha=1)

            lines.extend(line)


        ax.set_xlabel("Stimuli Value")
        ax.invert_yaxis()
        labs = [l.get_label() for l in lines]
        ax.legend(lines, labs, loc="lower right")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        return ax

    def plot_evaluation_function(self, ax: Axes | None = None) -> Axes | None:
        """
        Plot the evaluation function.
        """
        if ax is None:
            ax = plt.gca()
            ax.set_ylabel("Depth")

        factor_influence = self.__calculate_factor_influence()

        ax.plot(self.weighted_sum, self.weighted_sum.index, 'k-', linewidth=2, alpha=0.7, label="Evaluation Function (E)")
        [ax.plot(factor_influence[col], factor_influence.index, linestyle="dashed", marker="o", markersize="1.5", alpha=0.5, label=col) for col in factor_influence.columns]
        ax.set_title("Evaluation Function")
        ax.invert_yaxis()
        ax.set_xlabel("E")
        ax.legend(loc="lower right")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        return ax



    def save_result(self, file_path: str | PathLike[str] | None) -> None:
        """
        Save the simulation result to a file.

        Parameters
        ----------
        file_path: str
            The path to the file.
        """
        if file_path is None:
            self.result.to_csv(f"{self.name}_simulation_result.csv")
        else:
            self.result.to_csv(file_path)
