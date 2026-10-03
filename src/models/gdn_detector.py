"""
Graph Deviation Network (GDN) anomaly detector for KO-3201.

Adapted from Deng & Hooi, AAAI 2021 (arXiv:2106.06947, github.com/d-ailin/GDN):
  - one learnable embedding per sensor node
  - graph attention over the sensor graph (here: the fixed P&ID topology from config)
  - MLP head forecasts each sensor's next value from its last `win` values
  - deviation score a_i = (|err_i| - median_i) / IQR_i, system score A = max_i a_i
Differences from the original: the graph is the P&ID instead of a learned top-k
similarity graph, and attention is a dense masked softmax (6 nodes) instead of PyG GraphLayer.
"""

import json
import random
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.stats import iqr
from sklearn.preprocessing import MinMaxScaler

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "equipment_config.json"
DEFAULT_WEIGHTS = Path(__file__).resolve().parents[2] / "data" / "processed" / "gdn_ko3201_weights.pt"

SENSOR_NODES = ["PLANT_RATE", "KO3201_FEED", "KO3201_DISP", "KO3201_AMP", "KO3201_TEMP", "KO3201_VIB"]
SEED = 42


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_edge_index(edges: List[List[str]], nodes: List[str] = SENSOR_NODES) -> torch.Tensor:
    tag_to_idx = {tag: i for i, tag in enumerate(nodes)}
    return torch.tensor([[tag_to_idx[u], tag_to_idx[v]] for u, v in edges], dtype=torch.long).t().contiguous()


class GDNModel(nn.Module):
    """Dense graph attention over the P&ID (6 nodes) + MLP forecast head.

    Dense masked attention replaces torch_geometric GATConv: GATConv returned different
    outputs for identical inputs in this environment, which breaks reproducible demos.
    """

    def __init__(self, n_nodes: int, win: int, edge_index: torch.Tensor, dim: int = 16):
        super().__init__()
        adj = torch.eye(n_nodes, dtype=torch.bool)  # self loops
        adj[edge_index[1], edge_index[0]] = True  # adj[target, source]
        self.register_buffer("adj", adj)
        self.embedding = nn.Embedding(n_nodes, dim)
        self.proj = nn.Linear(win, dim)
        self.att_dst = nn.Linear(dim, 1, bias=False)
        self.att_src = nn.Linear(dim, 1, bias=False)
        self.bn = nn.BatchNorm1d(dim)
        self.out = nn.Sequential(nn.Linear(dim, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, N, win) -> (B, N) next-step forecast."""
        b, n, _ = x.shape
        emb = self.embedding.weight  # (N, dim)
        h = self.proj(x)  # (B, N, dim)
        g = h + emb  # sensor identity enters the attention, as in GDN
        logits = torch.nn.functional.leaky_relu(self.att_dst(g) + self.att_src(g).transpose(1, 2), 0.2)  # (B, target, source)
        alpha = torch.softmax(logits.masked_fill(~self.adj, float("-inf")), dim=-1)
        z = alpha @ h  # (B, N, dim)
        z = torch.relu(self.bn(z.reshape(b * n, -1))).view(b, n, -1) * emb
        return self.out(z).squeeze(-1)


class GDNDetector:
    def __init__(self, config_path: Optional[str] = None, equipment_tag: str = "KO-3201",
                 win: int = 5, persistence: int = 2, startup_mask_hours: int = 2):
        set_seed()
        with open(config_path or DEFAULT_CONFIG, encoding="utf-8") as f:
            topo = json.load(f)[equipment_tag]["pid_topology"]
        self.nodes = topo["nodes"]
        self.edge_index = build_edge_index(topo["edges"], self.nodes)
        self.win = win
        self.persistence = persistence
        self.startup_mask_hours = startup_mask_hours
        self.model = GDNModel(len(self.nodes), win, self.edge_index)
        self.scaler = MinMaxScaler()
        self.median = self.iqr = None
        self.tau: Optional[float] = None
        self.last_scores: Optional[pd.DataFrame] = None

    # ---- windows ----
    def _windows(self, scaled: np.ndarray):
        """Return X (T-win, N, win) and y (T-win, N): window t-win..t-1 predicts row t."""
        idx = np.arange(self.win, len(scaled))
        x = np.stack([scaled[i - self.win:i].T for i in idx]) if len(idx) else np.empty((0, scaled.shape[1], self.win))
        return torch.tensor(x, dtype=torch.float32), torch.tensor(scaled[idx], dtype=torch.float32)

    def _forecast_errors(self, scaled: np.ndarray) -> np.ndarray:
        x, y = self._windows(scaled)
        self.model.eval()
        with torch.no_grad():
            return (self.model(x) - y).abs().numpy()

    def _system_score(self, err: np.ndarray):
        a = (err - self.median) / (self.iqr + 1e-6)
        return a, a.max(axis=1)

    # ---- training ----
    def fit(self, train_df: pd.DataFrame, epochs: int = 30, lr: float = 5e-3, batch_size: int = 64,
            weights_path: Optional[Path] = DEFAULT_WEIGHTS) -> List[float]:
        set_seed()
        scaled = self.scaler.fit_transform(train_df[self.nodes].values)
        x, y = self._windows(scaled)
        opt = torch.optim.Adam(self.model.parameters(), lr=lr)
        losses = []
        for _ in range(epochs):
            self.model.train()
            perm = torch.randperm(len(x))
            total = 0.0
            for i in range(0, len(x), batch_size):
                b = perm[i:i + batch_size]
                if len(b) < 2:  # BatchNorm needs more than one sample
                    continue
                opt.zero_grad()
                loss = nn.functional.mse_loss(self.model(x[b]), y[b])
                loss.backward()
                opt.step()
                total += loss.item() * len(b)
            losses.append(total / len(x))

        err = self._forecast_errors(scaled)
        self.median = np.median(err, axis=0)
        self.iqr = iqr(err, axis=0)
        _, score = self._system_score(err)
        self.tau = float(np.percentile(score, 99.5))
        if weights_path:
            Path(weights_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save({"state_dict": self.model.state_dict(), "tau": self.tau,
                        "median": self.median, "iqr": self.iqr}, weights_path)
        return losses

    # ---- inference ----
    def detect(self, test_df: pd.DataFrame) -> pd.DataFrame:
        """Return df indexed like test_df with A(t) (`anomaly_score`), `raw_exceed`, `is_anomaly`, `a_<node>`.

        is_anomaly = score > tau for `persistence` consecutive hours, excluding offline
        rows and the first `startup_mask_hours` after a RUN_STATUS 0 -> 1 restart.
        """
        scaled = self.scaler.transform(test_df[self.nodes].values)
        a, score = self._system_score(self._forecast_errors(scaled))

        n = len(test_df)
        scores = np.full(n, np.nan)
        scores[self.win:] = score
        per_node = np.full((n, len(self.nodes)), np.nan)
        per_node[self.win:] = a

        run = test_df["RUN_STATUS"].values if "RUN_STATUS" in test_df else np.ones(n)
        valid = run == 1
        # startup mask: hours since the last offline row, within the mask window
        offline_age = np.full(n, np.inf)
        last_off = -np.inf
        for i in range(n):
            if run[i] == 0:
                last_off = i
            offline_age[i] = i - last_off
        # windows still containing offline rows are contaminated, so mask for at least `win` hours
        valid &= offline_age > max(self.startup_mask_hours, self.win)

        raw = (np.nan_to_num(scores, nan=-np.inf) > self.tau) & valid
        persisted = pd.Series(raw).rolling(self.persistence).min().fillna(0).astype(bool).values

        out = pd.DataFrame({"anomaly_score": scores, "raw_exceed": raw, "is_anomaly": persisted}, index=test_df.index)
        for j, tag in enumerate(self.nodes):
            out[f"a_{tag}"] = per_node[:, j]
        self.last_scores = out
        return out

    def predict_step(self, current_row, history_window_df: pd.DataFrame) -> dict:
        """Streaming interface: score one new row given the preceding rows (needs >= win rows)."""
        keep = self.win + self.persistence + self.startup_mask_hours
        df = pd.concat([history_window_df.tail(keep), pd.DataFrame([dict(current_row)])], ignore_index=True)
        last = self.detect(df).iloc[-1]
        return {"anomaly_score": last["anomaly_score"], "is_anomaly": bool(last["is_anomaly"]),
                "top_contributors": self.get_top_contributors(len(df) - 1)}

    def get_top_contributors(self, row_index: int, top_k: int = 2) -> List[tuple]:
        """Top-k (node, a_i) for a row of the last detect() result (positional index)."""
        row = self.last_scores.iloc[row_index][[f"a_{t}" for t in self.nodes]].dropna()
        top = row.sort_values(ascending=False).head(top_k)
        return [(k[2:], float(v)) for k, v in top.items()]
