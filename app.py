import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" ---
st.set_page_config(page_title="Mendonça Poços", page_icon="💧", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style> .stApp { background-color: #f0f2f6; } </style>""", unsafe_allow_html=True)

DATA_FILE = "gastos_dados.json"
MIDIA_DIR = "uploads_midias"
if not os.path.exists(MIDIA_DIR): os.makedirs(MIDIA_DIR)

LIMITE_DINHEIRO_SEMANAL = 500.00

# --- USUÁRIOS E SENHAS ---
CREDENCIAIS = {"Rafael": "raf123", "Ednaldo": "edn123", "Luiz Felipe": "luiz123", "Carlos": "car123", "Cardoso": "card123", "Guilherme": "gui123", "Paulo": "pau123", "ADM": "adm9988"}
TURMAS = [nome for nome in CREDENCIAIS.keys() if nome != "ADM"]

# --- FUNÇÕES DE ARMAZENAMENTO ISOLADO ---
def carregar_dados():
    estrutura_limpa = {t: {"transacoes": [], "historico": [], "pocos": [], "midias": []} for t in TURMAS}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                for t in TURMAS:
                    if t not in dados: dados[t] = {"transacoes": [], "historico": [], "pocos": [], "midias": []}
                    if "midias" not in dados[t]: dados[t]["midias"] = []
                return dados
            except: return estrutura_limpa
    return estrutura_limpa

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)

# Inicialização do Estado da Sessão
if 'dados' not in st.session_state: st.session_state.dados = carregar_dados()
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'turma' not in st.session_state: st.session_state.turma = None
if 'selecionou_usuario' not in st.session_state: st.session_state.selecionou_usuario = None

# --- DESIGN DA LOGO DA EMPRESA ---
def desenhar_logo():
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    else: st.markdown("<center><h1>💧</h1></center>", unsafe_allow_html=True)
    st.markdown("<center>MENDONÇA POÇOS</center>", unsafe_allow_html=True)
    st.markdown("<center>======= GESTÃO CORPORATIVA =======</center>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# --- TELA DE LOGIN / SELEÇÃO DE EQUIPE ---
if st.session_state.perfil is None:
    desenhar_logo()
    if st.session_state.selecionou_usuario is None:
        st.write("Identifique-se para entrar no aplicativo:")
        if st.button("🔐 ACESSAR SISTEMA"): st.session_state.selecionou_usuario = "FUNCIONARIO_FORM"; st.rerun()
        st.divider()
        if st.button("🔑 ACESSO ADMINISTRADOR (ADM)", type="secondary"): st.session_state.selecionou_usuario = "ADM_SENHA"; st.rerun()
    elif st.session_state.selecionou_usuario == "FUNCIONARIO_FORM":
        st.subheader("Login de Colaborador")
        usuario_digitado = st.text_input("Digite seu Nome (Usuário)")
        senha_digitada = st.text_input("Digite sua Senha", type="password")
        c_voltar, c_entrar = st.columns(2)
        if c_voltar.button("Voltar"): st.session_state.selecionou_usuario = None; st.rerun()
        if c_entrar.button("Entrar"):
            if usuario_digitado in CREDENCIAIS and usuario_digitado != "ADM":
                if senha_digitada == CREDENCIAIS[usuario_digitado]:
                    st.session_state.perfil = "TURMA"; st.session_state.turma = usuario_digitado; st.session_state.selecionou_usuario = None; st.rerun()
                else: st.error("Senha incorreta!")
            else: st.error("Usuário não encontrado.")
    elif st.session_state.selecionou_usuario == "ADM_SENHA":
        st.write("Digite a senha master para o perfil: **ADM**")
        senha_adm = st.text_input("Senha ADM", type="password")
        c_voltar, c_entrar = st.columns(2)
        if c_voltar.button("Voltar"): st.session_state.selecionou_usuario = None; st.rerun()
        if c_entrar.button("Entrar como ADM"):
            if senha_adm == CREDENCIAIS["ADM"]: st.session_state.perfil = "ADM"; st.session_state.selecionou_usuario = "ADM_MONITORAMENTO"; st.rerun()
            else: st.error("Senha de Administrador incorreta!")
    elif st.session_state.selecionou_usuario == "ADM_MONITORAMENTO":
        st.subheader("Painel de Monitoramento (ADM)")
        col1, col2 = st.columns(2)
        for idx, t in enumerate(TURMAS):
            c = col1 if idx % 2 == 0 else col2
            if c.button(f"Ver {t}"): st.session_state.perfil = "TURMA"; st.session_state.turma = t; st.session_state.selecionou_usuario = None; st.rerun()
        st.divider()
        if st.button("Ir para o Painel Geral Consolidado 📊"): st.session_state.selecionou_usuario = None; st.rerun()

# --- INTERFACE PRINCIPAL OPERACIONAL ---
else:
    c_status, c_sair = st.columns([3, 1])
    with c_status:
        identificacao = st.session_state.turma if st.session_state.perfil == "TURMA" else "Gestor Geral (ADM)"
        st.markdown(f"🟢 Logado: {identificacao}")
    with c_sair:
        if st.button("Sair"): st.session_state.perfil = None; st.session_state.turma = None; st.session_state.selecionou_usuario = None; st.rerun()
    
    desenhar_logo()
    abas_menu = ["Registrar", "Relatório Mensal"]
    if st.session_state.perfil == "ADM": abas_menu.append("Painel ADM")
    
    aba1, aba2, *aba3 = st.tabs(abas_menu)
    
    with aba1:
        if st.session_state.perfil == "ADM": st.warning("O perfil Administrador serve apenas para monitoramento.")
        else:
            t_ativa = st.session_state.turma
            trans_semana = st.session_state.dados[t_ativa]["transacoes"]
            c1, c2 = st.columns(2)
            c1.metric("💵 Dinheiro", f"R$ {sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Dinheiro'):.2f}")
            c2.metric("💳 Cartão", f"R$ {sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Cartão'):.2f}")
            
            if st.toggle("📝 Registrar Despesas", value=False):
                with st.form("form_final_envio", clear_on_submit=True):
                    cat = st.selectbox("Categoria", ["Café da Manhã", "Almoço", "Outros"])
                    opcao_pgto = st.radio("Método de Pagamento", ["💵 Dinheiro", "💳 Cartão"], horizontal=True)
                    valor_input = st.text_input("Valor R$")
                    if st.form_submit_button("SALVAR"):
                        valor_final = float(valor_input.replace(",", "."))
                        novo_trans = {"data": datetime.now().strftime("%d/%m %H:%M"), "ano_mes": datetime.now().strftime("%Y-%m"), "categoria": cat, "metodo": "Dinheiro" if "Dinheiro" in opcao_pgto else "Cartão", "valor": valor_final}
                        st.session_state.dados[t_ativa]["transacoes"].append(novo_trans)
                        st.session_state.dados[t_ativa]["historico"].append(novo_trans)
                        salvar_dados(st.session_state.dados); st.rerun()
            
            if st.toggle("🚰 Poços Perfurados", value=False):
                with st.form("form_pocos", clear_on_submit=True):
                    cl = st.text_input("Cliente"); ci = st.text_input("Cidade"); mt = st.text_input("Metragem"); mat = st.text_area("Material"); fun = st.text_input("Funcionários")
                    if st.form_submit_button("SALVAR RELATÓRIO"):
                        st.session_state.dados[t_ativa]["pocos"].append({"data": datetime.now().strftime("%d/%m/%Y"), "ano_mes": datetime.now().strftime("%Y-%m"), "cliente": cl, "cidade": ci, "metragem": mt, "material": mat, "funcionarios": fun})
                        salvar_dados(st.session_state.dados); st.rerun()

    with aba2:
        st.subheader("📅 Histórico Mensal")
        target_turma = st.session_state.turma if st.session_state.perfil == "TURMA" else st.selectbox("Selecione o Colaborador", TURMAS)
        hist = st.session_state.dados[target_turma]["historico"]
        pocos = st.session_state.dados[target_turma].get("pocos", [])
        midias = st.session_state.dados[target_turma].get("midias", [])
        
        meses = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in hist + pocos)), reverse=True)
        if meses:
            mes_sel = st.selectbox("Escolha o mês", meses)
            
            # Configuração das abas internas (Mídias apenas para Funcionário)
            if st.session_state.perfil == "TURMA":
                sub_f, sub_p, sub_m = st.tabs(["💰 Custos", "🚰 Poços", "📸 Mídias"])
            else:
                sub_f, sub_p = st.tabs(["💰 Custos", "🚰 Poços"])

            with sub_f:
                t_mes = [t for t in hist if t.get("ano_mes") == mes_sel]
                for t in reversed(t_mes): st.write(f"{t['data']} - {t['categoria']} - R${t['valor']:.2f}")
                
            with sub_p:
                p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel]
                for p in reversed(p_mes): st.write(f"📍 {p['data']} - {p['cliente']} ({p['cidade']})")
            
            if st.session_state.perfil == "TURMA":
                with sub_m:
                    img_file = st.camera_input("📸 Usar Câmera")
                    upload_file = st.file_uploader("Ou enviar arquivo (Foto/Vídeo)", type=["jpg", "jpeg", "png", "mp4"])
                    arquivo = img_file if img_file else upload_file
                    if arquivo and st.button("💾 Salvar Mídia"):
                        nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo.name}"
                        path = os.path.join(MIDIA_DIR, nome_arquivo)
                        with open(path, "wb") as f: f.write(arquivo.getbuffer())
                        st.session_state.dados[st.session_state.turma]["midias"].append(path)
                        salvar_dados(st.session_state.dados); st.success("Salvo!"); st.rerun()
                    for m in reversed(midias): st.write(f"📁 {os.path.basename(m)}")

    if st.session_state.perfil == "ADM":
        with aba3[0]:
            if st.button("RESETAR GASTOS DA SEMANA"):
                for t in TURMAS: st.session_state.dados[t]["transacoes"] = []
                salvar_dados(st.session_state.dados); st.rerun()
