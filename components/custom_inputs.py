import flet as ft
from core.colors import CORES

# Estilos Baseados nas Imagens (Tailwind Colors)
BORDA_INPUT = "#E5E7EB"  # Gray-200
TEXTO_INPUT = "#374151"  # Gray-700
BG_INPUT = "white"
LABEL_COLOR = "#111827"  # Gray-900 (Mais escuro, igual imagem)

class RenovarTextField(ft.TextField):
    def __init__(self, label, width=None, expand=False, on_change=None, read_only=False, suffix_icon=None, value=None, multiline=False, height=40, **kwargs):
        super().__init__(value=value, **kwargs) 
        self.label = "" 
        self.hint_text = "" # Placeholder vazio para ficar limpo
        self.width = width
        self.expand = expand
        self.on_change = on_change
        self.read_only = read_only
        self.suffix_icon = suffix_icon
        self.multiline = multiline
        
        # Estilo
        self.bgcolor = BG_INPUT
        self.border_color = BORDA_INPUT
        self.text_size = 14
        self.height = height if not multiline else None
        self.min_lines = 3 if multiline else 1
        self.content_padding = 12
        self.text_style = ft.TextStyle(color=TEXTO_INPUT, font_family="Jost")
        self.border_radius = 6
        self.cursor_color = CORES['ouro']

class RenovarDropdown(ft.Dropdown):
    def __init__(self, label, options=[], width=None, expand=False, on_change=None, value=None, **kwargs):
        # CORREÇÃO: Passando value corretamente para o pai
        super().__init__(value=value, **kwargs)
        
        self.label = ""
        self.hint_text = "Selecione"
        # Garante que options seja uma lista de strings ou de ft.dropdown.Option
        self.options = [ft.dropdown.Option(opt) if isinstance(opt, str) else opt for opt in options]
        self.width = width
        self.expand = expand
        self.on_change = on_change
        
        # Estilo
        self.bgcolor = BG_INPUT
        self.border_color = BORDA_INPUT
        self.border_radius = 6
        self.text_size = 14
        self.height = 40
        self.content_padding = 10
        self.text_style = ft.TextStyle(color=TEXTO_INPUT, font_family="Jost")