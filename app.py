import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "gastos_dados.json"
LIMITE_DINHEIRO_SEMANAL = 500.00

# Configuração da página do App
st.set_page_config(page_title="Mendonça Poços Finanças", page_icon="📊", layout="centered")

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                if isinstance(dados, list): 
                    dados = {"transacoes": dados, "historico": []}
                return dados
            except:
                return {"transacoes": [], "historico": []}
    return {"transacoes": [], "historico": []}

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# --- TOPO DO APLICATIVO ---
st.markdown("<h1 style='text-align: center; color: #00bcd4;'>MENDONÇA POÇOS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>POÇOS ARTESIANOS • GESTÃO FINANCEIRA</p>", unsafe_allow_html=True)
st.divider()

# --- DASHBOARD DE CARDS ---
total_dinheiro = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo") == "Dinheiro")
total_cartao = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo") == "Cartão")
restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_dinheiro

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background-color: #1e222b; padding: 15px; border-radius: 10px; border-left: 5px solid #00bcd4;'>
        <span style='color: #888; font-size: 12px;'>💵 DINHEIRO EM ESPÉCIE</span><br>
        <b style='font-size: 22px; color: white;'>R$ {total_dinheiro:.2f}</b><br>
        <span style='color: #4caf50; font-size: 12px;'>Restante: R$ {restante_dinheiro:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: #1e222b; padding: 15px; border-radius: 10px; border-left: 5px solid #e91e63;'>
        <span style='color: #888; font-size: 12px;'>💳 CARTÃO CORPORATIVO</span><br>
        <b style='font-size: 22px; color: white;'>R$ {total_cartao:.2f}</b><br>
        <span style='color: #888; font-size: 12px;'>Acumulado do Mês</span>
    </div>
    """, unsafe_allow_html=True)

st.write("")
# Barra de progresso visual do dinheiro
progresso = min(total_dinheiro / LIMITE_DINHEIRO_SEMANAL, 1.0)
st.progress(progresso)

# --- FORMULÁRIO DE CADASTRO ---
st.markdown("### 📝 Registrar Novo Gasto")
with st.form("form_gasto", clear_on_submit=True):
    categoria = st.selectbox("Selecione o Gasto", ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar", "Pedágio / Transporte", "Outros"])
    metodo = st.radio("Forma de Pagamento", ["Dinheiro", "Cartão"], horizontal=True)
    valor = st.number_input("Valor gasto R$", min_value=0.0, step=1.0, format="%.2f")
    botao_salvar = st.form_submit_button("Salvar Lançamento")

if botao_salvar:
    if valor > 0:
        agora = datetime.now()
        nova_transacao = {
            "data": agora.strftime("%d/%m %H:%M"),
            "ano_mes": agora.strftime("%Y-%m"),
            "categoria": categoria,
            "metodo": metodo,
            "valor": valor
        }
        dados["transacoes"].append(nova_transacao)
        dados["historico"].append(nova_transacao)
        salvar_dados(dados)
        st.success("Gasto registrado com sucesso!")
        st.rerun()

# --- HISTÓRICO ---
st.markdown("### 📅 Gastos Recentes da Semana")
for t in reversed(dados["transacoes"][-5:]):
    emoji = "💳" if t.get("metodo") == "Cartão" else "💵"
    st.markdown(f"**{emoji} {t['categoria']}** | R$ {t['valor']:.2f} *({t['data']} - {t['metodo']})*")

if st.button("🚨 Resetar Virada de Semana", type="primary"):
    dados["transacoes"] = []
    salvar_dados(dados)
    st.warning("Semana resetada!")
    st.rerun()
