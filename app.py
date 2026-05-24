import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "gastos_dados.json"
LIMITE_DINHEIRO_SEMANAL = 500.00

# Configuração da página do App
st.set_page_config(page_title="Mendonça Poços Finanças", page_icon="📊", layout="centered")

# 1. Inicializa ou carrega os dados salvos estruturando o histórico permanente
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                
                # Migração/Adaptação caso o JSON antigo seja uma lista simples ou formato anterior
                if isinstance(dados, list):
                    dados = {"transacoes": dados, "historico": []}
                if "transacoes" not in dados:
                    dados["transacoes"] = []
                if "historico" not in dados:
                    dados["historico"] = []
                    
                return dados
            except json.JSONDecodeError:
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

# --- CALCULOS DOS GASTOS ---
total_dinheiro = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo") == "Dinheiro")
total_cartao = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo") == "Cartão")
restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_dinheiro

# --- DASHBOARD DE CARDS VISUAIS ---
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
# Barra de progresso visual interativa do dinheiro
progresso = min(total_dinheiro / LIMITE_DINHEIRO_SEMANAL, 1.0)
st.progress(progresso)

# --- ABA DE OPERAÇÕES DO MENU ---
aba_inserir, aba_historico, aba_config = st.tabs(["📝 Registrar Gasto", "📅 Histórico Mensal", "⚙️ Ajustes Semanais"])

# 2. Fluxo de inserção de novos gastos
with aba_inserir:
    st.markdown("### Lançar Nova Despesa")
    with st.form("form_gasto", clear_on_submit=True):
        categorias = ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar", "Pedágio / Transporte", "Outros"]
        categoria_escolhida = st.selectbox("Selecione o que foi gasto:", categorias)
        
        opcao_pgto = st.radio("Qual foi o método de pagamento?", ["Dinheiro em Espécie", "Cartão de Crédito"], horizontal=True)
        metodo = "Dinheiro" if opcao_pgto == "Dinheiro em Espécie" else "Cartão"
        
        valor = st.number_input("Valor gasto R$", min_value=0.0, step=1.0, format="%.2f")
        botao_salvar = st.form_submit_button("SALVAR LANÇAMENTO")

    if botao_salvar:
        if valor > 0:
            agora = datetime.now()
            nova_transacao = {
                "data": agora.strftime("%d/%m %H:%M"),
                "ano_mes": agora.strftime("%Y-%m"),
                "semana_ano": agora.strftime("%U"),
                "categoria": categoria_escolhida,
                "metodo": metodo,
                "valor": valor
            }
            
            dados["transacoes"].append(nova_transacao)
            dados["historico"].append(nova_transacao)
            salvar_dados(dados)
            st.success("✓ Gasto registrado com sucesso de forma permanente!")
            st.rerun()
        else:
            st.error("Por favor, digite um valor maior que zero.")

    # Tabela de Histórico Recente da Semana Ativa
    st.markdown("#### Gastos da Semana Atual")
    if dados["transacoes"]:
        for t in reversed(dados["transacoes"][-6:]):
            emoji = "💳" if t.get("metodo") == "Cartão" else "💵"
            cor = "magenta" if t.get("metodo") == "Cartão" else "cyan"
            st.markdown(f"**{emoji} {t['categoria']}** | <span style='color:{cor};'>{t['metodo']}</span> | **R$ {t['valor']:.2f}** *({t['data']})*", unsafe_allow_html=True)
    else:
        st.info("Nenhum lançamento registrado nesta semana.")

# 3. Exibe os meses disponíveis e filtra os dados salvos permanentemente
with aba_historico:
    st.markdown("### Arquivo de Transações")
    if not dados["historico"]:
        st.info("Nenhum dado arquivado ainda no histórico permanente.")
    else:
        meses_disponiveis = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in dados["historico"])), reverse=True)
        
        opcoes_formatadas = []
        for mes in meses_disponiveis:
            ano, mes_num = mes.split("-")
            opcoes_formatadas.append(f"{mes_num}/{ano}")
            
        mes_selecionado_formatado = st.selectbox("Selecione o mês para consulta:", opcoes_formatadas)
        
        # Converte de volta "05/2026" para "2026-05" para filtrar o JSON
        mes_num_sel, ano_sel = mes_selecionado_formatado.split("/")
        mes_escolhido = f"{ano_sel}-{mes_num_sel}"
        
        transacoes_mes = [t for t in dados["historico"] if t.get("ano_mes", "") == mes_escolhido]
        
        total_din_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Dinheiro")
        total_card_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Cartão")
        
        st.markdown(f"**💵 Total em Dinheiro:** R$ {total_din_mes:.2f}")
        st.markdown(f"**💳 Total no Cartão:** R$ {total_card_mes:.2f}")
        st.divider()
        
        for t in reversed(transacoes_mes):
            emoji = "💳" if t.get("metodo") == "Cartão" else "💵"
            st.markdown(f"**{t['data']}** - {emoji} {t['categoria']} - R$ {t['valor']:.2f}")

# 4. Ajustes e Viradas de folha
with aba_config:
    st.markdown("### Administração do Sistema")
    st.warning("Atenção: A ação abaixo limpa o painel da semana ativa, mas mantém o histórico mensal salvo.")
    if st.button("🚨 Resetar Balanço Semanal (Zerar Barras)", type="primary"):
        dados["transacoes"] = []
        salvar_dados(dados)
        st.success("✓ Balanço da semana resetado com sucesso!")
        st.rerun()
