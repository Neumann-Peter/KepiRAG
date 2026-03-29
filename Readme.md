\# Program indítása Windows alatt



1\. Virtuális környezet létrehozása és aktiválása



`python -m venv .venv`

`.venv\\Scripts\\activate`



2\. Függőségek telepítése



`pip install --upgrade pip`

`pip install -r requirements.txt`



3\. Képek bemásolása



A feldolgozandó képeket a `data/raw/` mappába kell tenni.



4\. Az adatbázis és indexek felépítése



`python src/ingest.py`



Ez létrehozza a ROI képeket, az SQLite adatbázist és a FAISS indexeket.



5\. Hasonló képek keresése



Példa:



`python src/query\_similar.py data/raw/becsi\_felvagott.png`



6\. Címkék frissítése



`python src/label\_data.py`



7\. Újraépítés szükség esetén



`Remove-Item db\\metadata.db -ErrorAction SilentlyContinue`

`Remove-Item index\\\*.index -ErrorAction SilentlyContinue`

`Remove-Item index\\\*\_mapping.npy -ErrorAction SilentlyContinue`

`python src/ingest.py`



