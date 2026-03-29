from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
ROI_DIR = DATA_DIR / "roi"
PROCESSED_DIR = DATA_DIR / "processed"

DATE_ROI_DIR = ROI_DIR / "date"
BARCODE_ROI_DIR = ROI_DIR / "barcode"
SEAL_ROI_DIR = ROI_DIR / "seal"

DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "metadata.db"

INDEX_DIR = BASE_DIR / "index"

INDEX_CONFIGS = {
    "full": {
        "index_path": INDEX_DIR / "full.index",
        "mapping_path": INDEX_DIR / "full_mapping.npy",
    },
    "date": {
        "index_path": INDEX_DIR / "date.index",
        "mapping_path": INDEX_DIR / "date_mapping.npy",
    },
    "barcode": {
        "index_path": INDEX_DIR / "barcode.index",
        "mapping_path": INDEX_DIR / "barcode_mapping.npy",
    },
    "seal": {
        "index_path": INDEX_DIR / "seal.index",
        "mapping_path": INDEX_DIR / "seal_mapping.npy",
    },
}

# Fix ROI-k (x, y, w, h)
DATE_ROI = (100, 50, 220, 90)
BARCODE_ROI = (300, 200, 260, 120)
SEAL_ROI = (50, 300, 500, 100)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def ensure_directories() -> None:
    for path in [
        RAW_DIR,
        DATE_ROI_DIR,
        BARCODE_ROI_DIR,
        SEAL_ROI_DIR,
        PROCESSED_DIR,
        DB_DIR,
        INDEX_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)