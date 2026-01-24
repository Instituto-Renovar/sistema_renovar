import flet as ft
from core.colors import CORES
from components.custom_inputs import RenovarTextField
from controllers.user_controller import UserController
import time

def LoginView(page: ft.Page):
    # Controller para validar o login
    user_ctrl = UserController()

    # --- Elementos Visuais ---
    # Logo
    logo = ft.Image(src="logo_renovar.png", width=200, height=200, fit=ft.ImageFit.CONTAIN)
    
    # Textos de Boas-vindas
    titulo = ft.Text("Bem-vindo de volta!", size=24, weight="bold", color="white")
    subtitulo = ft.Text("Acesse sua conta para continuar", size=14, color="white70")

    # Campos de Entrada
    email = RenovarTextField("E-mail", width=350, bgcolor="white", color="black")
    senha = RenovarTextField("Senha", password=True, width=350, can_reveal_password=True, bgcolor="white", color="black")
    
    # Texto de Erro (Invisível no início)
    txt_erro = ft.Text("", color="#FF6B6B", size=13, weight="bold", visible=False)

    # Link Recuperar Senha
    recuperar_senha = ft.TextButton("Esqueceu a senha?", style=ft.ButtonStyle(color="white70"))

    # Função de Login (Lógica Nova Blindada)
    def realizar_login(e):
        txt_erro.visible = False
        txt_erro.update()

        if not email.value or not senha.value:
            txt_erro.value = "Por favor, preencha e-mail e senha."
            txt_erro.visible = True
            page.update()
            return

        # Feedback visual
        btn_entrar.text = "Entrando..."
        btn_entrar.disabled = True
        btn_entrar.update()

        # Busca no banco (usando o método .get() rápido)
        usuario = user_ctrl.buscar_por_email(email.value)

        if usuario:
            if usuario.get('senha') == senha.value:
                # SALVA NA SESSÃO DO FLET (Isso que a Sidebar vai ler)
                page.session.set("user_name", usuario['nome'])
                page.session.set("user_perms", usuario.get('permissoes', []))
                
                print(f"✅ Login sucesso: {usuario['nome']}")
                page.go("/dashboard")
            else:
                txt_erro.value = "Senha incorreta."
                txt_erro.visible = True
        else:
            txt_erro.value = "E-mail não encontrado."
            txt_erro.visible = True

        # Restaura botão se falhar
        btn_entrar.text = "Entrar"
        btn_entrar.disabled = False
        page.update()

    # Botão Dourado (Estilo Original)
    btn_entrar = ft.ElevatedButton(
        "Entrar", 
        width=350, 
        height=50,
        bgcolor=CORES['ouro'], 
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=realizar_login
    )

    # --- Montagem do Layout Roxo ---
    conteudo_login = ft.Container(
        width=450,
        padding=40,
        border_radius=20,
        # Sem fundo branco, direto no roxo ou container trans? 
        # Baseado na sua descrição "centro roxo", vou deixar transparente para pegar o fundo
        content=ft.Column([
            ft.Container(content=logo, alignment=ft.alignment.center),
            ft.Container(height=10),
            titulo,
            subtitulo,
            ft.Container(height=30),
            email,
            senha,
            txt_erro, # Mensagem de erro aqui
            ft.Container(height=10),
            btn_entrar,
            recuperar_senha
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # Centralização na Tela (Padding removido para não grudar nas bordas)
    return ft.View(
        route="/",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                bgcolor=CORES['roxo_brand'], # Fundo Roxo Original
                content=conteudo_login
            )
        ],
        padding=0
    )