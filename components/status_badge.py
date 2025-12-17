import flet as ft

def StatusBadge(status):
    """Badge estilo Pílula Pastel (Fiel à imagem ac3f15)"""
    status = status.upper() if status else "NOVO"
    
    # Cores exatas da imagem
    cor_bg = "#F3F4F6"
    cor_dot = "#9CA3AF"
    cor_txt = "#374151"
    
    if status == "NOVO":
        cor_bg = "#DBEAFE"      # Azul
        cor_dot = "#3B82F6"
        cor_txt = "#1E40AF"
    
    elif status == "MATRICULADO":
        cor_bg = "#D1FAE5"      # Verde
        cor_dot = "#10B981"
        cor_txt = "#065F46"
        
    elif status in ["EM CONTATO", "EM NEGOCIAÇÃO", "INTERESSADO"]:
        cor_bg = "#FEF3C7"      # Amarelo/Laranja suave
        cor_dot = "#F59E0B"
        cor_txt = "#92400E"
        
    elif status in ["INCUBADORA", "EM ESPERA"]:
        cor_bg = "#FFEDD5"      # Laranja
        cor_dot = "#F97316"
        cor_txt = "#9A3412"
        
    elif status == "TURMA ABERTA": # Badge verde especial do curso
        return ft.Container(
            content=ft.Text("TURMA ABERTA", size=9, weight="bold", color="#065F46"),
            bgcolor="#D1FAE5",
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            border_radius=4
        )

    return ft.Container(
        bgcolor=cor_bg,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        content=ft.Row([
            ft.Container(width=6, height=6, border_radius=6, bgcolor=cor_dot),
            ft.Text(status.title(), size=11, weight=ft.FontWeight.BOLD, color=cor_txt, font_family="Jost")
        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER, run_spacing=0),
        width=100,
        alignment=ft.alignment.center
    )