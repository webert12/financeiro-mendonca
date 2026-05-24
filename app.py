import flet as ft
import json
import os
from datetime import datetime

DATA_FILE = "gastos_dados.json"
LIMITE_PADRAO_SEMANAL = 500.00
TURMAS_DISPONIVEIS = ["Turma Rafael", "Turma Ednaldo", "Turma Carlos", "Turma L. Felipe", "Turma Cardoso", "Turma Manutenção"]

def inicializar_estrutura():
    """Garante que cada turma tenha seu espaço 100% individual e limpo no arquivo"""
    dados = {}
    for turma in TURMAS_DISPONIVEIS:
        dados[turma] = {
            "transacoes": [],
            "historico": []
        }
    return dados

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                # Garante que novas turmas ou chaves estejam presentes se o arquivo for antigo
                for turma in TURMAS_DISPONIVEIS:
                    if turma not in dados:
                        dados[turma] = {"transacoes": [], "historico": []}
                return dados
            except:
                return inicializar_estrutura()
    return inicializar_estrutura()

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

def main(page: ft.Page):
    page.title = "Mendonça Poços Finanças"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    dados_globais = carregar_dados()
    
    # Variáveis de controle de sessão
    usuario_atual = {"perfil": None, "turma_selecionada": None}

    # --- COMPONENTES DE INTERFACE GLOBAIS ---
    txt_dinheiro = ft.Text("R$ 0.00", size=24, weight=ft.FontWeight.BOLD)
    txt_restante = ft.Text("Restante: R$ 500.00", size=12, color=ft.colors.GREEN)
    txt_cartao = ft.Text("R$ 0.00", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.PINK)
    progresso = ft.ProgressBar(value=0.0, bgcolor=ft.colors.SURFACE_VARIANT, color=ft.colors.CYAN)
    lista_semana = ft.ListView(expand=True, spacing=10, padding=10)
    
    drop_categoria = ft.Dropdown(
        label="Selecione o Gasto",
        options=[
            ft.dropdown.Option("Café da Manhã"),
            ft.dropdown.Option("Almoço"),
            ft.dropdown.Option("Café da Tarde"),
            ft.dropdown.Option("Jantar"),
            ft.dropdown.Option("Outros"),
        ],
        on_change=lambda e: mudar_categoria(e)
    )

    drop_outros = ft.Dropdown(
        label="Especifique 'Outros'",
        visible=False,
        options=[
            ft.dropdown.Option("Pedágio"),
            ft.dropdown.Option("Transportes"),
            ft.dropdown.Option("Mecânica"),
            ft.dropdown.Option("Lojas (Loja de Construção)"),
        ]
    )

    def mudar_categoria(e):
        drop_outros.visible = (drop_categoria.value == "Outros")
        page.update()

    radio_pagamento = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="Dinheiro", label="💵 Dinheiro"),
        ft.Radio(value="Cartão", label="💳 Cartão")
    ]))

    txt_valor = ft.TextField(label="Valor gasto R$", keyboard_type=ft.KeyboardType.NUMBER)

    # --- HISTÓRICO MENSAL ---
    drop_adm_turma_filtro = ft.Dropdown(label="Filtrar por Turma (ADM)", options=[ft.dropdown.Option(t) for t in TURMAS_DISPONIVEIS], visible=False)
    drop_meses = ft.Dropdown(label="Selecione o Mês")
    txt_resumo_mes = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    lista_mes = ft.ListView(expand=True, spacing=5)

    # --- FUNÇÃO DE LOGICA: ATUALIZAR VALORES NA TELA ---
    def atualizar_valores():
        turma = usuario_atual["turma_selecionada"]
        
        # Se for ADM e não escolheu uma turma específica na aba de visão, calcula o geral de todas
        if usuario_atual["perfil"] == "ADM" and not turma:
            total_din = sum(sum(t["valor"] for t in dados_globais[tr]["transacoes"] if t.get("metodo") == "Dinheiro") for tr in TURMAS_DISPONIVEIS)
            total_car = sum(sum(t["valor"] for t in dados_globais[tr]["transacoes"] if t.get("metodo") == "Cartão") for tr in TURMAS_DISPONIVEIS)
            restante = (LIMITE_PADRAO_SEMANAL * len(TURMAS_DISPONIVEIS)) - total_din
            limite_total = LIMITE_PADRAO_SEMANAL * len(TURMAS_DISPONIVEIS)
        else:
            # Puxa estritamente os dados da turma ativa logada
            alvo = turma if turma else TURMAS_DISPONIVEIS[0]
            total_din = sum(t["valor"] for t in dados_globais[alvo]["transacoes"] if t.get("metodo") == "Dinheiro")
            total_car = sum(t["valor"] for t in dados_globais[alvo]["transacoes"] if t.get("metodo") == "Cartão")
            restante = LIMITE_PADRAO_SEMANAL - total_din
            limite_total = LIMITE_PADRAO_SEMANAL

        txt_dinheiro.value = f"R$ {total_din:.2f}"
        txt_restante.value = f"Restante: R$ {restante:.2f}"
        txt_cartao.value = f"R$ {total_car:.2f}"
        progresso.value = min(total_din / limite_total, 1.0) if limite_total > 0 else 0

        # Atualiza a lista rápida de transações recentes baseada em quem está logado
        lista_semana.controls.clear()
        transacoes_remover_exibicao = []
        
        if usuario_atual["perfil"] == "ADM":
            # ADM lista os últimos gastos gerais indicando qual turma gastou
            for tr in TURMAS_DISPONIVEIS:
                for t in dados_globais[tr]["transacoes"]:
                    t_copia = t.copy()
                    t_copia["origem"] = tr
                    transacoes_remover_exibicao.append(t_copia)
        else:
            for t in dados_globais[turma]["transacoes"]:
                t_copia = t.copy()
                t_copia["origem"] = turma
                transacoes_remover_exibicao.append(t_copia)

        for t in reversed(transacoes_remover_exibicao[-10:]):
            emoji = "💳" if t.get("metodo") == "Cartão" else "💵"
            cor = ft.colors.PINK if t.get("metodo") == "Cartão" else ft.colors.CYAN
            tag_turma = f"[{t['origem']}] " if usuario_atual["perfil"] == "ADM" else ""
            lista_semana.controls.append(
                ft.ListTile(
                    leading=ft.Text(emoji, size=20),
                    title=ft.Text(f"{tag_turma}{t['categoria']} - R$ {t['valor']:.2f}"),
                    subtitle=ft.Text(f"{t['data']} | {t['metodo']}", color=cor)
                )
            )
        page.update()

    # --- AÇÃO: SALVAR NOVO GASTO ---
    def salvar_gasto(e):
        if usuario_atual["perfil"] == "ADM":
            page.overlay.append(ft.SnackBar(ft.Text("Erro: Administrador não faz lançamentos diretos. Escolha uma Turma."), open=True))
            page.update()
            return
            
        try:
            val = float(txt_valor.value.replace(",", "."))
            if val <= 0: return

            cat_final = drop_categoria.value
            if cat_final == "Outros":
                cat_final = "Loja de Construção" if "Lojas" in drop_outros.value else drop_outros.value

            met = radio_pagamento.value
            if not met or not cat_final: return

            turma = usuario_atual["turma_selecionada"]
            agora = datetime.now()
            
            nova_transacao = {
                "data": agora.strftime("%d/%m %H:%M"),
                "ano_mes": agora.strftime("%Y-%m"),
                "categoria": cat_final,
                "metodo": met,
                "valor": val
            }

            # Armazenamento rigoroso apenas na gaveta da turma correspondente
            dados_globais[turma]["transacoes"].append(nova_transacao)
            dados_globais[turma]["historico"].append(nova_transacao)
            salvar_dados(dados_globais)

            txt_valor.value = ""
            drop_categoria.value = None
            drop_outros.visible = False
            radio_pagamento.value = None

            atualizar_valores()
            carregar_meses()
            page.overlay.append(ft.SnackBar(ft.Text("✓ Gasto registrado com sucesso!"), open=True))
        except Exception as ex:
            pass

    btn_salvar = ft.ElevatedButton("SALVAR LANÇAMENTO", on_click=salvar_gasto, bgcolor=ft.colors.CYAN, color=ft.colors.BLACK)

    # --- LÓGICA DO FILTRO DE HISTÓRICO ---
    def carregar_meses():
        historico_combinado = []
        if usuario_atual["perfil"] == "ADM":
            for tr in TURMAS_DISPONIVEIS:
                historico_combinado.extend(dados_globais[tr]["historico"])
        else:
            historico_combinado = dados_globais[usuario_atual["turma_selecionada"]]["historico"]

        if historico_combinado:
            meses = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in historico_combinado)), reverse=True)
            drop_meses.options = [ft.dropdown.Option(m) for m in meses]
        page.update()

    def filtrar_mes(e):
        mes_sel = drop_meses.value
        if not mes_sel: return

        transacoes_filtradas = []
        
        if usuario_atual["perfil"] == "ADM":
            turma_filtro = drop_adm_turma_filtro.value
            if turma_filtro:
                # ADM vendo uma turma específica
                transacoes_filtradas = [t for t in dados_globais[turma_filtro]["historico"] if t.get("ano_mes", "") == mes_sel]
            else:
                # ADM vendo o consolidado de todas as turmas juntas
                for tr in TURMAS_DISPONIVEIS:
                    for t in dados_globais[tr]["historico"]:
                        if t.get("ano_mes", "") == mes_sel:
                            t_c = t.copy()
                            t_c["categoria"] = f"({tr}) {t_c['categoria']}"
                            transacoes_filtradas.append(t_c)
        else:
            # Turma vendo apenas seus próprios dados históricos
            transacoes_filtradas = [t for t in dados_globais[usuario_atual["turma_selecionada"]]["historico"] if t.get("ano_mes", "") == mes_sel]

        tot_din = sum(t["valor"] for t in transacoes_filtradas if t.get("metodo") == "Dinheiro")
        tot_car = sum(t["valor"] for t in transacoes_filtradas if t.get("metodo") == "Cartão")

        txt_resumo_mes.value = f"💵 Dinheiro: R$ {tot_din:.2f} | 💳 Cartão: R$ {tot_car:.2f}"

        lista_mes.controls.clear()
        for t in reversed(transacoes_filtradas):
            lista_mes.controls.append(ft.Text(f"{t['data']} - {t['categoria']} - R$ {t['valor']:.2f}"))
        page.update()

    btn_filtrar = ft.ElevatedButton("Visualizar Relatório", on_click=filtrar_mes)

    # --- ADMINISTRAÇÃO: RESET CONTROLADO ---
    def resetar_semana(e):
        if usuario_atual["perfil"] != "ADM": return
        
        # O ADM limpa a semana ativa de TODAS as turmas de uma vez só, preservando o histórico mensal
        for tr in TURMAS_DISPONIVEIS:
            dados_globais[tr]["transacoes"] = []
            
        salvar_dados(dados_globais)
        atualizar_valores()
        page.overlay.append(ft.SnackBar(ft.Text("🚨 Semana resetada para todas as turmas!"), open=True))

    btn_reset = ft.ElevatedButton("🚨 Resetar Semana Geral", on_click=resetar_semana, color=ft.colors.WHITE, bgcolor=ft.colors.RED)

    # --- SISTEMA DE SELEÇÃO DE PERFIL / LOGIN ---
    def logar_perfil(perfil, turma=None):
        usuario_atual["perfil"] = perfil
        usuario_atual["turma_selecionada"] = turma
        
        # Configurações visuais baseadas nas permissões do perfil
        if perfil == "ADM":
            aba_conf.visible = True
            drop_adm_turma_filtro.visible = True
            btn_reset.visible = True
            aba_registro.visible = False # O ADM monitora e audita, não faz lançamentos comuns
        else:
            aba_conf.visible = False
            drop_adm_turma_filtro.visible = False
            btn_reset.visible = False
            aba_registro.visible = True

        page.controls.clear()
        page.add(
            ft.Row([
                ft.Text(f"Conectado como: {turma if turma else perfil}", size=14, color=ft.colors.CYAN, weight=ft.FontWeight.BOLD),
                ft.TextButton("Desconectar", on_click=lambda e: exibir_tela_login())
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            tabs
        )
        atualizar_valores()
        carregar_meses()
        page.update()

    def exibir_tela_login():
        page.controls.clear()
        
        botoes_turmas = []
        for t in TURMAS_DISPONIVEIS:
            botoes_turmas.append(
                ft.ElevatedButton(text=t, on_click=lambda e, nome_t=t: logar_perfil("TURMA", nome_t), width=150)
            )

        grid_turmas = ft.GridView(
            expand=False,
            runs_count=2,
            max_extent=160,
            child_aspect_ratio=2.5,
            spacing=10,
            run_spacing=10,
            controls=botoes_turmas
        )

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("MENDONÇA POÇOS", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN),
                    ft.Text("Selecione seu acesso abaixo para continuar:", size=14, color=ft.colors.SUBTITLE_NATIVE_VIDEO),
                    ft.Divider(height=20),
                    ft.Text("Painel Operacional das Equipes:", size=14, weight=ft.FontWeight.BOLD),
                    grid_turmas,
                    ft.Divider(height=20),
                    ft.Text("Acesso de Gestão Corporativa:", size=14, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("ÁREA DO ADMINISTRADOR (ADM)", on_click=lambda e: logar_perfil("ADM"), bgcolor=ft.colors.SURFACE_VARIANT, color=ft.colors.WHITE, width=320),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        page.update()

    # --- MONTAGEM DO LAYOUT DAS ABAS ---
    card_dinheiro = ft.Container(ft.Column([ft.Text("💵 DINHEIRO", size=12), txt_dinheiro, txt_restante]), bgcolor=ft.colors.SURFACE_VARIANT, padding=15, border_radius=10, expand=True)
    card_cartao = ft.Container(ft.Column([ft.Text("💳 CARTÃO", size=12), txt_cartao, ft.Text("Acumulado Mês", size=12)]), bgcolor=ft.colors.SURFACE_VARIANT, padding=15, border_radius=10, expand=True)

    aba_registro = ft.Column([
        ft.Row([card_dinheiro, card_cartao]),
        progresso,
        ft.Text("📝 Registrar Novo Gasto", size=16, weight=ft.FontWeight.BOLD),
        drop_categoria, drop_outros, radio_pagamento, txt_valor, btn_salvar,
        ft.Divider(),
        ft.Text("Gastos Recentes Semanais", size=14, weight=ft.FontWeight.BOLD),
        lista_semana
    ], spacing=15)

    aba_hist = ft.Column([drop_adm_turma_filtro, drop_meses, btn_filtrar, txt_resumo_mes, ft.Divider(), lista_mes], spacing=15)
    aba_conf = ft.Column([ft.Text("Administração Central", size=16, weight=ft.FontWeight.BOLD), btn_reset], spacing=15)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Registrar", content=aba_registro),
            ft.Tab(text="Histórico", content=aba_hist),
            ft.Tab(text="Ajustes", content=aba_conf),
        ],
        expand=True
    )

    # Inicia mostrando a tela de seleção profissional de turmas
    exibir_tela_login()

if __name__ == "__main__":
    # Mantido a compatibilidade perfeita para rodar na rede ou emuladores pelo Pydroid/Termux
    ft.run(target=main, port=8550, view=None, host="0.0.0.0")
