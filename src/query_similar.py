import sys
from pathlib import Path

from PIL import Image

from config import (
    DB_PATH,
    INDEX_CONFIGS,
    DATE_ROI,
    BARCODE_ROI,
    SEAL_ROI,
)
from preprocessing import (
    load_image,
    bgr_to_rgb,
    crop_roi,
    ensure_non_empty_roi,
)
from embeddings import EmbeddingModel
from retrieval import FaissStore
from database import get_image_label_and_defect_by_id
from decision import summarize_labels, aggregate_decision


def create_pil_from_bgr(image_bgr):
    rgb = bgr_to_rgb(image_bgr)
    return Image.fromarray(rgb)


def load_store(name: str, dim: int) -> FaissStore:
    store = FaissStore(
        INDEX_CONFIGS[name]["index_path"],
        INDEX_CONFIGS[name]["mapping_path"],
    )
    store.create_or_load(dim=dim)
    return store


def attach_labels(results):
    enriched = []

    for result in results:
        row = get_image_label_and_defect_by_id(DB_PATH, result["image_db_id"])
        if row is None:
            enriched.append({
                "image_db_id": result["image_db_id"],
                "score": result["score"],
                "filename": None,
                "label": None,
                "defect_type": None,
            })
            continue

        record_id, filename, label, defect_type = row

        enriched.append({
            "image_db_id": record_id,
            "score": result["score"],
            "filename": filename,
            "label": label,
            "defect_type": defect_type,
        })

    return enriched


def print_channel_results(title, results_with_labels):
    print(f"\n--- {title} ---")
    for i, item in enumerate(results_with_labels, start=1):
        print(
            f"{i}. "
            f"score={item['score']:.4f} | "
            f"id={item['image_db_id']} | "
            f"fajl={item['filename']} | "
            f"label={item['label']} | "
            f"defect={item['defect_type']}"
        )


def main():
    if len(sys.argv) < 2:
        print("Használat: python src/query_similar.py data/raw/tesztkep.png")
        return

    query_path = Path(sys.argv[1])
    if not query_path.exists():
        print(f"A fájl nem létezik: {query_path}")
        return

    image = load_image(query_path)

    roi_date = crop_roi(image, DATE_ROI)
    roi_barcode = crop_roi(image, BARCODE_ROI)
    roi_seal = crop_roi(image, SEAL_ROI)

    ensure_non_empty_roi(roi_date, "date")
    ensure_non_empty_roi(roi_barcode, "barcode")
    ensure_non_empty_roi(roi_seal, "seal")

    model = EmbeddingModel()

    full_embedding = model.image_to_embedding(create_pil_from_bgr(image))
    date_embedding = model.image_to_embedding(create_pil_from_bgr(roi_date))
    barcode_embedding = model.image_to_embedding(create_pil_from_bgr(roi_barcode))
    seal_embedding = model.image_to_embedding(create_pil_from_bgr(roi_seal))

    full_store = load_store("full", full_embedding.shape[0])
    date_store = load_store("date", date_embedding.shape[0])
    barcode_store = load_store("barcode", barcode_embedding.shape[0])
    seal_store = load_store("seal", seal_embedding.shape[0])

    full_results = attach_labels(full_store.search(full_embedding, k=5))
    date_results = attach_labels(date_store.search(date_embedding, k=5))
    barcode_results = attach_labels(barcode_store.search(barcode_embedding, k=5))
    seal_results = attach_labels(seal_store.search(seal_embedding, k=5))

    print(f"\nLekérdezett kép: {query_path.name}")

    print_channel_results("TELJES KÉP", full_results)
    print_channel_results("DÁTUM ROI", date_results)
    print_channel_results("BARCODE ROI", barcode_results)
    print_channel_results("SEAL ROI", seal_results)

    channel_summaries = {
        "full": summarize_labels(full_results, top_k=3),
        "date": summarize_labels(date_results, top_k=3),
        "barcode": summarize_labels(barcode_results, top_k=3),
        "seal": summarize_labels(seal_results, top_k=3),
    }

    decision = aggregate_decision(channel_summaries)

    print("\n=== ÖSSZESÍTETT DÖNTÉS ===")
    print(f"Döntés: {decision['final_decision']}")
    print(f"Indoklás: {decision['reason']}")
    print(f"Szavazatok: {decision['votes']}")
    print(f"Statisztika: {decision['stats']}")


if __name__ == "__main__":
    main()