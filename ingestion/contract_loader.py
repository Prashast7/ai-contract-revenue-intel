import os
from typing import List, Dict
from PyPDF2 import PdfReader


def load_contracts(contracts_dir: str) -> List[Dict]:
    """
    Loads all PDF contracts from a directory and extracts text.
    """
    contracts = []

    for file_name in os.listdir(contracts_dir):
        if not file_name.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(contracts_dir, file_name)
        reader = PdfReader(file_path)

        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        contracts.append(
            {
                "contract_id": file_name.replace(".pdf", ""),
                "text": full_text.strip()
            }
        )

    return contracts
