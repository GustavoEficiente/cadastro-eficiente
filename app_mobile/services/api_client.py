import json
import mimetypes
import os
import requests


def normalize_base_url(base_url: str) -> str:
    base_url = (base_url or "").strip()
    return base_url.rstrip("/")


def login(base_url: str, username: str, password: str):
    url = f"{normalize_base_url(base_url)}/api/login/"

    payload = {
        "username": username,
        "password": password,
        "usuario": username,
        "senha": password,
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_campos(base_url: str):
    url = f"{normalize_base_url(base_url)}/api/campos/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def send_cadastro(base_url: str, cadastro: dict):
    url = f"{normalize_base_url(base_url)}/api/cadastros/criar/"

    fotos = cadastro.get("fotos", [])
    fotos_validas = [f for f in fotos if f and os.path.exists(f)]

    data = {
        "id_ponto": cadastro.get("id_ponto", ""),
        "nome_cadastrador": cadastro.get("nome_cadastrador", ""),
        "usuario": cadastro.get("nome_cadastrador", ""),
        "data_cadastro": cadastro.get("data_cadastro", ""),
        "hora_cadastro": cadastro.get("hora_cadastro", ""),
        "latitude": cadastro.get("latitude", ""),
        "longitude": cadastro.get("longitude", ""),
        "status_sincronizacao": cadastro.get("status_sincronizacao", "Sincronizado"),
        "dados_extras": json.dumps(cadastro.get("dados_extras", {}), ensure_ascii=False),
    }

    file_handle = None

    try:
        if fotos_validas:
            caminho = fotos_validas[0]
            file_handle = open(caminho, "rb")

            mime_type = mimetypes.guess_type(caminho)[0] or "image/jpeg"

            files = {
                "foto": (os.path.basename(caminho), file_handle, mime_type)
            }

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=60
            )
        else:
            response = requests.post(
                url,
                data=data,
                timeout=60
            )

        print("STATUS:", response.status_code)
        print("RESPOSTA:", response.text)

        response.raise_for_status()
        return response.json()

    finally:
        if file_handle:
            file_handle.close()