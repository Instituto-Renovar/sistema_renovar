import flet as ft
from core.colors import CORES
from controllers.auth_controller import AuthController

def LoginView(page: ft.Page):
    auth = AuthController()

    # --- Elementos da Tela ---
    logo = ft.Image(src="logo_renovar.png", width=100, height=100, fit="contain")
    
    txt_email = ft.TextField(
        label="E-mail", 
        prefix_icon=ft.Icons.PERSON, 
        border_radius=10, 
        bgcolor=ft.Colors.GREY_50,
        height=50,
        text_size=14,
        content_padding=15
    )
    
    txt_senha = ft.TextField(
        label="Senha", 
        prefix_icon=ft.Icons.LOCK, 
        password=True, 
        can_reveal_password=True, 
        border_radius=10, 
        bgcolor=ft.Colors.GREY_50,
        height=50,
        text_size=14,
        content_padding=15
    )

    # --- Lógica de Login ---
    def realizar_login(e):
        if not txt_email.value or not txt_senha.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha e-mail e senha!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        btn_entrar.text = "Entrando..."
        btn_entrar.disabled = True
        page.update()

        try:
            sucesso, usuario = auth.login(txt_email.value, txt_senha.value)
        except Exception as err:
            print(f"Erro no login: {err}")
            sucesso = False

        if sucesso:
            # Salva na memória volátil (funciona sempre)
            page.usuario = usuario
            print(f"✅ Login efetuado! Usuário: {usuario.get('nome')}")
            
            # Redirecionamento
            if usuario.get('funcao') == 'Professor':
                page.go("/teacher")
            else:
                page.go("/dashboard")
        else:
            btn_entrar.text = "ACESSAR SISTEMA"
            btn_entrar.disabled = False
            page.snack_bar = ft.SnackBar(ft.Text("E-mail ou senha incorretos!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # --- Lógica de Recuperação ---
    def abrir_modal_esqueci(e):
        txt_email_rec = ft.TextField(label="Digite seu e-mail cadastrado", width=300)
        
        def enviar_recuperacao(e):
            if not txt_email_rec.value: return
            sucesso, msg = auth.recuperar_senha(txt_email_rec.value)
            cor = "green" if sucesso else "red"
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=cor)
            page.snack_bar.open = True
            page.close(dlg)
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Recuperar Senha", size=16, weight="bold"),
            content=ft.Column([
                ft.Text("Insira seu e-mail. Enviaremos uma nova senha provisória.", size=12, color="grey"),
                txt_email_rec
            ], height=100, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg)),
                ft.ElevatedButton("Enviar", bgcolor=CORES['ouro'], color="white", on_click=enviar_recuperacao)
            ],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg)

    btn_entrar = ft.ElevatedButton(
        "ACESSAR SISTEMA",
        bgcolor=CORES['ouro'],
        color="white",
        width=300,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=realizar_login
    )

    btn_esqueci = ft.TextButton(
        "Esqueci minha senha",
        style=ft.ButtonStyle(color=CORES['ouro']),
        on_click=abrir_modal_esqueci
    )

    card_login = ft.Container(
        width=380, padding=40, bgcolor="white", border_radius=20,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.2, "black")),
        content=ft.Column([
            ft.Container(content=logo, alignment=ft.Alignment(0, 0)),
            ft.Container(height=10),
            ft.Text("Bem-vindo", size=24, weight="bold", color="#31144A", text_align="center"),
            ft.Container(height=20),
            txt_email,
            ft.Container(height=10),
            txt_senha,
            ft.Container(height=20),
            btn_entrar,
            ft.Container(content=btn_esqueci, alignment=ft.Alignment(0, 0))
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    layout_centro = ft.Container(
        content=card_login, 
        expand=True, 
        bgcolor="#31144A", 
        alignment=ft.Alignment(0, 0)
    )

    return ft.View(route="/", controls=[layout_centro], padding=0)