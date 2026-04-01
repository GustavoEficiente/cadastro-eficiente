import requests
from config import API_BASE_URL


def login(username: str, password: str) -> dict:
    url = f"{API_BASE_URL}/login/"
    response = requests.post(url, json={
        "username": username,
        "password": password
    }, timeout=20)
    response.raise_for_status()
    return response.json()


def listar_cidades() -> list:
    url = f"{API_BASE_URL}/cidades/"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def listar_campos() -> list:
    url = f"{API_BASE_URL}/campos/"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def enviar_cadastro(payload: dict) -> dict:
    url = f"{API_BASE_URL}/cadastro/"
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()