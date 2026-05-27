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
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .logo-text {
        text-align: center;
        font-weight: bold;
        color: white;
        font-size: 24px;
        letter-spacing: 2px;
        margin-top: 5px;
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

# --- USUÁRIOS E SENHAS ---
CREDENCIAIS = {
    "Rafael": "raf123",
    "Ednaldo": "edn123",
    "Luiz Felipe": "luiz123",
    "Carlos": "car123",
    "Cardoso": "card123",
    "Guilherme": "gui123",
    "Paulo": "pau123",
    "ADM": "adm9988"
}

TURMAS = [nome for nome in CREDENCIAIS.keys() if nome != "ADM"]

# --- FUNÇÕES DE ARMAZENAMENTO ISOLADO ---
def carregar_dados():
    estrutura_limpa = {t: {"transacoes": [], "historico": [], "pocos": []} for t in TURMAS}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                if "transacoes" in dados or isinstance(dados, list):
                    return estrutura_limpa
                # Garante que chaves novas como 'pocos' existam mesmo em arquivos antigos
                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {"transacoes": [], "historico": [], "pocos": []}
                    if "pocos" not in dados[t]:
                        dados[t]["pocos"] = []
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
if 'selecionou_usuario' not in st.session_state:
    st.session_state.selecionou_usuario = None

# --- DESIGN DA LOGO DA EMPRESA ---
def desenhar_logo():
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("<h1 style='text-align: center; color: #00cfcc; margin-bottom: 0px;'>💧</h1>", unsafe_allow_html=True)
    st.markdown("<div class='logo-text'>MENDONÇA POÇOS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-logo'>======= GESTÃO CORPORATIVA =======</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- TELA DE LOGIN / SELEÇÃO DE EQUIPE ---
if st.session_state.perfil is None:
    desenhar_logo()
    
    if st.session_state.selecionou_usuario is None:
        st.write("Identifique-se para entrar no aplicativo:")
        
        # Botão principal limpo que oculta tudo
        if st.button("🔐 ACESSAR SISTEMA"):
            st.session_state.selecionou_usuario = "FUNCIONARIO_FORM"
            st.rerun()
                
        st.divider()
        if st.button("🔑 ACESSO ADMINISTRADOR (ADM)", type="secondary"):
            st.session_state.selecionou_usuario = "ADM_SENHA"
            st.rerun()
            
    # Formulário de login manual para os funcionários (Ocultando a lista de nomes)
    elif st.session_state.selecionou_usuario == "FUNCIONARIO_FORM":
        st.subheader("Login de Colaborador")
        usuario_digitado = st.text_input("Digite seu Nome (Usuário)")
        senha_digitada = st.text_input("Digite sua Senha", type="password")
        
        c_voltar, c_entrar = st.columns(2)
        if c_voltar.button("Voltar"):
            st.session_state.selecionou_usuario = None
            st.rerun()
            
        if c_entrar.button("Entrar"):
            # Validação se o usuário existe nas chaves e se a senha está correta
            if usuario_digitado in CREDENCIAIS and usuario_digitado != "ADM":
                if senha_digitada == CREDENCIAIS[usuario_digitado]:
                    st.session_state.perfil = "TURMA"
                    st.session_state.turma = usuario_digitado
                    st.session_state.selecionou_usuario = None
                    st.rerun()
                else:
                    st.error("Senha incorreta! Tente novamente.")
            else:
                st.error("Usuário não encontrado. Verifique se escreveu o nome corretamente.")

    # Formulário de verificação do ADM corporativo
    elif st.session_state.selecionou_usuario == "ADM_SENHA":
        st.write("Digite a senha master para o perfil: **ADM**")
        senha_adm = st.text_input("Senha ADM", type="password")
        
        c_voltar, c_entrar = st.columns(2)
        if c_voltar.button("Voltar"):
            st.session_state.selecionou_usuario = None
            st.rerun()
            
        if c_entrar.button("Entrar como ADM"):
            if senha_adm == CREDENCIAIS["ADM"]:
                st.session_state.perfil = "ADM"
                st.session_state.selecionou_usuario = "ADM_MONITORAMENTO" # Mantém os botões ativos só aqui dentro
                st.rerun()
            else:
                st.error("Senha de Administrador incorreta!")

    # Painel exclusivo de monitoramento visual do ADM na raiz do login (apenas se ele quiser selecionar alguém para ver direto)
    elif st.session_state.selecionou_usuario == "ADM_MONITORAMENTO":
        st.subheader("Painel de Monitoramento (ADM)")
        st.write("Selecione uma das equipes abaixo para auditar ou clique em 'Entrar no Painel Geral':")
        
        col1, col2 = st.columns(2)
        for idx, t in enumerate(TURMAS):
            c = col1 if idx % 2 == 0 else col2
            if c.button(f"Ver {t}"):
                st.session_state.perfil = "TURMA"
                st.session_state.turma = t
                st.session_state.selecionou_usuario = None
                st.rerun()
                
        st.divider()
        if st.button("Ir para o Painel Geral Consolidado 📊"):
            st.session_state.selecionou_usuario = None
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
            st.session_state.selecionou_usuario = None
            st.rerun()
            
    desenhar_logo()

    # Separação de menus baseada no perfil logado
    abas_menu = ["Registrar", "Relatório Mensal"]
    if st.session_state.perfil == "ADM":
        abas_menu.append("Painel ADM")
        
    aba1, aba2, *aba3 = st.tabs(abas_menu)

    # --- ABA 1: REGISTRO DE GASTOS E PRODUÇÃO ---
    with aba1:
        if st.session_state.perfil == "ADM":
            st.warning("O perfil Administrador serve apenas para monitoramento corporativo. Faça login com o nome de um colaborador para registrar dados de campo.")
        else:
            t_ativa = st.session_state.turma
            trans_semana = st.session_state.dados[t_ativa]["transacoes"]
            pocos_registrados = st.session_state.dados[t_ativa].get("pocos", [])
            
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
            
            st.divider()
            
            # --- ÁREA 1 OCULTA: REGISTRO DE DESPESAS ---
            mostrar_painel = st.toggle("📝 Registrar Despesas", value=False)
            if mostrar_painel:
                st.subheader("Nova Despesa")
                
                categoria_pai = st.selectbox(
                    "Selecione o que foi gasto", 
                    ["Café da Manhã", "Almoço", "Outros"]
                )
                
                sub_categoria = "Nenhum"
                detalhe_texto = ""
                
                if categoria_pai == "Outros":
                    st.markdown("⬇️ **Selecione o tipo de despesa extra:**")
                    sub_categoria = st.radio("Subcategoria", ["Mecânica", "Pedágio", "Transportes", "Escrever motivo próprio"], horizontal=True)
                    if sub_categoria == "Escrever motivo próprio":
                        detalhe_texto = st.text_input("Escreva detalhadamente o que foi gasto:")

                with st.form("form_final_envio", clear_on_submit=True):
                    opcao_pgto = st.radio("Qual foi o método de pagamento?", ["💵 Dinheiro em Espécie", "💳 Cartão de Crédito"], horizontal=True)
                    valor_input = st.text_input("Valor gasto R$ (Exemplo: 25,50)")
                    
                    enviado = st.form_submit_button("CONFIRMAR E SALVAR LANÇAMENTO")
                    
                    if enviado:
                        try:
                            valor_final = float(valor_input.replace(",", "."))
                            if valor_final <= 0:
                                st.error("Insira um valor maior que zero.")
                            else:
                                metodo_final = "Dinheiro" if "Dinheiro" in opcao_pgto else "Cartão"
                                agora = datetime.now()
                                
                                if categoria_pai == "Outros":
                                    if sub_categoria == "Escrever motivo próprio" and detalhe_texto.strip() != "":
                                        categoria_final = f"Outros ({detalhe_texto.strip()})"
                                    else:
                                        categoria_final = f"{sub_categoria}"
                                else:
                                    categoria_final = categoria_pai
                                
                                nova_transacao = {
                                    "data": agora.strftime("%d/%m %H:%M"),
                                    "ano_mes": agora.strftime("%Y-%m"),
                                    "categoria": categoria_final,
                                    "metodo": metodo_final,
                                    "valor": valor_final
                                }
                                
                                st.session_state.dados[t_ativa]["transacoes"].append(nova_transacao)
                                st.session_state.dados[t_ativa]["historico"].append(nova_transacao)
                                salvar_dados(st.session_state.dados)
                                st.success("✓ Gasto registrado com sucesso!")
                                st.rerun()
                        except ValueError:
                            st.error("Entrada inválida. Digite apenas números no campo de valor.")

                st.divider()
                st.write("**Gastos Recentes da Semana Atual:**")
                if trans_semana:
                    for t in reversed(trans_semana[-5:]):
                        icone = "💵" if t["metodo"] == "Dinheiro" else "💳"
                        st.markdown(f"{icone} **{t['data']}** - {t['categoria']} - `R$ {t['valor']:.2f}`")
                else:
                    st.caption("Nenhum gasto registrado nesta semana.")

            # --- ÁREA 2 OCULTA: POÇOS PERFURADOS ---
            mostrar_pocos = st.toggle("🚰 Poços Perfurados", value=False)
            if mostrar_pocos:
                st.subheader("Relatório de Poço Concluído")
                
                with st.form("form_pocos_perfurados", clear_on_submit=True):
                    data_poco = st.text_input("Data da conclusão (dia/mês/ano)", value=datetime.now().strftime("%d/%m/%Y"))
                    cidade_poco = st.text_input("Cidade onde o poço foi feito")
                    metragem_poco = st.text_input("Metragem total finalizada (Ex: 85 metros)")
                    material_poco = st.text_area("Materiais de tubulação utilizados no poço")
                    
                    enviar_poco = st.form_submit_button("SALVAR RELATÓRIO DO POÇO")
                    
                    if enviar_poco:
                        if not cidade_poco or not metragem_poco or not material_poco:
                            st.error("Por favor, preencha todos os campos do formulário antes de salvar.")
                        else:
                            novo_poco = {
                                "data": data_poco,
                                "ano_mes": datetime.now().strftime("%Y-%m"),
                                "cidade": cidade_poco,
                                "metragem": metragem_poco,
                                "material": material_poco
                            }
                            if "pocos" not in st.session_state.dados[t_ativa]:
                                st.session_state.dados[t_ativa]["pocos"] = []
                                
                            st.session_state.dados[t_ativa]["pocos"].append(novo_poco)
                            salvar_dados(st.session_state.dados)
                            st.success("✓ Relatório do poço arquivado com sucesso!")
                            st.rerun()
                
                st.divider()
                st.write("**Histórico de Poços Feitos por Você:**")
                if pocos_registrados:
                    for idx, p in enumerate(reversed(pocos_registrados)):
                        with st.expander(f"📍 {p['data']} - {p['cidade']} ({p['metragem']})"):
                            st.write(f"**Material Utilizado:**\n{p['material']}")
                else:
                    st.caption("Nenhum poço registrado nesta conta.")

    # --- ABA 2: HISTÓRICO MENSAL ARQUIVADO (VISÃO DE RELATÓRIO) ---
    with aba2:
        st.subheader("📅 Histórico Mensal")
        
        target_turma = st.session_state.turma
        if st.session_state.perfil == "ADM":
            target_turma = st.selectbox("Selecione o colaborador para conferência", TURMAS)
            
        historico_alvo = st.session_state.dados[target_turma]["historico"]
        pocos_alvo = st.session_state.dados[target_turma].get("pocos", [])
        meses_disponiveis = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in historico_alvo + pocos_alvo)), reverse=True)
        
        if meses_disponiveis:
            mes_sel = st.selectbox("Escolha o mês de referência", meses_disponiveis)
            
            sub_aba_financeiro, sub_aba_producao = st.tabs(["💰 Controle de Custos", "🚰 Poços Executados"])
            
            with sub_aba_financeiro:
                transacoes_mes = [t for t in historico_alvo if t.get("ano_mes", "") == mes_sel]
                tot_din_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Dinheiro")
                tot_car_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Cartão")
                
                st.info(f"💰 **Total Período:** 💵 Dinheiro: R$ {tot_din_mes:.2f} | 💳 Cartão: R$ {tot_car_mes:.2f}")
                for t in reversed(transacoes_mes):
                    icone = "💵" if t["metodo"] == "Dinheiro" else "💳"
                    st.markdown(f"{icone} **{t['data']}** - {t['categoria']} - `R$ {t['valor']:.2f}`")
                    
            with sub_aba_producao:
                pocos_mes = [p for p in pocos_alvo if p.get("ano_mes", "") == mes_sel]
                if pocos_mes:
                    for p in reversed(pocos_mes):
                        st.markdown(f"🟩 **Data:** {p['data']} | **Cidade:** {p['cidade']} | **Metragem:** {p['metragem']}")
                        st.caption(f"**Materiais aplicados:** {p['material']}")
                        st.divider()
                else:
                    st.caption("Nenhum poço registrado por esta equipe no mês selecionado.")
        else:
            st.write("Nenhum dado permanente arquivado nesta conta.")

    # --- ABA 3: PAINEL DE CONTROLE ADM (CENTRAL GLOBAL) ---
    if st.session_state.perfil == "ADM":
        with aba3[0]:
            st.subheader("🚨 Ferramentas de Gestão Central")
            st.write("Esta ação zera instantaneamente o balanço e as barras semanais de todos os colaboradores para iniciar o controle da nova semana. O histórico acumulado do mês NÃO é modificado.")
            
            if st.button("RESETAR GASTOS DA SEMANA (FECHAR SEMANA)"):
                for t in TURMAS:
                    st.session_state.dados[t]["transacoes"] = []
                salvar_dados(st.session_state.dados)
                st.success("🚨 Semana fechada com sucesso! Todos os gráficos voltaram a zero e as turmas estão prontas para a nova semana.")
                st.rerun()
