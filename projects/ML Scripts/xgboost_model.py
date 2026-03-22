import argparse
import os

import numpy as np
import pandas as pd
import xgboost as xgb


def _train_val_split(X, y, test_size=0.2, seed=42):
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be between 0 and 1.")
    n = X.shape[0]
    if n < 5:
        raise ValueError("Need at least 5 rows to train a model.")

    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    split = int(n * (1.0 - test_size))

    train_idx = idx[:split]
    val_idx = idx[split:]

    return X[train_idx], X[val_idx], y[train_idx], y[val_idx]


def train_xgboost(dataset_csv, model_out, test_size=0.2, seed=42):
    df = pd.read_csv(dataset_csv)
    if "win" not in df.columns:
        raise ValueError("Dataset must include a 'win' target column.")

    y = df["win"].astype(int).to_numpy()
    X = df.drop(columns=["win"]).to_numpy(dtype=float)

    X_train, X_val, y_train, y_val = _train_val_split(
        X, y, test_size=test_size, seed=seed
    )

    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)

    params = {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "max_depth": 5,
        "eta": 0.1,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "seed": seed,
    }

    evals = [(dtrain, "train"), (dval, "val")]
    model = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=300,
        evals=evals,
        early_stopping_rounds=25,
        verbose_eval=False,
    )

    preds = model.predict(dval)
    pred_labels = (preds >= 0.5).astype(int)
    accuracy = float((pred_labels == y_val).mean())

    os.makedirs(os.path.dirname(model_out) or ".", exist_ok=True)
    model.save_model(model_out)

    return {
        "rows": df.shape[0],
        "features": X.shape[1],
        "best_iteration": model.best_iteration,
        "val_accuracy": accuracy,
        "model_out": model_out,
    }


def main():
    parser = argparse.ArgumentParser(description="Train XGBoost model for match outcomes.")
    parser.add_argument(
        "--dataset",
        default="matches_dataset.csv",
        help="Path to dataset CSV produced by dataset_builder.py",
    )
    parser.add_argument(
        "--model-out",
        default="xgb_model.json",
        help="Output path for the trained model",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    results = train_xgboost(
        dataset_csv=args.dataset,
        model_out=args.model_out,
        test_size=args.test_size,
        seed=args.seed,
    )

    print("Training complete.")
    print("Rows:", results["rows"])
    print("Features:", results["features"])
    print("Best iteration:", results["best_iteration"])
    print("Validation accuracy:", f"{results['val_accuracy']:.4f}")
    print("Model saved to:", results["model_out"])


if __name__ == "__main__":
    main()
