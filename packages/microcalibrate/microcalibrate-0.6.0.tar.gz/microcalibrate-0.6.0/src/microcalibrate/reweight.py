import logging
import os
from typing import Optional

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

from .utils.log_performance import log_performance_over_epochs
from .utils.metrics import loss, pct_close

logger = logging.getLogger(__name__)

# Add device variable to use gpu (incl mps) if available
device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)


def reweight(
    original_weights: np.ndarray,
    loss_matrix: pd.DataFrame,
    targets_array: np.ndarray,
    dropout_rate: Optional[float] = 0.1,
    epochs: Optional[int] = 2_000,
    noise_level: Optional[float] = 10.0,
    subsample_every: Optional[int] = 50,
    learning_rate: Optional[float] = 1e-3,
    csv_path: Optional[str] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Reweight the original weights based on the loss matrix and targets.

    Args:
        original_weights (np.ndarray): Original weights to be reweighted.
        loss_matrix (pd.DataFrame): DataFrame containing the loss matrix.
        targets_array (np.ndarray): Array of target values.
        dropout_rate (float): Optional probability of dropping weights during training.
        epochs (int): Optional number of epochs for training.
        noise_level (float): Optional level of noise to add to the original weights.
        subsample_every (int): Optional frequency of subsampling during training.
        learning_rate (float): Optional learning rate for the optimizer.

    Returns:
        np.ndarray: Reweighted weights.
        original_indices (np.ndarray): Indices of the original weights that were kept after subsampling.
        performance_df (pd.DataFrame): DataFrame containing the performance metrics over epochs.
    """
    if csv_path is not None and not csv_path.endswith(".csv"):
        raise ValueError("csv_path must be a string ending with .csv")

    target_names = np.array(loss_matrix.columns)

    logger.info(
        f"Starting calibration process for targets {target_names}: {targets_array}"
    )
    logger.info(
        f"Original weights - mean: {original_weights.mean():.4f}, "
        f"std: {original_weights.std():.4f}"
    )

    loss_matrix = torch.tensor(
        loss_matrix.values, dtype=torch.float32, device=device
    )
    original_indices = np.arange(loss_matrix.shape[0])

    targets = torch.tensor(targets_array, dtype=torch.float32, device=device)
    random_noise = np.random.random(original_weights.shape) * noise_level
    weights = torch.tensor(
        np.log(original_weights + random_noise),
        requires_grad=True,
        dtype=torch.float32,
        device=device,
    )

    logger.info(
        f"Initial weights after noise - mean: {torch.exp(weights).mean().item():.4f}, "
        f"std: {torch.exp(weights).std():.4f}"
    )

    def dropout_weights(weights: torch.Tensor, p: float) -> torch.Tensor:
        """Apply dropout to the weights.

        Args:
            weights (torch.Tensor): Current weights in log space.
            p (float): Probability of dropping weights.

        Returns:
            torch.Tensor: Weights after applying dropout.
        """
        if p == 0:
            return weights
        total_weight = weights.sum()
        mask = torch.rand_like(weights) < p
        masked_weights = weights.clone()
        masked_weights[mask] = 0
        masked_weights = masked_weights / masked_weights.sum() * total_weight
        return masked_weights

    optimizer = torch.optim.Adam([weights], lr=learning_rate)

    iterator = tqdm(range(epochs), desc="Reweighting progress", unit="epoch")

    loss_over_epochs = []
    estimates_over_epochs = []
    pct_close_over_epochs = []
    epochs = []

    tracking_n = 10  # Track every 10th epoch
    for i in iterator:
        optimizer.zero_grad()
        running_loss = None
        for j in range(2):
            weights_ = dropout_weights(weights, dropout_rate)
            estimate = torch.exp(weights_) @ loss_matrix
            l = loss(estimate, targets)
            close = pct_close(estimate, targets)
            if running_loss is None:
                running_loss = l
            else:
                running_loss += l

        l = running_loss / 2

        if i % tracking_n == 0:
            epochs.append(i)
            loss_over_epochs.append(l.item())
            pct_close_over_epochs.append(close)
            estimates_over_epochs.append(estimate.detach().cpu().numpy())

            iterator.set_postfix(
                {
                    "loss": l.item(),
                    "count_observations": loss_matrix.shape[0],
                    "weights_mean": torch.exp(weights).mean().item(),
                    "weights_std": torch.exp(weights).std().item(),
                    "weights_min": torch.exp(weights).min().item(),
                }
            )

            logger.info(f"Within 10% from targets: {close:.2%} \n")

            if len(loss_over_epochs) > 1:
                loss_change = loss_over_epochs[-2] - l.item()
                logger.info(
                    f"Epoch {i:4d}: Loss = {l.item():.6f}, "
                    f"Change = {loss_change:.6f} "
                    f"({'improving' if loss_change > 0 else 'worsening'})"
                )

        l.backward()
        optimizer.step()

        if subsample_every > 0 and i % subsample_every == 0 and i > 0:
            weight_values = np.exp(weights.detach().cpu().numpy())

            k = 100
            # indices = indices of weights with values < 1
            indices = np.where(weight_values >= k)[0]
            loss_matrix = loss_matrix[indices, :]
            weights = weights[indices]

            logger.info(
                f"Epoch {i}: Subsampling - kept {len(indices)} observations, "
                f"removed {original_indices - len(indices)} (weights < {k})"
            )

            loss_matrix = torch.tensor(
                loss_matrix.detach().cpu(), dtype=torch.float32, device=device
            )
            weights = torch.tensor(
                weights.detach().cpu(),
                dtype=torch.float32,
                device=device,
                requires_grad=True,
            )

            original_indices = original_indices[indices]
            optimizer = torch.optim.Adam([weights], lr=learning_rate)

    tracker_dict = {
        "epochs": epochs,
        "loss": loss_over_epochs,
        "estimates": estimates_over_epochs,
    }

    performance_df = log_performance_over_epochs(
        tracker_dict, targets, target_names
    )

    if csv_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        performance_df.to_csv(csv_path, index=True)

    logger.info(f"Reweighting completed. Final sample size: {len(weights)}")

    final_weights = torch.exp(weights).detach().cpu().numpy()

    return (
        final_weights,
        original_indices,
        performance_df,
    )
