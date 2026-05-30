import streamlit as st
import json
import os
from datetime import datetime, timedelta, timezone
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" PREMIUM ---
st.set_page_config(page_title="Mendonça Poços", page_icon="💧", layout="centered", initial_sidebar_state="collapsed")

# Estilização profissional com foco em centralização absoluta e tradução total (UI/UX)
st.markdown("""
<style>
    /* Importação da Fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset Geral da Página e Centralização de Texto Base */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        font-family: 'Inter', sans-serif !important;
        color: #f8fafc !important;
        text-align: center !important;
    }
    
    /* Customização Global para Forçar Centralização */
    h1, h2, h3, h4, h5, h6, p, span {
        font-family: 'Inter', sans-serif !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    /* Centralizar Labels dos Widgets */
    label[data-testid="stWidgetLabel"] {
        justify-content: center !important;
        text-align: center !important;
        display: flex !important;
        width: 100% !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* Centralizar Opções do Seletor de Rádio (Método de Pagamento) */
    div[data-testid="stRadio"] > div {
        justify-content: center !important;
    }
    
    /* Transformação dos Cards de Métricas */
    div[data-testid="stMetricContainer"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }

    /* Estilização de Botões */
    div.stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        margin: 0 auto !important;
        display: block !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Botões Secundários */
    div.stButton > button[kind="secondary"] {
        background: #334155 !important;
        border: 1px solid #475569 !important;
        color: #f1f5f9 !important;
        box-shadow: none !important;
    }
    
    /* Botões de Perigo/Reset */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
    }

    /* Formulários e Containers */
    div[data-testid="stForm"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
        text-align: center !important;
    }
    
    /* Abas/Tabs Customizadas */
    div[data-testid="stTabBar"] {
        background-color: #111827 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        margin-bottom: 20px !important;
        display: flex !important;
        justify-content: center !important;
    }
    button[data-testid="stTabBarTab"] {
        border-radius: 8px !important;
        color: #94a3b8 !important;
    }
    button[data-testid="stTabBarTab"][aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
    
    /* Inputs de Texto e Seletores Centralizados */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        text-align: center !important;
    }
    
    /* --- CORREÇÃO DEFINITIVA DO ARQUIVO DE UPLOAD --- */
    div[data-testid="stFileUploader"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    div[data-testid="stFileUploaderDropzone"] {
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        padding: 20px !important;
        background-color: #0f172a !important;
        border: 2px dashed #334155 !important;
        border-radius: 12px !important;
        width: 100% !important;
    }

    /* Oculta os textos nativos do Streamlit que ficavam em inglês ou quebrando layout */
    div[data-testid="stFileUploaderDropzone"] span, 
    div[data-testid="stFileUploaderDropzone"] small {
        display: none !important;
    }
    
    /* Remove a quebra e o bug do 'uploadupload' e cria um botão limpo e centralizado */
    div[data-testid="stFileUploaderDropzone"] button {
        font-size: 0 !important; /* Apaga o texto 'Browse files' nativo */
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2) !important;
        cursor: pointer !important;
        margin: 5px auto !important;
        display: inline-block !important;
    }
    
    /* Injeta o texto perfeito traduzido em Português do Brasil */
    div[data-testid="stFileUploaderDropzone"] button::after {
        content: "✨ Selecionar Arquivo" !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        display: block !important;
    }
    
    /* Badge de Usuário Ativo */
    .user-badge {
        background: rgba(2, 132, 199, 0.15);
        border: 1px solid rgba(2, 132, 199, 0.3);
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 600;
        color: #38bdf8;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 0 auto !important;
    }
</style>
""", unsafe_allow_html=True)

# CONFIGURAÇÃO DO FUSO HORÁRIO DE BRASÍLIA (UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))

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

# --- FUNÇÃO PARA GERAR PDF EM MEMÓRIA ---
def exportar_para_pdf(titulo, linhas_conteudo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle(titulo)
    
    # Design do Cabeçalho do PDF
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.0, 0.28, 0.67)  # Azul corporativo
    c.drawString(50, 750, titulo.upper())
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(50, 740, 550, 740)
    
    # Configuração do texto
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    y = 710
    
    for linha in linhas_conteudo:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 750
        c.drawString(50, y, str(linha))
        y -= 22
        
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# --- FUNÇÕES DE ARMAZENAMENTO ISOLADO ---
def carregar_dados():
    estrutura_limpa = {t: {"transacoes": [], "historico": [], "pocos": [], "midias": []} for t in TURMAS}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                if "transacoes" in dados or isinstance(dados, list):
                    return estrutura_limpa
                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {"transacoes": [], "historico": [], "pocos": [], "midias": []}
                    if "pocos" not in dados[t]:
                        dados[t]["pocos"] = []
                    if "midias" not in dados[t]:
                        dados[t]["midias"] = []
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

# Chaves dinâmicas para resetar os uploaders de mídia e mensagens persistentes
if 'foto_key' not in st.session_state:
    st.session_state.foto_key = 0
if 'video_key' not in st.session_state:
    st.session_state.video_key = 0
if 'msg_sucesso' not in st.session_state:
    st.session_state.msg_sucesso = None

# --- DESIGN DA LOGO DA EMPRESA ---
def desenhar_logo():
    st.markdown("<div style='text-align: center; margin-bottom: 25px;'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("<h1 style='font-size: 55px; margin: 0; filter: drop-shadow(0px 4px 10px rgba(56,189,248,0.3));'>💧</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #38bdf8; font-family: sans-serif; font-weight: 800; margin: 8px 0 2px 0; letter-spacing: 1px;'>MENDONÇA POÇOS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; letter-spacing: 3px; font-size: 11px; font-weight: 600; margin: 0;'>GESTÃO CORPORATIVA</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- TELA DE LOGIN / SELEÇÃO DE EQUIPE ---
if st.session_state.perfil is None:
    desenhar_logo()
    if st.session_state.selecionou_usuario is None: 
        st.markdown("<div style='text-align: center; margin-bottom: 15px; color: #94a3b8;'>Identifique-se para entrar no aplicativo:</div>", unsafe_allow_html=True) 
        if st.button("🔐 ACESSAR SISTEMA"): 
            st.session_state.selecionou_usuario = "FUNCIONARIO_FORM" 
            st.rerun() 
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 ACESSO ADMINISTRADOR (ADM)", type="secondary"): 
            st.session_state.selecionou_usuario = "ADM_SENHA" 
            st.rerun() 
    elif st.session_state.selecionou_usuario == "FUNCIONARIO_FORM": 
        st.markdown("<h3 style='text-align:center; color:#f8fafc; margin-bottom:20px;'>Login de Colaborador</h3>", unsafe_allow_html=True) 
        usuario_digitado = st.text_input("Digite seu Nome (Usuário)") 
        senha_digitada = st.text_input("Digite sua Senha", type="password") 
        st.markdown("<br>", unsafe_allow_html=True)
        c_voltar, c_entrar = st.columns(2) 
        if c_voltar.button("Voltar", type="secondary"): 
            st.session_state.selecionou_usuario = None 
            st.rerun() 
        if c_entrar.button("Entrar"): 
            if usuario_digitado in CREDENCIAIS and usuario_digitado != "ADM": 
                if senha_digitada == CREDENCIAIS[usuario_digitado]: 
                    st.session_state.perfil = "TURMA" 
                    st.session_state.turma = usuario_digitado 
                    st.session_state.selecionou_usuario = None 
                    st.rerun() 
                else: 
                    st.error("Senha incorreta! Tente novamente.") 
            else: 
                st.error("Usuário não encontrado.")
    elif st.session_state.selecionou_usuario == "ADM_SENHA": 
        st.markdown("<div style='text-align:center; margin-bottom:15px;'>Digite a senha master para o perfil: <b>ADM</b></div>", unsafe_allow_html=True) 
        senha_adm = st.text_input("Senha ADM", type="password") 
        st.markdown("<br>", unsafe_allow_html=True)
        c_voltar, c_entrar = st.columns(2) 
        if c_voltar.button("Voltar", type="secondary"): 
            st.session_state.selecionou_usuario = None 
            st.rerun() 
        if c_entrar.button("Entrar como ADM"): 
            if senha_adm == CREDENCIAIS["ADM"]: 
                st.session_state.perfil = "ADM" 
                st.session_state.selecionou_usuario = "ADM_MONITORAMENTO" 
                st.rerun() 
            else: 
                st.error("Senha de Administrador incorreta!")
    elif st.session_state.selecionou_usuario == "ADM_MONITORAMENTO": 
        st.markdown("<h3 style='text-align:center; color:#38bdf8; margin-bottom:20px;'>Painel de Monitoramento (ADM)</h3>", unsafe_allow_html=True) 
        col1, col2 = st.columns(2) 
        for idx, t in enumerate(TURMAS): 
            c = col1 if idx % 2 == 0 else col2 
            if c.button(f"👤 Ver {t}", key=f"btn_adm_ver_{t}", type="secondary"): 
                st.session_state.perfil = "TURMA" 
                st.session_state.turma = t 
                st.session_state.selecionou_usuario = None 
                st.rerun() 
        st.divider() 
        if st.button("📊 Painel Geral Consolidado"): 
            st.session_state.selecionou_usuario = None 
            st.rerun()
# --- INTERFACE PRINCIPAL OPERACIONAL ---
else:
    c_status, c_sair = st.columns([2.5, 1.5])
    with c_status:
        identificacao = st.session_state.turma if st.session_state.perfil == "TURMA" else "Gestor Geral (ADM)"
        st.markdown(f"<div class='user-badge'>🟢 Ativo: {identificacao}</div>", unsafe_allow_html=True)
    with c_sair:
        if st.button("🚪 Sair do App", type="secondary"):
            st.session_state.perfil = None
            st.session_state.turma = None
            st.session_state.selecionou_usuario = None
            st.rerun()
    
    desenhar_logo()
    
    # --- LOGICA DE MENUS SEPARADOS (ADM vs FUNCIONÁRIO) ---
    if st.session_state.perfil == "ADM":
        aba_relatorio, aba_adm = st.tabs(["📅 Relatório Mensal", "⚙️ Painel ADM"])
        
        with aba_relatorio:
            st.markdown("<h4 style='color:#38bdf8; margin-top:10px;'>📅 Histórico Mensal de Equipes</h4>", unsafe_allow_html=True) 
            target_turma = st.selectbox("Selecione o Colaborador para Auditar", TURMAS) 
            hist = st.session_state.dados[target_turma]["historico"] 
            pocos = st.session_state.dados[target_turma].get("pocos", []) 
            midias = st.session_state.dados[target_turma].get("midias", [])
            
            meses = sorted(list(set(t.get("ano_mes", datetime.now(FUSO_BRASILIA).strftime("%Y-%m")) for t in hist + pocos + midias)), reverse=True) 
            if meses: 
                mes_sel = st.selectbox("Escolha o mês de referência:", meses, key="mes_sel_adm") 
                sub_f, sub_p, sub_m = st.tabs(["💰 Custos", "🚰 Poços", "📷 Mídias"]) 
                
                with sub_f: 
                    t_mes = [t for t in hist if t.get("ano_mes") == mes_sel] 
                    dias_disponiveis = sorted(list(set(t['data'][:5] for t in t_mes if 'data' in t)), reverse=True)
                    
                    if dias_disponiveis:
                        dias_pdf_sel = st.multiselect("📄 Escolha os dias para incluir no PDF:", dias_disponiveis, default=dias_disponiveis, key="dias_pdf_adm")
                        
                        if dias_pdf_sel:
                            t_filtrado_pdf = [t for t in t_mes if t.get('data', '')[:5] in dias_pdf_sel]
                            linhas_pdf_fin = [f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}" for t in t_filtrado_pdf]
                            pdf_financeiro = exportar_para_pdf(f"Custos - {target_turma} - Filtro customizado", linhas_pdf_fin)
                            st.download_button("📥 Baixar Relatório Financeiro (PDF)", pdf_financeiro, f"financeiro_{target_turma}_{mes_sel}.pdf", "application/pdf")
                        else:
                            st.warning("Selecione ao menos 1 dia para gerar o PDF.")
                            
                        st.markdown("---")
                        dia_sel = st.selectbox("🔍 Escolha o dia para analisar custos na tela:", dias_disponiveis, key="dia_sel_adm_custos")
                        t_dia = [t for t in t_mes if t.get('data', '')[:5] == dia_sel]
                        for t in reversed(t_dia): 
                            st.markdown(f"<div style='background:#0f172a; padding:10px; border-radius:8px; margin-bottom:8px; border-left:3px solid #38bdf8;'>💵 <b>{t['data']}</b> - {t['categoria']} - <span style='color:#38bdf8; font-weight:600;'>R${t['valor']:.2f}</span></div>", unsafe_allow_html=True)
                    else:
                        st.caption("Nenhum custo registrado.")
                
                with sub_p: 
                    p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                    if p_mes: 
                        sel_poco = st.selectbox("Escolha o poço para analisar/baixar:", [f"{p['data']} - {p['cliente']}" for p in p_mes], key="sel_poco_adm") 
                        p_baixar = next(p for p in p_mes if f"{p['data']} - {p['cliente']}" == sel_poco) 
                        
                        st.markdown(f"""
                        <div style='background-color: #0f172a; padding: 18px; border-radius: 12px; border-left: 5px solid #0284c7; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                            <h4 style='margin-top:0; color:#38bdf8; font-size:1.1rem;'>📋 Dados do Relatório</h4>
                            <span style='color:#94a3b8;'>📍 Cliente:</span> <b>{p_baixar['cliente']}</b><br>
                            <span style='color:#94a3b8;'>🏙️ Cidade:</span> <b>{p_baixar['cidade']}</b><br>
                            <span style='color:#94a3b8;'>📏 Metragem:</span> <b>{p_baixar['metragem']} metros</b><br>
                            <span style='color:#94a3b8;'>👥 Funcionários:</span> <b>{p_baixar['funcionarios']}</b><br>
                            <span style='color:#94a3b8;'>🧱 Materiais Usados:</span><br><i style='color:#f1f5f9;'>{p_baixar['material']}</i>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.checkbox("✏️ Corrigir/Editar este Relatório (ADM)", key="edit_mode_adm"):
                            with st.form("form_editar_poco_adm"):
                                novo_cl = st.text_input("Cliente", value=p_baixar['cliente'])
                                novo_ci = st.text_input("Cidade", value=p_baixar['cidade'])
                                novo_mt = st.text_input("Metragem", value=p_baixar['metragem'])
                                novo_fun = st.text_input("Funcionários", value=p_baixar['funcionarios'])
                                novo_mat = st.text_area("Material", value=p_baixar['material'])
                                
                                if st.form_submit_button("💾 Salvar Alterações"):
                                    idx_original = next(i for i, p in enumerate(st.session_state.dados[target_turma]["pocos"]) if id(p) == id(p_baixar))
                                    st.session_state.dados[target_turma]["pocos"][idx_original].update({
                                        "cliente": novo_cl, "cidade": novo_ci, "metragem": novo_mt, "material": novo_mat, "funcionarios": novo_fun
                                    })
                                    salvar_dados(st.session_state.dados)
                                    st.success("Relatório atualizado com sucesso!")
                                    st.rerun()
                        
                        # CORREÇÃO AQUI: Mudado de linhas_pdf_poco para coincidir com o argumento da função abaixo
                        linhas_pdf_poco = [
                            f"Data de Registro: {p_baixar['data']}", f"Cliente: {p_baixar['cliente']}", f"Cidade: {p_baixar['cidade']}",
                            f"Metragem Perfurada: {p_baixar['metragem']} metros", f"Funcionarios na Obra: {p_baixar['funcionarios']}", f"Materiais Utilizados: {p_baixar['material']}"
                        ]
                        pdf_poco = exportar_para_pdf(f"Relatorio de Poco - {p_baixar['cliente']}", linhas_pdf_poco)
                        st.download_button("📥 Baixar este Poço (PDF)", pdf_poco, f"poco_{p_baixar['cliente']}_{p_baixar['data'].replace('/','-')}.pdf", "application/pdf") 
                    else: 
                        st.caption("Nenhum poço encontrado.")
                
                with sub_m:
                    m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                    if m_mes:
                        pocos_disponiveis = sorted(list(set(m.get("poco", "Geral / Sem Poço Específico") for m in m_mes)))
                        poco_selecionado = st.selectbox("🔍 Escolha o Poço para visualizar mídias:", pocos_disponiveis, key="poco_sel_midia_adm")
                        m_filtrado = [m for m in m_mes if m.get("poco", "Geral / Sem Poço Específico") == poco_selecionado]
                        
                        fotos_filtradas = [m for m in m_filtrado if "video" not in m.get("tipo", "").lower() and not m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                        videos_filtradas = [m for m in m_filtrado if "video" in m.get("tipo", "").lower() or m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                        
                        st.markdown(f"### 📁 Arquivos de: *{poco_selecionado}*")
                        with st.expander("📸 FOTOS SALVAS"):
                            if fotos_filtradas:
                                for f in reversed(fotos_filtradas):
                                    st.write(f"📅 {f['data']}")
                                    if os.path.exists(f['caminho']): st.image(f['caminho'], use_container_width=True)
                                    st.divider()
                            else: st.caption("Nenhuma foto localizada.")
                        
                        with st.expander("🎥 VÍDEOS SALVOS"):
                            if videos_filtradas:
                                for v in reversed(videos_filtradas):
                                    st.write(f"📅 {v['data']}")
                                    if os.path.exists(v['caminho']): st.video(v['caminho'])
                                    st.divider()
                            else: st.caption("Nenhum vídeo localizado.")
                    else:
                        st.caption("Nenhuma mídia registrada.")
            else:
                st.info("Nenhum registro encontrado para este colaborador.")

        with aba_adm:
            st.markdown("<h4 style='color:#ef4444; margin-top:10px;'>⚙️ Controle Global do Sistema</h4>", unsafe_allow_html=True)
            if st.button("❌ RESETAR GASTOS DA SEMANA (TODAS AS EQUIPES)", type="primary"): 
                for t in TURMAS: 
                    st.session_state.dados[t]["transacoes"] = [] 
                salvar_dados(st.session_state.dados)
                st.success("Limites semanais resetados com sucesso!")
                st.rerun()

    else:
        # Interface Operacional Completa Exclusiva dos Funcionários
        aba1, aba2 = st.tabs(["📝 Registrar Atividades", "📅 Relatório Mensal"])
        
        with aba1: 
            t_ativa = st.session_state.turma 
            trans_semana = st.session_state.dados[t_ativa]["transacoes"] 
            
            total_gasto_dinheiro = sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Dinheiro')
            saldo_restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_gasto_dinheiro
            
            # Painel Superior de Métricas Estilizado
            c1, c2 = st.columns(2) 
            c1.metric("💵 Saldo Restante", f"R$ {saldo_restante_dinheiro:.2f}") 
            c2.metric("💳 Acumulado Cartão", f"R$ {sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Cartão'):.2f}") 
            
            st.markdown("<br>", unsafe_allow_html=True)
            mostrar_painel = st.toggle("📝 Registrar Nova Despesa", value=False) 
            if mostrar_painel: 
                with st.form("form_final_envio", clear_on_submit=True): 
                    st.markdown("<h4 style='margin:0; color:#38bdf8;'>💰 Lançar Custo</h4>", unsafe_allow_html=True)
                    cat = st.selectbox("Categoria", ["Café da Manhã", "Almoço", "Outros"]) 
                    opcao_pgto = st.radio("Método de Pagamento", ["💵 Dinheiro", "💳 Cartão"], horizontal=True) 
                    valor_input = st.text_input("Valor R$ (Ex: 25,50)") 
                    if st.form_submit_button("SALVAR DESPESA"): 
                        valor_final = float(valor_input.replace(",", ".")) 
                        novo_trans = {"data": datetime.now(FUSO_BRASILIA).strftime("%d/%m %H:%M"), "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"), "categoria": cat, "metodo": "Dinheiro" if "Dinheiro" in opcao_pgto else "Cartão", "valor": valor_final} 
                        st.session_state.dados[t_ativa]["transacoes"].append(novo_trans) 
                        st.session_state.dados[t_ativa]["historico"].append(novo_trans) 
                        salvar_dados(st.session_state.dados); st.rerun() 
                        
            mostrar_pocos = st.toggle("🚰 Relatar Poço Perfurado", value=False) 
            if mostrar_pocos: 
                with st.form("form_pocos", clear_on_submit=True): 
                    st.markdown("<h4 style='margin:0; color:#38bdf8;'>📋 Informações da Perfuração</h4>", unsafe_allow_html=True)
                    cl = st.text_input("Nome do Cliente")
                    ci = st.text_input("Cidade")
                    mt = st.text_input("Metragem Perfurada (Metros)")
                    mat = st.text_area("Materiais Utilizados")
                    fun = st.text_input("Funcionários na Obra")
                    
                    st.markdown("<br><h5 style='color:#38bdf8; margin:0;'>Anexar Mídias desta Obra 📷</h5>", unsafe_allow_html=True)
                    
                    foto_capturada = st.file_uploader(
                        "Opção 1: Capturar Foto (Tamanho Máx: 200MB | Formatos: JPG, PNG)", 
                        type=["jpg", "jpeg", "png"], 
                        key=f"foto_auto_{st.session_state.foto_key}"
                    )
                    
                    video_gravado = st.file_uploader(
                        "Opção 2: Gravar Vídeo (Tamanho Máx: 200MB | Formatos: MP4, MOV, AVI)", 
                        type=["mp4", "mov", "avi", "3gp"], 
                        key=f"video_auto_{st.session_state.video_key}"
                    )
                    
                    if st.form_submit_button("ENVIAR RELATÓRIO COMPLETO"): 
                        st.session_state.dados[t_ativa]["pocos"].append({
                            "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y"), 
                            "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"), 
                            "cliente": cl, "cidade": ci, "metragem": mt, "material": mat, "funcionarios": fun
                        }) 
                        
                        nome_poco_vinculo = f"{cl} ({ci})" if (cl or ci) else "Geral / Sem Poço Específico"
                        
                        if foto_capturada is not None:
                            if not os.path.exists("saved_media"): os.makedirs("saved_media")
                            nome_arquivo_foto = f"saved_media/{t_ativa}_{datetime.now(FUSO_BRASILIA).strftime('%Y%m%d_%H%M%S')}_camera.jpg"
                            with open(nome_arquivo_foto, "wb") as f: 
                                f.write(foto_capturada.getbuffer())
                            st.session_state.dados[t_ativa]["midias"].append({
                                "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M"), 
                                "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"),
                                "caminho": nome_arquivo_foto, "tipo": "image/jpeg", "poco": nome_poco_vinculo
                            })
                            st.session_state.foto_key += 1

                        if video_gravado is not None:
                            if not os.path.exists("saved_media"): os.makedirs("saved_media")
                            extensao = video_gravado.name.split(".")[-1]
                            nome_arquivo_video = f"saved_media/{t_ativa}_{datetime.now(FUSO_BRASILIA).strftime('%Y%m%d_%H%M%S')}.{extensao}"
                            with open(nome_arquivo_video, "wb") as f: 
                                f.write(video_gravado.getbuffer())
                            st.session_state.dados[t_ativa]["midias"].append({
                                "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M"), 
                                "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"),
                                "caminho": nome_arquivo_video, "tipo": video_gravado.type, "poco": nome_poco_vinculo
                            })
                            st.session_state.video_key += 1
                        
                        salvar_dados(st.session_state.dados)
                        st.session_state.msg_sucesso = "✅ Relatório e mídias salvos com sucesso!"
                        st.rerun()

                st.markdown("""
                    <iframe src="about:blank" style="display:none;" onload="
                        const doc = window.parent.document;
                        const aplicarFiltrosCamera = () => {
                            const inputs = doc.querySelectorAll('input[type=\"file\"]');
                            inputs.forEach(input => {
                                if (input.accept.includes('mp4') || input.accept.includes('video') || input.accept.includes('jpg')) {
                                    input.setAttribute('capture', 'environment');
                                }
                            });
                        };
                        setInterval(aplicarFiltrosCamera, 800);
                    "></iframe>
                """, unsafe_allow_html=True)

        with aba2: 
            st.markdown("<h4 style='color:#38bdf8; margin-top:10px;'>📅 Meu Histórico Mensal</h4>", unsafe_allow_html=True) 
            t_ativa = st.session_state.turma 
            
            if st.session_state.msg_sucesso:
                st.success(st.session_state.msg_sucesso)
                st.session_state.msg_sucesso = None
                
            hist = st.session_state.dados[t_ativa]["historico"] 
            pocos = st.session_state.dados[t_ativa].get("pocos", []) 
            midias = st.session_state.dados[t_ativa].get("midias", [])
            
            meses = sorted(list(set(t.get("ano_mes", datetime.now(FUSO_BRASILIA).strftime("%Y-%m")) for t in hist + pocos + midias)), reverse=True) 
            if meses: 
                mes_sel = st.selectbox("Escolha o mês de referência:", meses, key="mes_sel_turma") 
                sub_f, sub_p, sub_m = st.tabs(["💰 Meus Custos", "🚰 Poços Relatados", "📷 Minhas Mídias"]) 
                
                with sub_f: 
                    t_mes = [t for t in hist if t.get("ano_mes") == mes_sel] 
                    dias_disponiveis = sorted(list(set(t['data'][:5] for t in t_mes if 'data' in t)), reverse=True)
                    
                    if dias_disponiveis:
                        dias_pdf_sel = st.multiselect("📄 Selecione os dias para incluir no PDF:", dias_disponiveis, default=dias_disponiveis, key="dias_pdf_turma")
                        
                        if dias_pdf_sel:
                            t_filtrado_pdf = [t for t in t_mes if t.get('data', '')[:5] in dias_pdf_sel]
                            linhas_pdf_fin = [f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}" for t in t_filtrado_pdf]
                            pdf_financeiro = exportar_para_pdf(f"Relatorio Financeiro - {t_ativa}", linhas_pdf_fin)
                            st.download_button("📥 Baixar Relatório Financeiro (PDF)", pdf_financeiro, f"financeiro_{t_ativa}_{mes_sel}.pdf", "application/pdf") 
                        else:
                            st.warning("Selecione pelo menos um dia para gerar o relatório PDF.")
                            
                        st.markdown("---")
                        dia_sel = st.selectbox("🔍 Escolha o dia para analisar custos na tela:", dias_disponiveis, key="dia_sel_turma_custos")
                        t_dia = [t for t in t_mes if t.get('data', '')[:5] == dia_sel]
                        for t in reversed(t_dia): 
                            st.markdown(f"<div style='background:#0f172a; padding:10px; border-radius:8px; margin-bottom:8px; border-left:3px solid #0284c7;'>💵 <b>{t['data']}</b> - {t['categoria']} - <span style='color:#38bdf8; font-weight:600;'>R${t['valor']:.2f}</span></div>", unsafe_allow_html=True)
                    else:
                        st.caption("Nenhum custo registrado.")
                
                with sub_p: 
                    p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                    if p_mes: 
                        sel_poco = st.selectbox("Escolha o poço para analisar/baixar:", [f"{p['data']} - {p['cliente']}" for p in p_mes], key="sel_poco_turma") 
                        p_baixar = next(p for p in p_mes if f"{p['data']} - {p['cliente']}" == sel_poco) 
                        
                        st.markdown(f"""
                        <div style='background-color: #0f172a; padding: 18px; border-radius: 12px; border-left: 5px solid #0284c7; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                            <h4 style='margin-top:0; color:#38bdf8; font-size:1.1rem;'>📋 Dados Atuais do Relatório</h4>
                            <span style='color:#94a3b8;'>📍 Cliente:</span> <b>{p_baixar['cliente']}</b><br>
                            <span style='color:#94a3b8;'>🏙️ Cidade:</span> <b>{p_baixar['cidade']}</b><br>
                            <span style='color:#94a3b8;'>📏 Metragem Perfurada:</span> <b>{p_baixar['metragem']} metros</b><br>
                            <span style='color:#94a3b8;'>👥 Funcionários:</span> <b>{p_baixar['funcionarios']}</b><br>
                            <span style='color:#94a3b8;'>🧱 Materiais Usados:</span><br><i style='color:#f1f5f9;'>{p_baixar['material']}</i>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.checkbox("✏️ Editar este Relatório", key="edit_mode_turma"):
                            with st.form("form_editar_poco_turma"):
                                novo_cl = st.text_input("Cliente", value=p_baixar['cliente'])
                                novo_ci = st.text_input("Cidade", value=p_baixar['cidade'])
                                novo_mt = st.text_input("Metragem", value=p_baixar['metragem'])
                                novo_fun = st.text_input("Funcionários", value=p_baixar['funcionarios'])
                                novo_mat = st.text_area("Material", value=p_baixar['material'])
                                
                                if st.form_submit_button("💾 Salvar Alterações"):
                                    idx_original = next(i for i, p in enumerate(st.session_state.dados[t_ativa]["pocos"]) if id(p) == id(p_baixar))
                                    st.session_state.dados[t_ativa]["pocos"][idx_original].update({
                                        "cliente": novo_cl, "cidade": novo_ci, "metragem": novo_mt, "material": novo_mat, "funcionarios": novo_fun
                                    })
                                    salvar_dados(st.session_state.dados)
                                    st.success("Relatório corrigido com sucesso!")
                                    st.rerun()
                        
                        linhas_pdf_poco = [
                            f"Data de Registro: {p_baixar['data']}", f"Cliente: {p_baixar['cliente']}", f"Cidade: {p_baixar['cidade']}",
                            f"Metragem Perfurada: {p_baixar['metragem']} metros", f"Funcionarios na Obra: {p_baixar['funcionarios']}", f"Materiais Utilizados: {p_baixar['material']}"
                        ]
                        pdf_poco = exportar_para_pdf(f"Relatorio de Poco - {p_baixar['cliente']}", linhas_pdf_poco)
                        st.download_button("📥 Baixar este Poço (PDF)", pdf_poco, f"poco_{p_baixar['cliente']}_{p_baixar['data'].replace('/','-')}.pdf", "application/pdf") 
                    else: 
                        st.caption("Nenhum poço encontrado.")
                
                with sub_m:
                    m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                    if m_mes:
                        pocos_disponiveis = sorted(list(set(m.get("poco", "Geral / Sem Poço Específico") for m in m_mes)))
                        poco_selecionado = st.selectbox("🔍 Escolha o Poço para visualizar fotos e vídeos:", pocos_disponiveis, key="poco_sel_midia_turma")
                        m_filtrado = [m for m in m_mes if m.get("poco", "Geral / Sem Poço Específico") == poco_selecionado]
                        
                        fotos_filtradas = [m for m in m_filtrado if "video" not in m.get("tipo", "").lower() and not m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                        videos_filtrados = [m for m in m_filtrado if "video" in m.get("tipo", "").lower() or m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                        
                        st.markdown(f"### 📁 Arquivos de: *{poco_selecionado}*")
                        with st.expander("📸 FOTOS SALVAS"):
                            if fotos_filtradas:
                                for f in reversed(fotos_filtradas):
                                    st.write(f"📅 {f['data']}")
                                    if os.path.exists(f['caminho']): st.image(f['caminho'], use_container_width=True)
                                    st.divider()
                            else: st.caption("Nenhuma foto localizada para este poço.")
                        with st.expander("🎥 VÍDEOS SALVOS"):
                            if videos_filtrados:
                                for v in reversed(videos_filtrados):
                                    st.write(f"📅 {v['data']}")
                                    if os.path.exists(v['caminho']): st.video(v['caminho'])
                                    st.divider()
                            else: st.caption("Nenhum vídeo localizado para este poço.")
                    else: st.caption("Nenhuma mídia registrada para este colaborador neste mês.")
            else:
                st.info("Nenhum registro encontrado.")
