import flet as ft
from config.firebase_config import inicializar_firebase
from core.colors import CORES
import os # Importação necessária para ler a porta do servidor

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

    # Icone do sistema
    page.icon = "favicon.png"
    
    # Responsividade básica: Inicia rolando se for necessário
    page.scroll = ft.ScrollMode.AUTO
    
    page.bgcolor = CORES['fundo']
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(font_family="Jost", color_scheme_seed=CORES['roxo_brand'])

    inicializar_firebase()

    def route_change(e):
        page.views.clear()
        
        # Rotas
        if page.route == "/": page.views.append(LoginView(page))
        elif page.route == "/dashboard": page.views.append(DashboardView(page))
        elif page.route == "/workdesk": page.views.append(WorkDeskView(page))
        elif page.route == "/classes": page.views.append(ClassesView(page))
        elif page.route == "/frequency": page.views.append(FrequencyView(page))
        elif page.route == "/incubator": page.views.append(IncubatorView(page)) 
        elif page.route == "/settings": page.views.append(SettingsView(page))
        elif page.route == "/teacher": page.views.append(TeacherView(page))

        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/")

if __name__ == "__main__":
    # Lógica para rodar na Nuvem ou Local
    # Se existir uma variável de ambiente PORT (usada pelo Railway/Render), usa ela.
    # Senão, roda como Desktop app.
    port = int(os.environ.get("PORT", 8550))
    
    # Se estiver rodando na Web, o view=ft.AppView.WEB_BROWSER é automático
    ft.app(target=main, assets_dir="assets", port=port)