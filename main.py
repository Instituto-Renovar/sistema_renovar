import flet as ft
from config.firebase_config import inicializar_firebase
from core.colors import CORES
import os

# Importação das Views
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.workdesk_view import WorkDeskView
from views.classes_view import ClassesView
from views.incubator_view import IncubatorView
from views.settings_view import SettingsView
from views.teacher_view import TeacherView
from views.frequency_view import FrequencyView

def main(page: ft.Page):
    # Configuração Inicial
    page.title = "CRM Renovar"
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = CORES['fundo']
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Inicializa Firebase
    try:
        inicializar_firebase()
    except Exception as e:
        print(f"⚠️ Aviso: Firebase não conectou corretamente: {e}")

    # Função que gerencia qual tela mostrar
    def route_change(e):
        page.views.clear()
        val = page.route
        
        print(f"--- Carregando rota: {val} ---")
        
        try:
            if val == "/" or val == "": 
                page.views.append(LoginView(page))
            elif val == "/dashboard": page.views.append(DashboardView(page))
            elif val == "/workdesk": page.views.append(WorkDeskView(page))
            elif val == "/classes": page.views.append(ClassesView(page))
            elif val == "/frequency": page.views.append(FrequencyView(page))
            elif val == "/incubator": page.views.append(IncubatorView(page)) 
            elif val == "/settings": page.views.append(SettingsView(page))
            elif val == "/teacher": page.views.append(TeacherView(page))
            
            page.update()
            print("✅ Tela atualizada com sucesso!")
            
        except Exception as erro:
            print(f"❌ ERRO CRÍTICO AO CARREGAR A TELA {val}: {erro}")
            # Tela de Erro (Corrigida para não dar erro de alinhamento)
            page.views.append(ft.View(val, [
                ft.Container(
                    content=ft.Text(f"Erro no sistema: {erro}", color="red", size=20),
                    alignment=ft.Alignment(0, 0), # CORRIGIDO AQUI TAMBÉM
                    bgcolor="white",
                    expand=True
                )
            ]))
            page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    print("⚡ Sistema Iniciado. Carregando tela de login...")
    page.go("/") 
    # REMOVIDO: route_change(None) -> Isso causava carregamento duplo!

if __name__ == "__main__":
    print("--- INICIANDO SISTEMA CRM RENOVAR ---")
    ft.app(target=main, assets_dir="assets")