import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.clock import Clock

from services.db import (
    init_db,
    save_user_session,
    get_user_session,
    clear_user_session,
    save_form_config,
    get_form_config,
    insert_cadastro,
    list_pending_cadastros,
    list_local_cadastros,
    mark_as_synced,
)
from services.api_client import login, fetch_campos, send_cadastro
from services.gps_service import GPSService

try:
    from plyer import filechooser
except Exception:
    filechooser = None

KV = """
ScreenManager:
    LoginScreen:
    HomeScreen:
    FormScreen:
    LocalListScreen:

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.03, 0.12, 0.27, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:
            size_hint_y: 0.1

        Label:
            text: "Cadastro Eficiente"
            font_size: "22sp"
            bold: True
            size_hint_y: None
            height: dp(40)

        TextInput:
            id: base_url
            hint_text: "URL do servidor (ex.: https://cadastro-eficiente-1.onrender.com)"
            multiline: False
            text: root.base_url
            size_hint_y: None
            height: dp(48)

        TextInput:
            id: username
            hint_text: "Usuário"
            multiline: False
            text: root.username
            size_hint_y: None
            height: dp(48)

        TextInput:
            id: password
            hint_text: "Senha"
            password: True
            multiline: False
            text: root.password
            size_hint_y: None
            height: dp(48)

        Button:
            text: "Entrar"
            size_hint_y: None
            height: dp(52)
            on_release:
                root.do_login(base_url.text, username.text, password.text)

        Label:
            text: root.status_text
            text_size: self.width, None
            halign: "center"
            valign: "middle"

        Widget:
            size_hint_y: 0.2

<HomeScreen>:
    name: "home"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.03, 0.12, 0.27, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Cadastro Eficiente"
            font_size: "22sp"
            bold: True
            size_hint_y: None
            height: dp(40)

        Label:
            text: root.info_text
            size_hint_y: None
            height: dp(28)

        Button:
            text: "Novo cadastro"
            size_hint_y: None
            height: dp(50)
            on_release:
                app.open_form()

        Button:
            text: "Cadastros locais"
            size_hint_y: None
            height: dp(50)
            on_release:
                app.open_local_list()

        Button:
            text: "Sincronizar pendentes"
            size_hint_y: None
            height: dp(50)
            on_release:
                root.sync_pending()

        Button:
            text: "Atualizar configuração do formulário"
            size_hint_y: None
            height: dp(50)
            on_release:
                root.refresh_form_config()

        Button:
            text: "Sair"
            size_hint_y: None
            height: dp(50)
            on_release:
                app.logout()

        Label:
            text: root.sync_message
            text_size: self.width, None
            halign: "center"

<FormScreen>:
    name: "form"
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.03, 0.12, 0.27, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(8)

            Button:
                text: "Voltar"
                on_release: app.root.current = "home"

            Button:
                text: "Capturar coordenadas"
                on_release: root.capture_gps()

            Button:
                text: "Adicionar foto"
                on_release: root.pick_photo()

            Button:
                text: "Salvar local"
                on_release: root.save_local()

        Label:
            text: root.status_text
            size_hint_y: None
            height: dp(28)

        Label:
            text: root.photos_text
            size_hint_y: None
            height: dp(24)

        ScrollView:
            do_scroll_x: False

            GridLayout:
                id: form_container
                cols: 1
                spacing: dp(10)
                padding: dp(8)
                size_hint_y: None
                height: self.minimum_height

<LocalListScreen>:
    name: "local_list"
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.03, 0.12, 0.27, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(50)

            Button:
                text: "Voltar"
                on_release: app.root.current = "home"

            Button:
                text: "Atualizar lista"
                on_release: root.refresh_list()

        Label:
            text: root.status_text
            size_hint_y: None
            height: dp(28)

        ScrollView:
            do_scroll_x: False

            GridLayout:
                id: list_container
                cols: 1
                spacing: dp(8)
                padding: dp(8)
                size_hint_y: None
                height: self.minimum_height
"""


def gerar_id_ponto():
    agora = datetime.now()
    sufixo = str(uuid.uuid4())[:4].upper()
    return f"CEF-{agora.strftime('%Y%m%d-%H%M%S')}-{sufixo}"


class LoginScreen(Screen):
    base_url = StringProperty("")
    username = StringProperty("")
    password = StringProperty("")
    status_text = StringProperty("")

    def on_pre_enter(self):
        sess = get_user_session()
        if sess:
            self.base_url = sess.get("base_url", "")
            self.username = sess.get("username", "")
            self.password = sess.get("password", "")

    def do_login(self, base_url, username, password):
        base_url = (base_url or "").strip()
        username = (username or "").strip()
        password = (password or "").strip()

        if not base_url or not username or not password:
            self.status_text = "Preencha URL, usuário e senha."
            return

        try:
            result = login(base_url, username, password)

            if result.get("success") or result.get("ok"):
                config = fetch_campos(base_url)

                if isinstance(config, list):
                    campos = config
                else:
                    campos = config.get("results", [])

                save_user_session(base_url, username, password)
                save_form_config(campos)
                self.status_text = "Login realizado com sucesso."
                app = App.get_running_app()
                app.update_home()
                app.root.current = "home"
            else:
                self.status_text = result.get("message", "Falha no login.")
        except Exception as e:
            self.status_text = f"Erro: {e}"


class HomeScreen(Screen):
    info_text = StringProperty("")
    sync_message = StringProperty("")

    def on_pre_enter(self):
        self.refresh_info()

    def refresh_info(self):
        locais = list_local_cadastros()
        pendentes = [x for x in locais if int(x["synced"]) == 0]
        self.info_text = f"Cadastros locais: {len(locais)} | Pendentes: {len(pendentes)}"

    def refresh_form_config(self):
        sess = get_user_session()
        if not sess:
            self.sync_message = "Faça login primeiro."
            return

        try:
            config = fetch_campos(sess["base_url"])
            if isinstance(config, list):
                campos = config
            else:
                campos = config.get("results", [])
            save_form_config(campos)
            self.sync_message = "Configuração atualizada com sucesso."
        except Exception as e:
            self.sync_message = f"Erro ao atualizar: {e}"

    def sync_pending(self):
        sess = get_user_session()
        if not sess:
            self.sync_message = "Faça login primeiro."
            return

        pendentes = list_pending_cadastros()
        if not pendentes:
            self.sync_message = "Nenhum cadastro pendente."
            self.refresh_info()
            return

        enviados = 0
        erros = 0

        for item in pendentes:
            payload = {
                "id_ponto": item["id_ponto"],
                "nome_cadastrador": item["nome_cadastrador"],
                "data_cadastro": item["data_cadastro"],
                "hora_cadastro": item["hora_cadastro"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "status_sincronizacao": "Sincronizado",
                "dados_extras": item["dados_extras"],
                "fotos": item["fotos"],
            }

            try:
                resposta = send_cadastro(sess["base_url"], payload)
                if resposta.get("ok") or resposta.get("success"):
                    mark_as_synced(item["id"])
                    enviados += 1
                else:
                    erros += 1
            except Exception:
                erros += 1

        self.sync_message = f"Sincronização concluída. Enviados: {enviados} | Erros: {erros}"
        self.refresh_info()


class FormScreen(Screen):
    status_text = StringProperty("")
    photos_text = StringProperty("Fotos selecionadas: 0/5")
    dynamic_widgets = ObjectProperty(allownone=True)
    selected_photos = ListProperty([])

    def on_pre_enter(self):
        self.build_form()

    def build_form(self):
        container = self.ids.form_container
        container.clear_widgets()
        self.dynamic_widgets = {}
        self.base_fields = {}
        self.selected_photos = []
        self.photos_text = "Fotos selecionadas: 0/5"

        fields = [
            ("nome_cadastrador", "Nome do cadastrador"),
            ("data_cadastro", "Data do cadastro (AAAA-MM-DD)"),
            ("hora_cadastro", "Hora do cadastro (HH:MM:SS)"),
            ("latitude", "Latitude"),
            ("longitude", "Longitude"),
        ]

        defaults = {
            "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
            "hora_cadastro": datetime.now().strftime("%H:%M:%S"),
        }

        for field_key, label_text in fields:
            container.add_widget(Label(text=label_text, size_hint_y=None, height=dp(28)))
            ti = TextInput(
                text=defaults.get(field_key, ""),
                multiline=False,
                size_hint_y=None,
                height=dp(44),
            )
            self.base_fields[field_key] = ti
            container.add_widget(ti)

        config = get_form_config()

        for campo in config:
            nome = campo["nome_interno"]
            rotulo = campo["rotulo"]
            tipo = campo["tipo_campo"]

            container.add_widget(Label(text=rotulo, size_hint_y=None, height=dp(28)))

            if tipo == "lista":
                opcoes = [o["valor"] for o in campo.get("opcoes", []) if o.get("ativo")]
                widget = Spinner(
                    text="Selecione",
                    values=opcoes,
                    size_hint_y=None,
                    height=dp(44),
                )

            elif tipo == "booleano":
                box = BoxLayout(size_hint_y=None, height=dp(44))
                cb = CheckBox(size_hint=(None, None), size=(dp(40), dp(40)))
                box.add_widget(cb)
                container.add_widget(box)
                self.dynamic_widgets[nome] = {"widget": cb, "tipo": tipo}
                continue

            elif tipo == "textarea":
                widget = TextInput(multiline=True, size_hint_y=None, height=dp(100))

            else:
                widget = TextInput(multiline=False, size_hint_y=None, height=dp(44))

            self.dynamic_widgets[nome] = {"widget": widget, "tipo": tipo}
            container.add_widget(widget)

    def capture_gps(self):
        gps_service = App.get_running_app().gps_service

        def set_coords(lat, lon):
            self.base_fields["latitude"].text = lat
            self.base_fields["longitude"].text = lon
            self.status_text = "Coordenadas capturadas."

        gps_service.configure(set_coords)
        ok, _msg = gps_service.start()

        if ok:
            self.status_text = "Tentando capturar GPS..."
        else:
            gps_service.mock_fill_desktop()
            self.status_text = "GPS não disponível neste ambiente. Preenchimento de teste ativado."

    def pick_photo(self):
        if len(self.selected_photos) >= 5:
            self.status_text = "Limite máximo de 5 fotos por cadastro."
            return

        if not filechooser:
            self.status_text = "Seletor de arquivo não disponível neste ambiente."
            return

        try:
            caminhos = filechooser.open_file(
                title="Selecione uma foto",
                multiple=False,
                filters=[("Imagens", "*.png;*.jpg;*.jpeg")]
            )
            if caminhos:
                caminho = caminhos[0]
                if len(self.selected_photos) < 5:
                    self.selected_photos.append(caminho)
                    self.photos_text = f"Fotos selecionadas: {len(self.selected_photos)}/5"
                    self.status_text = f"Foto adicionada: {os.path.basename(caminho)}"
        except Exception as e:
            self.status_text = f"Erro ao selecionar foto: {e}"

    def _copiar_fotos_para_pasta_local(self, id_ponto):
        pasta_base = Path(__file__).resolve().parent / "fotos_local"
        pasta_base.mkdir(parents=True, exist_ok=True)

        pasta_cadastro = pasta_base / id_ponto
        pasta_cadastro.mkdir(parents=True, exist_ok=True)

        fotos_salvas = []

        for i, origem in enumerate(self.selected_photos[:5], start=1):
            if not os.path.exists(origem):
                continue

            ext = Path(origem).suffix.lower() or ".jpg"
            destino = pasta_cadastro / f"foto_{i}{ext}"
            shutil.copy2(origem, destino)
            fotos_salvas.append(str(destino))

        return fotos_salvas

    def save_local(self):
        dados_extras = {}

        for nome, meta in self.dynamic_widgets.items():
            widget = meta["widget"]
            tipo = meta["tipo"]

            if tipo == "booleano":
                valor = widget.active
            elif tipo == "lista":
                valor = "" if widget.text == "Selecione" else widget.text
            else:
                valor = widget.text

            dados_extras[nome] = valor

        id_ponto = gerar_id_ponto()
        fotos_salvas = self._copiar_fotos_para_pasta_local(id_ponto)

        cadastro = {
            "id_ponto": id_ponto,
            "nome_cadastrador": self.base_fields["nome_cadastrador"].text.strip(),
            "data_cadastro": self.base_fields["data_cadastro"].text.strip(),
            "hora_cadastro": self.base_fields["hora_cadastro"].text.strip(),
            "latitude": self.base_fields["latitude"].text.strip(),
            "longitude": self.base_fields["longitude"].text.strip(),
            "status_sincronizacao": "pendente",
            "dados_extras": dados_extras,
            "fotos": fotos_salvas,
        }

        insert_cadastro(cadastro)
        self.status_text = f"Cadastro salvo localmente: {cadastro['id_ponto']}"
        Clock.schedule_once(lambda _dt: self.build_form(), 0.3)


class LocalListScreen(Screen):
    status_text = StringProperty("")

    def on_pre_enter(self):
        self.refresh_list()

    def refresh_list(self):
        container = self.ids.list_container
        container.clear_widgets()

        registros = list_local_cadastros()

        if not registros:
            container.add_widget(Label(text="Nenhum cadastro local.", size_hint_y=None, height=dp(30)))
            return

        for item in registros:
            synced_text = "SINCRONIZADO" if int(item["synced"]) == 1 else "PENDENTE"
            qtd_fotos = len(item.get("fotos", []))
            texto = (
                f"{item['id_ponto']} | {item['nome_cadastrador']} | "
                f"{item['data_cadastro']} {item['hora_cadastro']} | "
                f"{synced_text} | Fotos: {qtd_fotos}"
            )
            lbl = Label(text=texto, size_hint_y=None, height=dp(36))
            container.add_widget(lbl)


class CadastroEficienteApp(App):
    def build(self):
        self.title = "Cadastro Eficiente"
        init_db()
        self.gps_service = GPSService()
        return Builder.load_string(KV)

    def on_start(self):
        sess = get_user_session()
        if sess:
            self.root.current = "home"
        self.update_home()

    def update_home(self):
        try:
            home = self.root.get_screen("home")
            home.refresh_info()
        except Exception:
            pass

    def open_form(self):
        self.root.current = "form"

    def open_local_list(self):
        self.root.current = "local_list"

    def logout(self):
        clear_user_session()
        self.root.current = "login"


if __name__ == "__main__":
    CadastroEficienteApp().run()