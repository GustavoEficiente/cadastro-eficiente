from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cadastros/", views.lista_cadastros, name="lista_cadastros"),
    path("cadastros/novo/", views.novo_cadastro, name="novo_cadastro"),
    path("cadastros/<int:pk>/editar/", views.editar_cadastro, name="editar_cadastro"),
    path("exportar/csv/", views.exportar_csv, name="exportar_csv"),
    path("exportar/excel/", views.exportar_excel, name="exportar_excel"),
    path("exportar/pdf/", views.exportar_pdf, name="exportar_pdf"),
    path("exportar/kml/", views.exportar_kml, name="exportar_kml"),
]