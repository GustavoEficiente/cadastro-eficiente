from kivy.app import App
from kivy.uix.label import Label

class TesteApp(App):
    def build(self):
        return Label(text="Kivy funcionando")

TesteApp().run()