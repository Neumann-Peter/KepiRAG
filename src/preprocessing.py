from pathlib import Path
import cv2
import numpy as np


def load_image(image_path: Path) -> np.ndarray:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Nem sikerült beolvasni a képet: {image_path}")
    return image


def crop_roi(image: np.ndarray, roi: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = roi
    return image[y:y + h, x:x + w]


def save_image(image: np.ndarray, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(output_path), image)
    if not ok:
        raise IOError(f"Nem sikerült menteni a képet: {output_path}")


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def ensure_non_empty_roi(image: np.ndarray, roi_name: str) -> None:
    if image is None or image.size == 0:
        raise ValueError(f"Üres vagy érvénytelen ROI: {roi_name}")