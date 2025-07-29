from datetime import datetime
import os
from uuid import uuid4
import torch
from torch import nn
from torch import optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import matplotlib.pyplot as plt
from tqdm import tqdm
from mandsot import eval
import pandas as pd


class EarlyStopping:
    def __init__(self, patience=5, delta=0):
        self.patience = patience
        self.delta = delta
        self.best_score = None
        self.early_stop = False
        self.counter = 0

    def __call__(self, val_loss):
        score = -val_loss
        if self.best_score is None:
            self.best_score = score
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.counter = 0


def train(model, train_loader, device, optimizer):
    model.train()
    criterion = nn.MSELoss()

    train_loss = 0.0
    total_samples = 0

    for batch_idx, (inputs, targets, initial) in enumerate(train_loader):
        inputs, targets, initial = inputs.float().to(device), targets.float().to(device), initial.long().to(device)
        # print("input shape:", inputs.shape)
        optimizer.zero_grad()
        outputs = model(inputs, initial)
        loss = criterion(outputs.squeeze(), targets.squeeze())
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        total_samples += len(inputs)

    return train_loss / total_samples


def plot_learning_curve(train_losses, val_losses):
    plt.figure()
    plt.plot(range(1, len(train_losses) + 1), train_losses, label='Train Loss')
    plt.plot(range(1, len(val_losses) + 1), val_losses, label='Validation Loss')
    plt.title('Learning Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()


def analyze_model_performance(file_path):
    data = pd.read_csv(file_path)
    filtered_data = data[data['NO'] > data['NO'].max() * 0.5]
    validation_loss_mean = filtered_data['Validation Loss'].mean()
    validation_mae_mean = filtered_data['Validation MAE'].mean()
    suitable_models = filtered_data[(filtered_data['Validation Loss'] < validation_loss_mean) & (filtered_data['Validation MAE'] < validation_mae_mean)]
    best_models = suitable_models.sort_values(by=['Validation Loss', 'Validation MAE'])
    print("Top performing models:")
    print(best_models.head())


def start(model, train_loader, test_loader, device, lr, es, output, keep_all):
    print(f"\nTraining started.")

    # generate model weights dir
    unique_id = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_') + str(uuid4())
    weights_dir = os.path.join(output, 'model_weights')
    weights_out_dir = os.path.join(weights_dir, unique_id)
    if not os.path.exists(weights_out_dir):
        os.makedirs(weights_out_dir)

    # initialize
    epoch = 0
    all_metrics = []  # store metrics for model performance evaluation
    val_loss_min = float('inf')
    train_losses = []
    val_losses = []

    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    while not es.early_stop:
        train_loader_tqdm = tqdm(train_loader, desc=f"[{epoch + 1}]", total=len(train_loader), colour='GREEN')
        train_loss = train(model, train_loader_tqdm, device, optimizer)
        val_loss, val_mae, val_mse = eval.evaluate(model, test_loader, device)

        # model metrics
        print(f'[{epoch + 1}]: Train loss: {train_loss} | Validation Loss: {val_loss} | Validation MAE: {val_mae}')
        print(f"[{epoch + 1}]: Current learning rate: {optimizer.param_groups[0]['lr']}")
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        all_metrics.append({
            "NO": len(all_metrics) + 1,
            "Epoch": f"{epoch + 1}",
            "Train Loss": train_loss,
            "Validation Loss": val_loss,
            "Validation MAE": val_mae,
            "Validation MSE": val_mse
        })

        # adjust learning rate
        scheduler.step(val_loss)

        # save the best model
        if keep_all:
            torch.save(model.state_dict(), os.path.join(weights_out_dir, f'sot_epoch_{epoch + 1}_loss_{val_loss}.pth'))

        if val_loss < val_loss_min:
            val_loss_min = val_loss
            # torch.save(model.state_dict(), os.path.join(weights_out_dir, f'sot_best_epoch_{epoch + 1}_loss_{val_loss}.pth'))
            torch.save(model.state_dict(), os.path.join(weights_out_dir, f'sot_best.pth'))

        # check early stopping conditions
        es(val_loss)
        epoch += 1

    # task upon completion
    print(f"\nTrain complete.")
    plot_learning_curve(train_losses, val_losses)
    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv(os.path.join(weights_out_dir, 'training_metrics.csv'), index=False)
    analyze_model_performance(os.path.join(weights_out_dir, 'training_metrics.csv'))
