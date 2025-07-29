# client.py
import argparse
import pandas as pd
import flwr as fl
import torch
import torch.nn as nn
import torch.optim as optim
from MEDfl.rw.model import Net  # your model definition in model.py

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, server_address: str, data_path: str = "data/data.csv"):
        self.server_address = server_address

        # 1. Load model
        self.model = Net()
        self.loss_fn = nn.MSELoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.01)

        # 2. Load data from CSV
        df = pd.read_csv(data_path)
        # Assume last column is label
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        self.X_train = torch.tensor(X, dtype=torch.float32)
        # If it's regression with single output; remove unsqueeze for multi-class
        self.y_train = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    def get_parameters(self, config):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train()
        for _ in range(5):
            self.optimizer.zero_grad()
            preds = self.model(self.X_train)
            loss = self.loss_fn(preds, self.y_train)
            loss.backward()
            self.optimizer.step()
        # Return updated params, number of examples, and an empty metrics dict
        return self.get_parameters(config), len(self.X_train), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        self.model.eval()
        with torch.no_grad():
            preds = self.model(self.X_train)
            loss = self.loss_fn(preds, self.y_train).item()
        return float(loss), len(self.X_train), {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flower client")
    parser.add_argument(
        "--server_address",
        type=str,
        required=True,
        help="Address of the Flower server (e.g., 127.0.0.1:8080)",
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="data/data.csv",
        help="Path to your CSV training data",
    )
    args = parser.parse_args()

    # Instantiate and start the client
    client = FlowerClient(server_address=args.server_address, data_path=args.data_path)
    fl.client.start_numpy_client(server_address=client.server_address, client=client)
