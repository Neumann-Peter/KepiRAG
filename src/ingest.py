from datetime import datetime
from pathlib import Path

from PIL import Image

from config import (
    ensure_directories,
    RAW_DIR,
    DATE_ROI_DIR,
    BARCODE_ROI_DIR,
    SEAL_ROI_DIR,
    DB_PATH,
    INDEX_CONFIGS,
    DATE_ROI,
    BARCODE_ROI,
    SEAL_ROI,
    SUPPORTED_EXTENSIONS,
)
from preprocessing import (
    load_image,
    crop_roi,
    save_image,
    bgr_to_rgb,
    ensure_non_empty_roi,
)
from embeddings import EmbeddingModel
from database import init_db, insert_image_record
from retrieval import FaissStore


def create_pil_from_bgr(image_bgr):
    rgb = bgr_to_rgb(image_bgr)
    return Image.fromarray(rgb)


def main():
    ensure_directories()
    init_db(DB_PATH)

    model = EmbeddingModel()
    stores = {}

    image_files = [
        p for p in RAW_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not image_files:
        print("Nincs feldolgozható kép a data/raw mappában.")
        return

    for image_path in image_files:
        print(f"Feldolgozás: {image_path.name}")

        image = load_image(image_path)

        roi_date = crop_roi(image, DATE_ROI)
        roi_barcode = crop_roi(image, BARCODE_ROI)
        roi_seal = crop_roi(image, SEAL_ROI)

        ensure_non_empty_roi(roi_date, "date")
        ensure_non_empty_roi(roi_barcode, "barcode")
        ensure_non_empty_roi(roi_seal, "seal")

        date_path = DATE_ROI_DIR / f"{image_path.stem}_date.png"
        barcode_path = BARCODE_ROI_DIR / f"{image_path.stem}_barcode.png"
        seal_path = SEAL_ROI_DIR / f"{image_path.stem}_seal.png"

        save_image(roi_date, date_path)
        save_image(roi_barcode, barcode_path)
        save_image(roi_seal, seal_path)

        full_embedding = model.image_to_embedding(create_pil_from_bgr(image))
        date_embedding = model.image_to_embedding(create_pil_from_bgr(roi_date))
        barcode_embedding = model.image_to_embedding(create_pil_from_bgr(roi_barcode))
        seal_embedding = model.image_to_embedding(create_pil_from_bgr(roi_seal))

        if not stores:
            stores = {
                "full": FaissStore(
                    INDEX_CONFIGS["full"]["index_path"],
                    INDEX_CONFIGS["full"]["mapping_path"],
                ),
                "date": FaissStore(
                    INDEX_CONFIGS["date"]["index_path"],
                    INDEX_CONFIGS["date"]["mapping_path"],
                ),
                "barcode": FaissStore(
                    INDEX_CONFIGS["barcode"]["index_path"],
                    INDEX_CONFIGS["barcode"]["mapping_path"],
                ),
                "seal": FaissStore(
                    INDEX_CONFIGS["seal"]["index_path"],
                    INDEX_CONFIGS["seal"]["mapping_path"],
                ),
            }

            stores["full"].create_or_load(dim=full_embedding.shape[0])
            stores["date"].create_or_load(dim=date_embedding.shape[0])
            stores["barcode"].create_or_load(dim=barcode_embedding.shape[0])
            stores["seal"].create_or_load(dim=seal_embedding.shape[0])

        row_id = insert_image_record(
            db_path=DB_PATH,
            filename=image_path.name,
            full_path=str(image_path),
            roi_date_path=str(date_path),
            roi_barcode_path=str(barcode_path),
            roi_seal_path=str(seal_path),
            label=None,
            defect_type=None,
            note=None,
            created_at=datetime.now().isoformat(),
        )

        stores["full"].add_vector(full_embedding, row_id)
        stores["date"].add_vector(date_embedding, row_id)
        stores["barcode"].add_vector(barcode_embedding, row_id)
        stores["seal"].add_vector(seal_embedding, row_id)

    for store in stores.values():
        store.save()

    print("Kész.")


if __name__ == "__main__":
    main()