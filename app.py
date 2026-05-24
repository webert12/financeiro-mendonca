import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" ---
st.set_page_config(
    page_title="Mendonça Poços",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização profissional para Celular (Mobile-First)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child {
        background-color: #00cfcc;
        color: black;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stMetric {
        background-color: #1e2129;
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #00cfcc;
    }
    .logo-text {
        text-align: center;
        font-weight: bold;
        color: white;
        font-size: 24px;
        letter-spacing: 2px;
        margin-top: -10px;
        margin-bottom: 5px;
    }
    .sub-logo {
        text-align: center;
        color: #888b94;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "gastos_dados.json"
LIMITE_DINHEIRO_SEMANAL = 500.00
TURMAS = [f"Turma {i}" for i in range(1, 7)]

# --- FUNÇÕES DE ARMAZENAMENTO ISOLADO ---
def carregar_dados():
    estrutura_limpa = {t: {"transacoes": [], "historico": []} for t in TURMAS}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                if "transacoes" in dados or isinstance(dados, list):
                    return estrutura_limpa
                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {"transacoes": [], "historico": []}
                return dados
            except:
                return estrutura_limpa
    return estrutura_limpa

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

# Inicialização do Estado da Sessão
if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()
if 'perfil' not in st.session_state:
    st.session_state.perfil = None
if 'turma' not in st.session_state:
    st.session_state.turma = None

# --- DESIGN DA LOGO DIGITAL DA EMPRESA ---
def desenhar_logo():
    # Renderização da logo em formato adaptado para web/mobile
    st.markdown("<h1 style='text-align: center; color: #00cfcc; margin-bottom: 0px;'>💧</h1>", unsafe_allow_html=True)
    st.markdown("<div class='logo-text'>MENDONÇA POÇOS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-logo'>======= GESTÃO CORPORATIVA =======</div>", unsafe_allow_html=True)

# --- TELA DE LOGIN / SELEÇÃO DE EQUIPE ---
if st.session_state.perfil is None:
    desenhar_logo()
    st.write("Selecione seu perfil para acessar o painel:")
    
    col1, col2 = st.columns(2)
    for idx, t in enumerate(TURMAS):
        c = col1 if idx % 2 == 0 else col2
        if c.button(t):
            st.session_state.perfil = "TURMA"
            st.session_state.turma = t
            st.rerun()
            
    st.divider()
    if st.button("🔑 ACESSO ADMINISTRADOR (ADM)", type="secondary"):
        st.session_state.perfil = "ADM"
        st.rerun()

# --- INTERFACE PRINCIPAL OPERACIONAL ---
else:
    # Top Bar do App
    c_status, c_sair = st.columns([3, 1])
    with c_status:
        identificacao = st.session_state.turma if st.session_state.perfil == "TURMA" else "Gestor Geral (ADM)"
        st.markdown(f"🟢 Logado: **{identificacao}**")
    with c_sair:
        if st.button("Sair"):
            st.session_state.perfil = None
            st.session_state.turma = None
            st.rerun()
            
    desenhar_logo()

    # Separação de menus baseada no perfil logado
    abas_menu = ["Registrar", "Relatório Mensal"]
    if st.session_state.perfil == "ADM":
        abas_menu.append("Painel ADM")
        
    aba1, aba2, *aba3 = st.tabs(abas_menu)

    # --- ABA 1: REGISTRO DE GASTOS SEMANAIS ---
    with aba1:
        if st.session_state.perfil == "ADM":
            st.warning("O perfil Administrador serve apenas para monitoramento corporativo. Faça login como uma das Turmas para registrar gastos.")
        else:
            t_ativa = st.session_state.turma
            trans_semana = st.session_state.dados[t_ativa]["transacoes"]
            
            # Cálculos de consumo da semana
            total_dinheiro = sum(t["valor"] for t in trans_semana if t.get("metodo") == "Dinheiro")
            total_cartao = sum(t["valor"] for t in trans_semana if t.get("metodo") == "Cartão")
            restante_din = LIMITE_DINHEIRO_SEMANAL - total_dinheiro
            
            # Métricas em bloco (estilo app)
            c1, c2 = st.columns(2)
            c1.metric("💵 Dinheiro Espécie", f"R$ {total_dinheiro:.2f}", f"Restante: R$ {restante_din:.2f}")
            c2.metric("💳 Cartão Acumulado", f"R$ {total_cartao:.2f}")
            
            # Barra de progresso visual do dinheiro
            pct_consumido = min(total_dinheiro / LIMITE_DINHEIRO_SEMANAL, 1.0) if LIMITE_DINHEIRO_SEMANAL > 0 else 0
            st.progress(pct_consumido)
            st.caption(f"Progresso de consumo do limite semanal ({int(pct_consumido*100)}%)")
            
            st.subheader("📝 Registrar Lançamento")
            with st.form("form_gasto", clear_on_submit=True):
                categoria_escolhida = st.selectbox("Selecione o que foi gasto", ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar", "Pedágio / Transporte", "Outros"])
                opcao_pgto = st.radio("Qual foi o método de pagamento?", ["💵 Dinheiro em Espécie", "💳 Cartão de Crédito"], horizontal=True)
                valor_input = st.text_input("Valor gasto R$ (Exemplo: 25,50)")
                
                enviado = st.form_submit_button("SALVAR LANÇAMENTO")
                
                if enviado:
                    try:
                        valor_final = float(valor_input.replace(",", "."))
                        if valor_final <= 0:
                            st.error("Insira um valor maior que zero.")
                        else:
                            metodo_final = "Dinheiro" if "Dinheiro" in opcao_pgto else "Cartão"
                            agora = datetime.now()
                            
                            nova_transacao = {
                                "data": agora.strftime("%d/%m %H:%M"),
                                "ano_mes": agora.strftime("%Y-%m"),
                                "categoria": categoria_escolhida,
                                "metodo": metodo_final,
                                "valor": valor_final
                            }
                            
                            st.session_state.dados[t_ativa]["transacoes"].append(nova_transacao)
                            st.session_state.dados[t_ativa]["historico"].append(nova_transacao)
                            salvar_dados(st.session_state.dados)
                            st.success("✓ Gasto registrado de forma permanente!")
                            st.rerun()
                    except ValueError:
                        st.error("Entrada inválida. Digite apenas números no campo de valor.")

            st.write("**Gastos Recentes da Semana Atual:**")
            if trans_semana:
                for t in reversed(trans_semana[-5:]):
                    icone = "💵" if t["metodo"] == "Dinheiro" else "💳"
                    st.markdown(f"{icone} **{t['data']}** - {t['categoria']} - `R$ {t['valor']:.2f}`")
            else:
                st.caption("Nenhum gasto registrado nesta semana.")

    # --- ABA 2: HISTÓRICO MENSAL ARQUIVADO ---
    with aba2:
        st.subheader("📅 Histórico Mensal")
        
        # Seleção de escopo para o ADM poder auditar equipes individualmente
        target_turma = st.session_state.turma
        if st.session_state.perfil == "ADM":
            target_turma = st.selectbox("Selecione a frente para conferência", TURMAS)
            
        historico_alvo = st.session_state.dados[target_turma]["historico"]
        meses_disponiveis = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in historico_alvo)), reverse=True)
        
        if meses_disponiveis:
            mes_sel = st.selectbox("Escolha o mês de referência", meses_disponiveis)
            transacoes_mes = [t for t in historico_alvo if t.get("ano_mes", "") == mes_sel]
            
            tot_din_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Dinheiro")
            tot_car_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Cartão")
            
            st.info(f"💰 **Total Período:** 💵 Dinheiro: R$ {tot_din_mes:.2f} | 💳 Cartão: R$ {tot_car_mes:.2f}")
            
            st.write("**Lançamentos do Mês:**")
            for t in reversed(transacoes_mes):
                icone = "💵" if t["metodo"] == "Dinheiro" else "💳"
                st.markdown(f"{icone} **{t['data']}** - {t['categoria']} - `R$ {t['valor']:.2f}`")
        else:
            st.write("Nenhum dado permanente arquivado nesta conta.")

    # --- ABA 3: PAINEL DE CONTROLE ADM (CENTRAL GLOBAL) ---
    if st.session_state.perfil == "ADM":
        with aba3[0]:
            st.subheader("🚨 Ferramentas de Gestão Central")
            st.write("Esta ação zera instantaneamente o balanço e as barras semanais das 6 equipes em campo, preservando os históricos arquivados.")
            
            if st.button("RESETAR SEMANA DE TODAS AS TURMAS"):
                for t in TURMAS:
                    st.session_state.dados[t]["transacoes"] = []
                salvar_dados(st.session_state.dados)
                st.success("🚨 O balanço e as barras da semana de todas as equipes foram limpos com sucesso!")
                st.rerun()
