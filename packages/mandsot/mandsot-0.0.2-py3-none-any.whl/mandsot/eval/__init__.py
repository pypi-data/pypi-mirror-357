import torch
from torch import nn
from tqdm import tqdm
import pandas as pd


def evaluate(model, data_loader, device):
    model.eval()
    criterion = nn.MSELoss()

    total_loss = 0.0
    total_mae = 0.0
    total_mse = 0.0
    total_samples = 0

    with torch.no_grad():
        for inputs, targets, initial in data_loader:
            inputs, targets, initial = inputs.float().to(device), targets.float().to(device), initial.long().to(device)
            outputs = model(inputs, initial)
            loss = criterion(outputs.squeeze(), targets.squeeze())

            mae = torch.abs(outputs.squeeze() - targets.squeeze()).mean()
            mse = ((outputs.squeeze() - targets.squeeze()) ** 2).mean()

            total_loss += loss.item()
            total_mae += mae.item()
            total_mse += mse.item()
            total_samples += len(inputs)

    avg_loss = total_loss / total_samples
    avg_mae = total_mae / total_samples
    avg_mse = total_mse / total_samples

    return avg_loss, avg_mae, avg_mse


def predict(model, data_loader, device):
    model.eval()
    all_paths = []
    all_preds = []

    with torch.no_grad():
        for batch in tqdm(data_loader, desc="Predicting"):
            inputs, paths = batch  # assume batch returns (input_tensor, path_list)
            inputs = inputs.float().to(device)  # [B, 80, T]
            if inputs.ndim == 3:
                B, _, T = inputs.shape
                initial = torch.zeros(B).long().to(device)  # initials is not needed for now
            else:
                raise ValueError("Unexpected input shape.")

            outputs = model(inputs, initial)  # [B]
            preds = outputs.cpu().numpy()
            hop_length = 128
            sr = 48000
            preds = preds * hop_length / sr * 1000  # to ms

            all_paths.extend(paths)
            all_preds.extend(preds)

    return pd.DataFrame({
        "location": all_paths,
        "onset": all_preds
    })

