from config import DB_PATH
from database import update_image_label

# Itt kézzel állítsd be a rekordokat
LABELS = [
    (1, "OK", None),
    (2, "OK", None),
    (3, "NOK", "date_error"),
]

def main():
    for row_id, label, defect_type in LABELS:
        update_image_label(DB_PATH, row_id, label, defect_type)
        print(f"Frissítve: id={row_id}, label={label}, defect_type={defect_type}")

if __name__ == "__main__":
    main()