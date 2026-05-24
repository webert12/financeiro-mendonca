import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "gastos_dados.json"
LIMITE_DINHEIRO_SEMANAL = 500.00
TURMAS = ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5", "Turma 6"]

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="Mendonça Poços Finanças", page_icon="💧", layout="centered")

# --- SISTEMA DE ARMAZENAMENTO ISOLADO ---
def inicializar_estrutura():
    dados = {}
    for t in TURMAS:
        dados[t] = {"transacoes": [], "historico": []}
    return dados

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                # Verifica se o arquivo antigo estava no formato antigo (sem turmas)
                if "transacoes" in dados or isinstance(dados, list):
                    dados = inicializar_estrutura()
                # Garante que todas as turmas mapeadas existam no arquivo
                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {"transacoes": [], "historico": []}
                return dados
            except:
                return inicializar_estrutura()
    return inicializar_estrutura()

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

# Inicializa o banco de dados e o estado da sessão do usuário
dados = carregar_dados()

if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "turma_selecionada" not in st.session_state:
    st.session_state.turma_selecionada = None

# --- TELA DE LOGIN / SELEÇÃO DE TURMAS ---
if st.session_state.perfil is None:
    st.title("💧 MENDONÇA POÇOS")
    st.subheader("Painel de Controle Financeiro")
    st.write("Selecione abaixo o seu perfil operacional para continuar:")
    
    st.write("**Equipes de Campo:**")
    col1, col2 = st.columns(2)
    for i, t in enumerate(TURMAS):
        target_col = col1 if i % 2 == 0 else col2
        if target_col.button(f"Entrar como {t}", use_container_width=True):
            st.session_state.perfil = "TURMA"
            st.session_state.turma_selecionada = t
            st.rerun()
            
    st.divider()
    st.write("**Gestão Corporativa:**")
    if st.button("🔑 ÁREA DO ADMINISTRADOR (ADM)", use_container_width=True, type="primary"):
        st.session_state.perfil = "ADM"
        st.session_state.turma_selecionada = None
        st.rerun()

# --- INTERFACE PRINCIPAL (LOGADO) ---
else:
    # Barra Superior de Conexão
    col_user, col_logout = st.columns([3, 1])
    with col_user:
        identificacao = st.session_state.turma_selecionada if st.session_state.perfil == "TURMA" else "Administrador (ADM)"
        st.markdown(f"🟢 Conectado: **{identificacao}**")
    with col_logout:
        if st.button("Desconectar", use_container_width=True):
            st.session_state.perfil = None
            st.session_state.turma_selecionada = None
            st.rerun()
            
    st.title("Mendonça Poços Finanças")
    
    # Se for Turma Comum, ela opera apenas nos seus dados. Se for ADM, calcula o somatório global.
    if st.session_state.perfil == "TURMA":
        turma_ativa = st.session_state.turma_selecionada
        total_din = sum(t["valor"] for t in dados[turma_ativa]["transacoes"] if t.get("metodo") == "Dinheiro")
        total_car = sum(t["valor"] for t in dados[turma_ativa]["transacoes"] if t.get("metodo") == "Cartão")
        restante = LIMITE_DINHEIRO_SEMANAL - total_din
        limite_total = LIMITE_DINHEIRO_SEMANAL
    else:
        # Visão Consolidada do ADM
        total_din = sum(sum(t["valor"] for t in dados[tr]["transacoes"] if t.get("metodo") == "Dinheiro") for tr in TURMAS)
        total_car = sum(sum(t["valor"] for t in dados[tr]["transacoes"] if t.get("metodo") == "Cartão") for tr in TURMAS)
        limite_total = LIMITE_DINHEIRO_SEMANAL * len(TURMAS)
        restante = limite_total - total_din

    # --- CARDS EXIBIDORES DE VALORES ---
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="💵 DINHEIRO GASTO", value=f"R$ {total_din:.2f}", delta=f"Restante: R$ {restante:.2f}", delta_color="normal")
    with c2:
        st.metric(label="💳 CARTÃO ACUMULADO", value=f"R$ {total_car:.2f}")
        
    progresso_porcentagem = min(total_din / limite_total, 1.0) if limite_total > 0 else 0
    st.progress(progresso_porcentagem)
    
    # --- GERENCIADOR DE ABAS DO STREAMLIT ---
    # Se for ADM, removemos a aba de registro de gastos direto (ele apenas audita ou gerencia)
    abas_disponiveis = ["Registrar Gasto", "Histórico Mensal", "Ajustes ADM"] if st.session_state.perfil == "ADM" else ["Registrar Gasto", "Histórico Mensal"]
    
    if st.session_state.perfil == "ADM":
        aba_escolhida = st.sidebar.radio("Navegação do Gestor", ["Histórico Mensal", "Ajustes ADM"])
    else:
        aba_escolhida = st.tabs(["📝 Registrar Gasto", "📅 Histórico Mensal"])

    # --- ABA 1: REGISTRAR GASTO (APENAS PARA AS TURMAS) ---
    if (st.session_state.perfil == "TURMA" and aba_escolhida[0].expanded) or (st.session_state.perfil == "TURMA" and aba_escolhida == "Registrar Gasto"):
        st.subheader("📝 Registrar Novo Gasto")
        
        drop_categoria = st.selectbox("Selecione o Gasto", ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar", "Outros"])
        
        cat_final = drop_categoria
        if drop_categoria == "Outros":
            drop_outros = st.selectbox("Especifique 'Outros'", ["Pedágio", "Transportes", "Mecânica", "Lojas (Loja de Construção)"])
            cat_final = "Loja de Construção" if "Lojas" in drop_outros else drop_outros
            
        radio_pagamento = st.radio("Método de Pagamento", ["💵 Dinheiro", "💳 Cartão"], horizontal=True)
        metodo_final = "Dinheiro" if "Dinheiro" in radio_pagamento else "Cartão"
        
        txt_valor = st.text_input("Valor gasto R$", value="")
        
        if st.button("SALVAR LANÇAMENTO", type="primary", use_container_width=True):
            try:
                val = float(txt_valor.replace(",", "."))
                if val > 0:
                    agora = datetime.now()
                    nova_transacao = {
                        "data": agora.strftime("%d/%m %H:%M"),
                        "ano_mes": agora.strftime("%Y-%m"),
                        "categoria": cat_final,
                        "metodo": metodo_final,
                        "valor": val
                    }
                    
                    dados[st.session_state.turma_selecionada]["transacoes"].append(nova_transacao)
                    dados[st.session_state.turma_selecionada]["historico"].append(nova_transacao)
                    salvar_dados(dados)
                    st.success("✓ Gasto registrado com sucesso!")
                    st.rerun()
            except ValueError:
                st.error("Por favor, insira um valor numérico válido.")
                
        st.divider()
        st.subheader("Gastos Recentes Semanais")
        for t in reversed(dados[st.session_state.turma_selecionada]["transacoes"][-6:]):
            st.text(f"{t['data']} | {t['categoria']} | R$ {t['valor']:.2f} ({t['metodo']})")

    # --- ABA 2: HISTÓRICO MENSAL ---
    if (st.session_state.perfil == "TURMA" and aba_escolhida[1].expanded) or (st.session_state.perfil == "ADM" and aba_escolhida == "Histórico Mensal"):
        st.subheader("📅 Histórico Mensal de Lançamentos")
        
        # Filtros específicos do administrador para auditar turmas individuais
        turma_alvo = st.session_state.turma_selecionada
        if st.session_state.perfil == "ADM":
            turma_alvo = st.selectbox("Selecione a Turma para Auditoria", ["Todas Juntas"] + TURMAS)
            
        # Puxa a lista de meses disponíveis com base nos dados acessíveis
        lista_historicos = []
        if turma_alvo == "Todas Juntas":
            for tr in TURMAS:
                for trans in dados[tr]["historico"]:
                    tc = trans.copy()
                    tc["categoria"] = f"({tr}) {tc['categoria']}"
                    lista_historicos.append(tc)
        else:
            lista_historicos = dados[turma_alvo]["historico"]
            
        meses_disponiveis = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in lista_historicos)), reverse=True)
        
        if meses_disponiveis:
            mes_sel = st.selectbox("Selecione o Mês Relatório", meses_disponiveis)
            
            transacoes_mes = [t for t in lista_historicos if t.get("ano_mes", "") == mes_sel]
            tot_din_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Dinheiro")
            tot_car_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Cartão")
            
            st.info(f"💰 **Resumo Período:** 💵 Dinheiro: R$ {tot_din_mes:.2f} | 💳 Cartão: R$ {tot_car_mes:.2f}")
            
            st.write("**Transações do Mês:**")
            for t in reversed(transacoes_mes):
                st.text(f"{t['data']} - {t['categoria']} - R$ {t['valor']:.2f} ({t['metodo']})")
        else:
            st.write("Nenhum histórico registrado até o momento.")

    # --- ABA 3: AJUSTES E GESTÃO ADM ---
    if st.session_state.perfil == "ADM" and aba_escolhida == "Ajustes ADM":
        st.subheader("🚨 Ferramentas de Gestão Central")
        st.write("Os comandos abaixo alteram os dados de todas as frentes de trabalho simultaneamente.")
        
        if st.button("Resetar Semana de Todas as Turmas", type="primary", use_container_width=True):
            for tr in TURMAS:
                dados[tr]["transacoes"] = []
            salvar_dados(dados)
            st.success("🚨 A semana ativa de todas as equipes foi resetada com sucesso!")
            st.rerun()
value = f"💵 Dinheiro: R$ {tot_din:.2f} | 💳 Cartão: R$ {tot_car:.2f}"

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
