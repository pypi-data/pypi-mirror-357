import os
from pathlib import Path
import gdown



CACHED_CREDENTIAL_PATH = Path.home() / ".calicropyield" / "service_account.json"
GDRIVE_FILE_ID = "1yowEKSOTif1nCL_4yyLtE_DkqL2FgOdh"

def ensure_shared_credentials() -> Path:
    """
    Ensure that the shared service_account.json credential exists locally.
    If not, download it from a secure Google Drive location.
    Returns the path to the credential file.
    """
    if not CACHED_CREDENTIAL_PATH.exists():
        print(f"🔐 Credential not found. Downloading to {CACHED_CREDENTIAL_PATH}...")
        CACHED_CREDENTIAL_PATH.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
        try:
            gdown.download(url, str(CACHED_CREDENTIAL_PATH), quiet=False)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to download credentials: {e}")

        if not CACHED_CREDENTIAL_PATH.exists():
            raise FileNotFoundError("Credential download failed. File still missing.")

    return CACHED_CREDENTIAL_PATH