from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from api_client import login, listar_cidades, listar_campos, enviar_cadastro
from db import (
    criar_tabelas, salvar_usuario, obter_usuario,
    salvar_cidades, listar_cidades_local,
    salvar_campos, listar_campos_local,
    salvar_cadastro_offline, listar_pendentes, marcar_sincronizado
)
from gps_service import GPSService


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.info = Label(text="Cadastro Eficiente", size_hint_y=None, height=50)
        self.username = TextInput(hint_text="Usuário", multiline=False, size_hint_y=None, height=44)
        self.password = TextInput(hint_text="Senha", password=True, multiline=False, size_hint_y=None, height=44)

        btn_login = Button(text="Entrar", size_hint_y=None, height=50)
        btn_login.bind(on_release=self.fazer_login)

        layout.add_widget(self.info)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(btn_login)

        self.add_widget(layout)

    def fazer_login(self, *args):
        try:
            resp = login(self.username.text.strip(), self.password.text.strip())
            if resp.get("status") == "ok":
                salvar_usuario(resp["user_id"], resp["username"], resp.get("nome", resp["username"]))

                cidades = listar_cidades()
                campos = listar_campos()
                salvar_cidades(cidades)
                salvar_campos(campos)

                self.manager.current = "cadastro"
            else:
                self.info.text = "Login inválido"
        except Exception as e:
            self.info.text = f"Erro login/API: {e}"


class CadastroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gps = GPSService()
        self.campos_widgets = {}

        raiz = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.status = Label(text="Novo cadastro", size_hint_y=None, height=40)
        raiz.add_widget(self.status)

        scroll = ScrollView()
        self.form = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter("height"))

        self.spinner_cidade = Spinner(text="Selecione a cidade", size_hint_y=None, height=44)
        self.spinner_tipo_coord = Spinner(
            text="decimal",
            values=["decimal", "gms", "utm"],
            size_hint_y=None,
            height=44
        )

        self.txt_lat = TextInput(hint_text="Latitude", multiline=False, size_hint_y=None, height=44)
        self.txt_lon = TextInput(hint_text="Longitude", multiline=False, size_hint_y=None, height=44)
        self.txt_coord_texto = TextInput(hint_text="Coordenada texto (opcional)", multiline=False, size_hint_y=None, height=44)

        self.form.add_widget(Label(text="Cidade", size_hint_y=None, height=30))
        self.form.add_widget(self.spinner_cidade)

        self.form.add_widget(Label(text="Tipo de coordenada", size_hint_y=None, height=30))
        self.form.add_widget(self.spinner_tipo_coord)

        self.form.add_widget(Label(text="Latitude", size_hint_y=None, height=30))
        self.form.add_widget(self.txt_lat)

        self.form.add_widget(Label(text="Longitude", size_hint_y=None, height=30))
        self.form.add_widget(self.txt_lon)

        self.form.add_widget(Label(text="Coordenada texto", size_hint_y=None, height=30))
        self.form.add_widget(self.txt_coord_texto)

        btn_gps = Button(text="Capturar coordenadas", size_hint_y=None, height=50)
        btn_gps.bind(on_release=self.capturar_coordenadas)
        self.form.add_widget(btn_gps)

        self.form.add_widget(Label(text="Campos do censo", size_hint_y=None, height=30))
        scroll.add_widget(self.form)

        botoes = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_salvar = Button(text="Salvar offline")
        btn_salvar.bind(on_release=self.salvar_offline)

        btn_sync = Button(text="Sincronizar")
        btn_sync.bind(on_release=self.sincronizar)

        botoes.add_widget(btn_salvar)
        botoes.add_widget(btn_sync)

        raiz.add_widget(scroll)
        raiz.add_widget(botoes)
        self.add_widget(raiz)

    def on_pre_enter(self, *args):
        self.carregar_cidades()
        self.montar_campos_dinamicos()

    def carregar_cidades(self):
        cidades = listar_cidades_local()
        self.spinner_cidade.values = [f'{c["id"]} - {c["nome"]}/{c["uf"]}' for c in cidades]

    def montar_campos_dinamicos(self):
        # remove campos antigos dinâmicos
        nomes_fixos = {
            self.spinner_cidade, self.spinner_tipo_coord,
            self.txt_lat, self.txt_lon, self.txt_coord_texto
        }
        while len(self.form.children) > 12:
            self.form.remove_widget(self.form.children[0])

        self.campos_widgets = {}
        campos = listar_campos_local()

        for campo in campos:
            self.form.add_widget(Label(text=campo["rotulo"], size_hint_y=None, height=30))

            tipo = campo["tipo_campo"]
            widget = None

            if tipo in ("texto", "numero", "data", "hora", "textarea"):
                widget = TextInput(multiline=(tipo == "textarea"), size_hint_y=None, height=90 if tipo == "textarea" else 44)
            elif tipo == "lista":
                valores = [op["valor"] for op in campo.get("opcoes", []) if op.get("ativo")]
                widget = Spinner(text="Selecione", values=valores, size_hint_y=None, height=44)
            elif tipo == "booleano":
                widget = Spinner(text="Selecione", values=["Sim", "Não"], size_hint_y=None, height=44)

            if widget:
                self.campos_widgets[campo["nome_interno"]] = widget
                self.form.add_widget(widget)

    def capturar_coordenadas(self, *args):
        ok = self.gps.iniciar()
        if not ok:
            self.status.text = "GPS indisponível aqui. Teste no Android."
            return

        self.status.text = "Buscando coordenadas..."
        Clock.schedule_once(self.preencher_coordenadas, 3)

    def preencher_coordenadas(self, dt):
        self.txt_lat.text = self.gps.latitude
        self.txt_lon.text = self.gps.longitude

        if self.gps.latitude and self.gps.longitude:
            self.status.text = "Coordenadas capturadas com sucesso."
        else:
            self.status.text = "Não foi possível obter coordenadas."
        self.gps.parar()

    def salvar_offline(self, *args):
        usuario = obter_usuario()
        if not usuario:
            self.status.text = "Usuário não encontrado."
            return

        cidade_id = None
        if self.spinner_cidade.text and " - " in self.spinner_cidade.text:
            cidade_id = int(self.spinner_cidade.text.split(" - ")[0])

        dados_extras = {}
        for nome, widget in self.campos_widgets.items():
            valor = getattr(widget, "text", "")
            dados_extras[nome] = valor

        payload = {
            "user_id": usuario["user_id"],
            "cidade": cidade_id,
            "tipo_coordenada": self.spinner_tipo_coord.text,
            "latitude": self.txt_lat.text or None,
            "longitude": self.txt_lon.text or None,
            "coordenada_texto": self.txt_coord_texto.text,
            "dados_extras": dados_extras,
        }

        salvar_cadastro_offline(payload)
        self.status.text = "Cadastro salvo offline."
        self.limpar_formulario()

    def sincronizar(self, *args):
        pendentes = listar_pendentes()
        enviados = 0

        for item in pendentes:
            try:
                enviar_cadastro(item["payload"])
                marcar_sincronizado(item["id"])
                enviados += 1
            except Exception:
                pass

        self.status.text = f"{enviados} cadastro(s) sincronizado(s)."

    def limpar_formulario(self):
        self.txt_lat.text = ""
        self.txt_lon.text = ""
        self.txt_coord_texto.text = ""
        self.spinner_tipo_coord.text = "decimal"
        self.spinner_cidade.text = "Selecione a cidade"

        for widget in self.campos_widgets.values():
            if hasattr(widget, "text"):
                if isinstance(widget, Spinner):
                    widget.text = "Selecione"
                else:
                    widget.text = ""


class CadastroEficienteApp(App):
    def build(self):
        criar_tabelas()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CadastroScreen(name="cadastro"))

        if obter_usuario():
            sm.current = "cadastro"
        else:
            sm.current = "login"

        return sm


if __name__ == "__main__":
    CadastroEficienteApp().run()