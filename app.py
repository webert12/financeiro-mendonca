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

# Estilização para parecer um App (Cores da empresa)
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
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "gastos_dados.json"
LIMITE_SEMANAL = 500.00
TURMAS = [f"Turma {i}" for i in range(1, 7)]

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                # Garante que todas as turmas existam
                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {"transacoes": [], "historico": []}
                return dados
            except: pass
    
    return {t: {"transacoes": [], "historico": []} for t in TURMAS}

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

# Inicialização
if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()
if 'perfil' not in st.session_state:
    st.session_state.perfil = None
if 'turma' not in st.session_state:
    st.session_state.turma = None

# --- TELA DE LOGIN (INTERFACE DE ENTRADA) ---
if st.session_state.perfil is None:
    st.title("💧 Mendonça Poços")
    st.write("Selecione seu perfil para acessar:")
    
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

# --- INTERFACE DO APP (LOGADO) ---
else:
    # Cabeçalho do App
    with st.container():
        c_status, c_sair = st.columns([3, 1])
        c_status.markdown(f"👤 **{st.session_state.turma if st.session_state.turma else 'Gestor ADM'}**")
        if c_sair.button("Sair"):
            st.session_state.perfil = None
            st.session_state.turma = None
            st.rerun()

    # Lógica de Abas (Navegação APK)
    menu = ["Registrar", "Relatórios"]
    if st.session_state.perfil == "ADM":
        menu.append("Gestão ADM")
    
    aba1, aba2, *aba3 = st.tabs(menu)

    # --- ABA: REGISTRAR GASTOS ---
    with aba1:
        if st.session_state.perfil == "ADM":
            st.warning("O perfil ADM é apenas para consulta. Acesse como Turma para lançar.")
        else:
            st.subheader("📝 Novo Lançamento")
            
            # Cálculos
            t_nome = st.session_state.turma
            trans_semana = st.session_state.dados[t_nome]["transacoes"]
            gasto_din = sum(t["valor"] for t in trans_semana if t["metodo"] == "Dinheiro")
            gasto_car = sum(t["valor"] for t in trans_semana if t["metodo"] == "Cartão")
            
            # Cards de visualização
            col_din, col_car = st.columns(2)
            col_din.metric("Dinheiro Gasto", f"R$ {gasto_din:.2f}", f"Restante: {LIMITE_SEMANAL-gasto_din:.2f}")
            col_car.metric("Cartão Total", f"R$ {gasto_car:.2f}")
            
            st.progress(min(gasto_din/LIMITE_SEMANAL, 1.0))
            
            # Formulário
            with st.form("registro_gasto", clear_on_submit=True):
                cat = st.selectbox("Categoria", ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar", "Pedágio", "Outros"])
                met = st.radio("Pagamento", ["💵 Dinheiro", "💳 Cartão"], horizontal=True)
                val = st.text_input("Valor (Ex: 25,50)")
                
                botao_salvar = st.form_submit_button("SALVAR GASTO")

                if botao_salvar:
                    try:
                        v = float(val.replace(",", "."))
                        metodo_limpo = "Dinheiro" if "Dinheiro" in met else "Cartão"
                        agora = datetime.now()
                        
                        novo = {
                            "data": agora.strftime("%d/%m %H:%M"),
                            "ano_mes": agora.strftime("%Y-%m"),
                            "categoria": cat,
                            "metodo": metodo_limpo,
                            "valor": v
                        }
                        
                        st.session_state.dados[t_nome]["transacoes"].append(novo)
                        st.session_state.dados[t_nome]["historico"].append(novo)
                        salvar_dados(st.session_state.dados)
                        st.success("Salvo com sucesso!")
                        st.rerun()
                    except:
                        st.error("Valor inválido. Digite apenas números.")

            st.write("**Últimos gastos da semana:**")
            for t in reversed(trans_semana[-3:]):
                st.caption(f"{t['data']} - {t['categoria']} - R$ {t['valor']:.2f} ({t['metodo']})")

    # --- ABA: RELATÓRIOS ---
    with aba2:
        st.subheader("📅 Histórico")
        
        target = st.session_state.turma
        if st.session_state.perfil == "ADM":
            target = st.selectbox("Escolha a Turma", TURMAS)
        
        hist = st.session_state.dados[target]["historico"]
        meses = sorted(list(set(t["ano_mes"] for t in hist)), reverse=True)
        
        if meses:
            mes_sel = st.selectbox("Mês de Referência", meses)
            dados_mes = [t for t in hist if t["ano_mes"] == mes_sel]
            
            t_din = sum(t["valor"] for t in dados_mes if t["metodo"] == "Dinheiro")
            t_car = sum(t["valor"] for t in dados_mes if t["metodo"] == "Cartão")
            
            st.info(f"💵 Dinheiro: R$ {t_din:.2f} | 💳 Cartão: R$ {t_car:.2f}")
            
            for t in reversed(dados_mes):
                st.markdown(f"**{t['data']}** - {t['categoria']} - `R$ {t['valor']:.2f}`")
        else:
            st.write("Nenhum registro encontrado para esta turma.")

    # --- ABA: GESTÃO ADM ---
    if st.session_state.perfil == "ADM":
        with aba3[0]:
            st.subheader("⚙️ Painel de Controle")
            st.write("Ação global para todas as 6 turmas:")
            
            if st.button("🚨 RESETAR SEMANA (TODAS AS TURMAS)"):
                for t in TURMAS:
                    st.session_state.dados[t]["transacoes"] = []
                salvar_dados(st.session_state.dados)
                st.success("Barras zeradas e limpas para todas as equipes!")
                st.rerun()
