import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Calibration:
    def __init__(
        self,
        loss_matrix: pd.DataFrame,
        weights: np.ndarray,
        targets: np.ndarray,
        epochs: Optional[int] = 32,
        noise_level: Optional[float] = 10.0,
        learning_rate: Optional[float] = 1e-3,
        dropout_rate: Optional[float] = 0.1,
        subsample_every: Optional[int] = 50,
        csv_path: Optional[str] = None,
    ):
        """Initialize the Calibration class.

        Args:
            loss_matrix (pd.DataFrame): DataFrame containing the loss matrix.
            weights (np.ndarray): Array of original weights.
            targets (np.ndarray): Array of target values.
            epochs (int): Optional number of epochs for calibration. Defaults to 32.
            noise_level (float): Optional level of noise to add to weights. Defaults to 10.0.
            learning_rate (float): Optional learning rate for the optimizer. Defaults to 1e-3.
            dropout_rate (float): Optional probability of dropping weights during training. Defaults to 0.1.
            subsample_every (int): Optional frequency of subsampling during training. Defaults to 50.
            csv_path (str): Optional path to save performance logs as CSV. Defaults to None.
        """

        self.loss_matrix = loss_matrix
        self.weights = weights
        self.targets = targets
        self.epochs = epochs
        self.noise_level = noise_level
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.subsample_every = subsample_every
        self.csv_path = csv_path
        self.performance_df = None

    def calibrate(self) -> None:
        """Calibrate the weights based on the loss matrix and targets."""
        target_names = np.array(self.loss_matrix.columns)

        self._assess_targets(
            loss_matrix=self.loss_matrix,
            weights=self.weights,
            targets=self.targets,
            target_names=target_names,
        )

        from .reweight import reweight

        new_weights, subsample, self.performance_df = reweight(
            original_weights=self.weights,
            loss_matrix=self.loss_matrix,
            targets_array=self.targets,
            epochs=self.epochs,
            noise_level=self.noise_level,
            learning_rate=self.learning_rate,
            dropout_rate=self.dropout_rate,
            subsample_every=self.subsample_every,
            csv_path=self.csv_path,
        )

        self.loss_matrix = self.loss_matrix.loc[subsample]
        self.weights = new_weights

        return self.performance_df

    def _assess_targets(
        self,
        loss_matrix: pd.DataFrame,
        weights: np.ndarray,
        targets: np.ndarray,
        target_names: Optional[np.ndarray] = None,
    ) -> None:
        """Assess the targets to ensure they do not violate basic requirements like compatibility, correct order of magnitude, etc.

        Args:
            loss_matrix (pd.DataFrame): DataFrame containing the loss matrix.
            weights (np.ndarray): Array of original weights.
            targets (np.ndarray): Array of target values.
            target_names (np.ndarray): Optional names of the targets for logging. Defaults to None.

        Raises:
            ValueError: If the targets do not match the expected format or values.
            ValueError: If the targets are not compatible with each other.
        """
        logger.info("Performing basic target assessment...")

        if targets.ndim != 1:
            raise ValueError("Targets must be a 1D NumPy array.")
        if len(targets) != loss_matrix.shape[1]:
            raise ValueError(
                f"Mismatch: {len(targets)} targets given, but loss_matrix has {loss_matrix.shape[1]} columns."
            )
        if np.any(np.isnan(targets)):
            raise ValueError("Targets contain NaN values.")

        if np.any(targets < 0):
            logger.warning(
                "Some targets are negative. This may not make sense for totals."
            )

        # Estimate order of magnitude from column sums and warn if they are off by an order of magnitude from targets
        estimates = (
            np.ones((1, loss_matrix.shape[0])) @ loss_matrix.values
        ).flatten()
        # Use a small epsilon to avoid division by zero
        eps = 1e-4
        adjusted_estimates = np.where(estimates == 0, eps, estimates)
        ratios = targets / adjusted_estimates

        for i, (target_val, estimate_val, ratio) in enumerate(
            zip(targets, estimates, ratios)
        ):
            if estimate_val == 0:
                logger.warning(
                    f"Column {target_names[i]} has a zero estimate sum; using ε={eps} for comparison."
                )

            order_diff = np.log10(abs(ratio)) if ratio != 0 else np.inf
            if order_diff > 1:
                logger.warning(
                    f"Target {target_names[i]} ({target_val:.2e}) differs from initial estimate ({estimate_val:.2e}) "
                    f"by {order_diff:.2f} orders of magnitude."
                )

            contributing_mask = loss_matrix.iloc[:, i] != 0
            contribution_ratio = contributing_mask.sum() / loss_matrix.shape[0]
            if contribution_ratio < 0.01:
                logger.warning(
                    f"Target {target_names[i]} is supported by only {contribution_ratio:.2%} "
                    f"of records in the loss matrix. This may make calibration unstable or ineffective."
                )

    def summary(
        self,
    ) -> str:
        """Generate a summary of the calibration process."""
        if self.performance_df is None:
            return "No calibration has been performed yet, make sure to run .calibrate() before requesting a summary."

        last_epoch = self.performance_df["epoch"].max()
        final_rows = self.performance_df[
            self.performance_df["epoch"] == last_epoch
        ]

        df = final_rows[["target_name", "target", "estimate"]].copy()
        df.rename(
            columns={
                "target_name": "Metric",
                "target": "Official target",
                "estimate": "Final estimate",
            },
            inplace=True,
        )
        df["Relative error"] = (
            df["Final estimate"] - df["Official target"]
        ) / df["Official target"]
        df = df.reset_index(drop=True)
        return df
