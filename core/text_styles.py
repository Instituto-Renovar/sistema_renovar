import flet as ft
from core.colors import CORES

# Estilos de Texto Reutilizáveis

def T_H1(texto):
    """Título Grande (Ex: Nome da Página)"""
    return ft.Text(texto, size=28, weight=ft.FontWeight.BOLD, color=CORES['roxo_brand'], font_family="Jost")

def T_H2(texto):
    """Subtítulo (Ex: Título de Seção)"""
    return ft.Text(texto, size=20, weight=ft.FontWeight.BOLD, color=CORES['roxo_accent'], font_family="Jost")

def T_Body(texto, cor=CORES['texto']):
    """Texto Comum"""
    return ft.Text(texto, size=14, color=cor, font_family="Jost")

def T_Label(texto):
    """Texto Pequeno (Labels de inputs)"""
    return ft.Text(texto, size=12, color=CORES['texto_leve'], weight=ft.FontWeight.W_500, font_family="Jost")