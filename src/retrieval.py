from pathlib import Path
import numpy as np
import faiss


class FaissStore:
    def __init__(self, index_path: Path, mapping_path: Path):
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.index = None
        self.mapping = []

    def create_or_load(self, dim: int) -> None:
        if self.index_path.exists() and self.mapping_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.mapping = np.load(self.mapping_path, allow_pickle=True).tolist()
        else:
            self.index = faiss.IndexFlatIP(dim)
            self.mapping = []

    def add_vector(self, vector: np.ndarray, image_db_id: int) -> None:
        vector = vector.reshape(1, -1).astype("float32")
        self.index.add(vector)
        self.mapping.append(image_db_id)

    def save(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        np.save(self.mapping_path, np.array(self.mapping, dtype=object))

    def search(self, query_vector: np.ndarray, k: int = 5):
        query_vector = query_vector.reshape(1, -1).astype("float32")
        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "image_db_id": self.mapping[idx],
            })
        return results