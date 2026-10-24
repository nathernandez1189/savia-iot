"""Reenvía la historia local a una instancia InfluxDB nueva.

Las filas conservan su timestamp y boot/seq, por lo que repetir el proceso es seguro.
"""

import os
import sqlite3

from collector import FIELDS, send_influx

database = os.path.join(os.getenv("DATA_DIR", "/data"), "outbox.sqlite3")
with sqlite3.connect(database) as db:
    rows = db.execute("SELECT " + ",".join(FIELDS) + " FROM readings ORDER BY received_at_ms").fetchall()
for values in rows:
    send_influx(dict(zip(FIELDS, values)))
print(f"Histórico reenviado a InfluxDB: {len(rows)} lecturas")
