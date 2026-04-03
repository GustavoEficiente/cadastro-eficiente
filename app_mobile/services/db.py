import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "cadastro_eficiente_mobile.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            username TEXT,
            password TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS form_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cadastros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ponto TEXT NOT NULL,
            nome_cadastrador TEXT,
            data_cadastro TEXT,
            hora_cadastro TEXT,
            latitude TEXT,
            longitude TEXT,
            status_sincronizacao TEXT,
            dados_extras TEXT,
            fotos_json TEXT,
            synced INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()

    # garante coluna fotos_json caso já exista banco antigo
    try:
        cur.execute("ALTER TABLE cadastros ADD COLUMN fotos_json TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()


def save_user_session(base_url, username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_session")
    cur.execute(
        "INSERT INTO user_session (base_url, username, password) VALUES (?, ?, ?)",
        (base_url, username, password),
    )
    conn.commit()
    conn.close()


def get_user_session():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_session ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def clear_user_session():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_session")
    conn.commit()
    conn.close()


def save_form_config(payload):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM form_config")
    cur.execute(
        "INSERT INTO form_config (payload_json, updated_at) VALUES (?, datetime('now'))",
        (json.dumps(payload, ensure_ascii=False),),
    )
    conn.commit()
    conn.close()


def get_form_config():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT payload_json FROM form_config ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return []
    return json.loads(row["payload_json"])


def insert_cadastro(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cadastros (
            id_ponto,
            nome_cadastrador,
            data_cadastro,
            hora_cadastro,
            latitude,
            longitude,
            status_sincronizacao,
            dados_extras,
            fotos_json,
            synced,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            data["id_ponto"],
            data.get("nome_cadastrador", ""),
            data.get("data_cadastro", ""),
            data.get("hora_cadastro", ""),
            str(data.get("latitude", "")),
            str(data.get("longitude", "")),
            data.get("status_sincronizacao", "pendente"),
            json.dumps(data.get("dados_extras", {}), ensure_ascii=False),
            json.dumps(data.get("fotos", []), ensure_ascii=False),
            0,
        ),
    )
    conn.commit()
    conn.close()


def list_local_cadastros():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cadastros ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    resultados = []
    for row in rows:
        item = dict(row)
        item["dados_extras"] = json.loads(item["dados_extras"] or "{}")
        item["fotos"] = json.loads(item["fotos_json"] or "[]")
        resultados.append(item)
    return resultados


def list_pending_cadastros():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cadastros WHERE synced = 0 ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()

    resultados = []
    for row in rows:
        item = dict(row)
        item["dados_extras"] = json.loads(item["dados_extras"] or "{}")
        item["fotos"] = json.loads(item["fotos_json"] or "[]")
        resultados.append(item)
    return resultados


def mark_as_synced(local_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cadastros SET synced = 1, status_sincronizacao = 'sincronizado' WHERE id = ?",
        (local_id,),
    )
    conn.commit()
    conn.close()