import json
import os
import requests


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def login(base_url: str, username: str, password: str):
    url = f"{normalize_base_url(base_url)}/api/login/"
    response = requests.post(
        url,
        json={"username": username, "password": password},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def fetch_campos(base_url: str):
    url = f"{normalize_base_url(base_url)}/api/campos/"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def send_cadastro(base_url: str, cadastro: dict):
    url = f"{normalize_base_url(base_url)}/api/cadastro-completo/"

    fotos = cadastro.get("fotos", [])
    fotos_validas = [f for f in fotos if f and os.path.exists(f)]

    if fotos_validas:
        data = {
            "id_ponto": cadastro.get("id_ponto", ""),
            "nome_cadastrador": cadastro.get("nome_cadastrador", ""),
            "data_cadastro": cadastro.get("data_cadastro", ""),
            "hora_cadastro": cadastro.get("hora_cadastro", ""),
            "latitude": cadastro.get("latitude", ""),
            "longitude": cadastro.get("longitude", ""),
            "status_sincronizacao": cadastro.get("status_sincronizacao", "sincronizado"),
            "dados_extras": json.dumps(cadastro.get("dados_extras", {}), ensure_ascii=False),
        }

        files = []
        file_handles = []

        try:
            for caminho in fotos_validas[:5]:
                fh = open(caminho, "rb")
                file_handles.append(fh)
                files.append(("fotos", (os.path.basename(caminho), fh, "image/jpeg")))

            response = requests.post(url, data=data, files=files, timeout=60)
            response.raise_for_status()
            return response.json()
        finally:
            for fh in file_handles:
                fh.close()

    response = requests.post(url, json=cadastro, timeout=30)
    response.raise_for_status()
    return response.json()