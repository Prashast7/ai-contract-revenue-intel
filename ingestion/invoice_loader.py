import pandas as pd
from pathlib import Path
from typing import List, Dict


def load_invoices(invoices_dir: Path) -> List[Dict]:
    invoices = []

    for file in invoices_dir.iterdir():
        if file.suffix.lower() != ".csv":
            continue

        df = pd.read_csv(file)
        invoices.extend(df.to_dict(orient="records"))

    return invoices
