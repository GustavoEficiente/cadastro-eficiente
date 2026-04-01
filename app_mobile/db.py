import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "app.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario_logado (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            nome TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracao_cidades (
            id INTEGER PRIMARY KEY,
            cidade_id INTEGER,
            nome TEXT,
            uf TEXT,
            ativo INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracao_campos (
            id INTEGER PRIMARY KEY,
            campo_id INTEGER,
            nome_interno TEXT,
            rotulo TEXT,
            tipo_campo TEXT,
            obrigatorio INTEGER,
            ativo INTEGER,
            ordem INTEGER,
            usa_lista_opcoes INTEGER,
            opcoes_json TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cadastros_offline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_json TEXT,
            sincronizado INTEGER DEFAULT 0,
            criado_em TEXT
        )
    """)

    conn.commit()
    conn.close()


def salvar_usuario(user_id: int, username: str, nome: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuario_logado")
    cur.execute(
        "INSERT INTO usuario_logado (user_id, username, nome) VALUES (?, ?, ?)",
        (user_id, username, nome)
    )
    conn.commit()
    conn.close()


def obter_usuario():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, nome FROM usuario_logado LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id": row[0],
        "username": row[1],
        "nome": row[2],
    }


def salvar_cidades(cidades: list):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM configuracao_cidades")

    for cidade in cidades:
        cur.execute("""
            INSERT INTO configuracao_cidades (cidade_id, nome, uf, ativo)
            VALUES (?, ?, ?, ?)
        """, (
            cidade["id"],
            cidade["nome"],
            cidade["uf"],
            1 if cidade["ativo"] else 0
        ))

    conn.commit()
    conn.close()


def listar_cidades_local():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT cidade_id, nome, uf
        FROM configuracao_cidades
        WHERE ativo = 1
        ORDER BY nome
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        {"id": r[0], "nome": r[1], "uf": r[2]}
        for r in rows
    ]


def salvar_campos(campos: list):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM configuracao_campos")

    for campo in campos:
        cur.execute("""
            INSERT INTO configuracao_campos (
                campo_id, nome_interno, rotulo, tipo_campo,
                obrigatorio, ativo, ordem, usa_lista_opcoes, opcoes_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campo["id"],
            campo["nome_interno"],
            campo["rotulo"],
            campo["tipo_campo"],
            1 if campo["obrigatorio"] else 0,
            1 if campo["ativo"] else 0,
            campo["ordem"],
            1 if campo["usa_lista_opcoes"] else 0,
            json.dumps(campo.get("opcoes", []), ensure_ascii=False)
        ))

    conn.commit()
    conn.close()


def listar_campos_local():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT nome_interno, rotulo, tipo_campo, obrigatorio, ordem, opcoes_json
        FROM configuracao_campos
        WHERE ativo = 1
        ORDER BY ordem, rotulo
    """)
    rows = cur.fetchall()
    conn.close()

    saida = []
    for r in rows:
        saida.append({
            "nome_interno": r[0],
            "rotulo": r[1],
            "tipo_campo": r[2],
            "obrigatorio": bool(r[3]),
            "ordem": r[4],
            "opcoes": json.loads(r[5] or "[]")
        })
    return saida


def salvar_cadastro_offline(payload: dict):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cadastros_offline (payload_json, sincronizado, criado_em)
        VALUES (?, 0, datetime('now'))
    """, (json.dumps(payload, ensure_ascii=False),))
    conn.commit()
    conn.close()


def listar_pendentes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, payload_json
        FROM cadastros_offline
        WHERE sincronizado = 0
        ORDER BY id
    """)
    rows = cur.fetchall()
    conn.close()

    return [{"id": r[0], "payload": json.loads(r[1])} for r in rows]


def marcar_sincronizado(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE cadastros_offline
        SET sincronizado = 1
        WHERE id = ?
    """, (registro_id,))
    conn.commit()
    conn.close()