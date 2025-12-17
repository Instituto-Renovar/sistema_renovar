import locale

# Funções Utilitárias (Máscaras e Formatação)

def formatar_telefone(e):
    """Máscara (XX) X XXXX-XXXX"""
    v = "".join(filter(str.isdigit, e.control.value))[:11]
    n = ""
    if len(v) > 0: n += v[:2]
    if len(v) > 2: n += f" {v[2:3]}"
    if len(v) > 3: n += f" {v[3:7]}"
    if len(v) > 7: n += f" {v[7:]}"
    e.control.value = n
    e.control.update()

def formatar_cpf(e):
    """Máscara 000.000.000-00"""
    v = "".join(filter(str.isdigit, e.control.value))[:11]
    n = ""
    if len(v) > 0: n += v[:3]
    if len(v) > 3: n += f".{v[3:6]}"
    if len(v) > 6: n += f".{v[6:9]}"
    if len(v) > 9: n += f"-{v[9:]}"
    e.control.value = n
    e.control.update()

def formatar_data(e):
    """Máscara DD/MM/AAAA"""
    v = "".join(filter(str.isdigit, e.control.value))[:8]
    n = ""
    if len(v) > 0: n += v[:2]
    if len(v) > 2: n += f"/{v[2:4]}"
    if len(v) > 4: n += f"/{v[4:]}"
    e.control.value = n
    e.control.update()

def formatar_cep(e):
    """Máscara 00.000-000"""
    v = "".join(filter(str.isdigit, e.control.value))[:8]
    n = ""
    if len(v) > 0: n += v[:2]
    if len(v) > 2: n += f".{v[2:5]}"
    if len(v) > 5: n += f"-{v[5:]}"
    e.control.value = n
    e.control.update()

def formatar_moeda(e):
    """
    Formata valores monetários em tempo real.
    Ex: Digita 1500 -> Vira 15,00. Digita 150000 -> Vira 1.500,00
    """
    valor = "".join(filter(str.isdigit, e.control.value))
    
    if not valor:
        e.control.value = ""
    else:
        try:
            # Transforma em float (centavos)
            f_valor = float(valor) / 100
            # Formatação manual para garantir padrão PT-BR (1.000,00)
            # O replace troca ponto por X, virgula por ponto, e X por virgula para inverter o padrão americano
            formatado = f"{f_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            e.control.value = formatado
        except:
            pass
            
    e.control.update()