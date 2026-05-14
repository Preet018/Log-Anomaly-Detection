"""
data_loader.py
--------------
Downloads the NSL-KDD dataset and splits it into two permanent files:

  KDDTrain_initial.txt  (70%) — used for the very first model training
  KDDRetrain_reserve.txt (30%) — held back, used ONLY when drift triggers retraining

This simulates real-world "new labelled data arriving" when the model is retrained.
"""

import os
import pandas as pd
import requests
from sklearn.model_selection import train_test_split

TRAIN_URL = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain+.txt"
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data_storage")

INITIAL_PATH = os.path.join(DATA_DIR, "KDDTrain_initial.txt")
RESERVE_PATH = os.path.join(DATA_DIR, "KDDRetrain_reserve.txt")
RAW_PATH     = os.path.join(DATA_DIR, "KDDTrain+.txt")

COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty_level"
]


def _download(url: str, filepath: str):
    if not os.path.exists(filepath):
        print(f"Downloading {url}...")
        r = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(r.content)
    else:
        print(f"File {filepath} already exists.")


def _split_and_save(raw_path: str):
    """
    Splits the full KDDTrain+.txt 70/30 into initial and reserve files.
    Only runs once — skips if both split files already exist.
    """
    if os.path.exists(INITIAL_PATH) and os.path.exists(RESERVE_PATH):
        return  # Already split

    print("Splitting KDDTrain+.txt → KDDTrain_initial.txt (70%) + KDDRetrain_reserve.txt (30%)...")
    df = pd.read_csv(raw_path, names=COLUMNS)
    df_initial, df_reserve = train_test_split(df, test_size=0.30, random_state=42)

    df_initial.to_csv(INITIAL_PATH, header=False, index=False)
    df_reserve.to_csv(RESERVE_PATH, header=False, index=False)
    print(f"  Initial set : {len(df_initial):,} rows → {INITIAL_PATH}")
    print(f"  Reserve set : {len(df_reserve):,} rows → {RESERVE_PATH}")


def load_data():
    """
    Used by ml_pipeline/main.py for INITIAL training.
    Loads KDDTrain_initial.txt (70% of the full dataset).
    Returns (df_train, df_test) split 80/20 within the initial set.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    _download(TRAIN_URL, RAW_PATH)
    _split_and_save(RAW_PATH)

    print("Loading initial training data (70% split)...")
    df = pd.read_csv(INITIAL_PATH, names=COLUMNS)
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    return df_train, df_test


def load_retrain_data():
    """
    Used by ml_pipeline/retrain.py for DRIFT-TRIGGERED retraining.
    Combines initial (70%) + reserve (30%) = full dataset.
    The model now sees data it was never trained on — simulating new labelled samples.
    Returns (df_train, df_test) split 80/20 within the combined set.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    _download(TRAIN_URL, RAW_PATH)
    _split_and_save(RAW_PATH)

    print("Loading combined data for retraining (initial 70% + reserve 30%)...")
    df_initial = pd.read_csv(INITIAL_PATH, names=COLUMNS)
    df_reserve = pd.read_csv(RESERVE_PATH, names=COLUMNS)
    df_combined = pd.concat([df_initial, df_reserve], ignore_index=True)
    print(f"  Combined size: {len(df_combined):,} rows")
    df_train, df_test = train_test_split(df_combined, test_size=0.2, random_state=42)
    return df_train, df_test
