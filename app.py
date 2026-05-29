import streamlit as st
import json
import os
from datetime import datetime
import pytz
from fpdf import FPDF

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" ---
st.set_page_config(
    page_title="Mendonça Poços",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização profissional para Celular (Mobile-First)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100% !important;
    }

    div.stButton > button:first-child {
        background-color: #00cfcc;
        color: black;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
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

    .media-card {
        background-color: #1e2129;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #00cfcc;
    }

    /* CAMERA EM TELA CHEIA */
    .stCameraInput {
        width: 100% !important;
    }

    .stCameraInput > div {
        width: 100% !important;
    }

    .stCameraInput video {
        width: 100% !important;
        height: 75vh !important;
        object-fit: cover !important;
        border-radius: 20px;
        background: black;
    }

    .stFileUploader {
        background-color: #1e2129;
        padding: 10px;
        border-radius: 15px;
    }

    /* PLAYER DE VÍDEO */
    video {
        width: 100% !important;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "gastos_dados.json"
MEDIA_DIR = "midias"
LIMITE_DINHEIRO_SEMANAL = 500.00

# Define o fuso horário de Brasília
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')

# Cria pasta de mídias automaticamente
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# --- FUNÇÃO GERADOR DE PDF ---
def gerar_pdf(titulo, conteudo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=titulo, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    conteudo_formatado = conteudo.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=conteudo_formatado)

    return pdf.output(dest='S').encode('latin-1')

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
    estrutura_limpa = {
        t: {
            "transacoes": [],
            "historico": [],
            "pocos": [],
            "midias": []
        } for t in TURMAS
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)

                if "transacoes" in dados or isinstance(dados, list):
                    return estrutura_limpa

                for t in TURMAS:
                    if t not in dados:
                        dados[t] = {
                            "transacoes": [],
                            "historico": [],
                            "pocos": [],
                            "midias": []
                        }

                    if "pocos" not in dados[t]:
                        dados[t]["pocos"] = []

                    if "midias" not in dados[t]:
                        dados[t]["midias"] = []

                return dados

            except:
                return estrutura_limpa

    return estrutura_limpa

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

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
        st.markdown(
            "<h1 style='text-align: center; color: #00cfcc; margin-bottom: 0px;'>💧</h1>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='logo-text'>MENDONÇA POÇOS</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-logo'>======= GESTÃO CORPORATIVA =======</div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

# --- TELA DE LOGIN / SELEÇÃO DE EQUIPE ---
if st.session_state.perfil is None:

    desenhar_logo()

    if st.session_state.selecionou_usuario is None:

        st.write("Identifique-se para entrar no aplicativo:")

        if st.button("🔐 ACESSAR SISTEMA"):
            st.session_state.selecionou_usuario = "FUNCIONARIO_FORM"
            st.rerun()

        st.divider()

        if st.button("🔑 ACESSO ADMINISTRADOR (ADM)", type="secondary"):
            st.session_state.selecionou_usuario = "ADM_SENHA"
            st.rerun()

    elif st.session_state.selecionou_usuario == "FUNCIONARIO_FORM":

        st.subheader("Login de Colaborador")

        usuario_digitado = st.text_input("Digite seu Nome (Usuário)")
        senha_digitada = st.text_input("Digite sua Senha", type="password")

        c_voltar, c_entrar = st.columns(2)

        if c_voltar.button("Voltar"):
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

# --- INTERFACE PRINCIPAL OPERACIONAL ---
else:

    c_status, c_sair = st.columns([3, 1])

    with c_status:
        identificacao = (
            st.session_state.turma
            if st.session_state.perfil == "TURMA"
            else "Gestor Geral (ADM)"
        )

        st.markdown(f"🟢 Logado: **{identificacao}**")

    with c_sair:

        if st.button("Sair"):

            st.session_state.perfil = None
            st.session_state.turma = None
            st.session_state.selecionou_usuario = None
            st.rerun()

    desenhar_logo()

    abas_menu = [
        "Registrar",
        "Relatório Mensal",
        "📸 Capturar Mídias"
    ]

    aba1, aba2, aba_midia = st.tabs(abas_menu)

    # =========================
    # ABA MÍDIAS
    # =========================
    with aba_midia:

        t_ativa = st.session_state.turma

        st.subheader("📸 Capturar Fotos e Vídeos")

        st.info(
            "Agora a câmera abre em tamanho grande "
            "igual tela cheia do celular."
        )

        tipo_midia = st.radio(
            "Selecione o tipo",
            ["📷 Foto", "🎥 Vídeo"],
            horizontal=True
        )

        descricao = st.text_input(
            "Descrição da mídia"
        )

        # =========================
        # FOTO
        # =========================
        if tipo_midia == "📷 Foto":

            st.info(
                "Use o botão da câmera para tirar a foto."
            )

            foto = st.camera_input(
                "📷 Abrir câmera",
                key="camera_foto"
            )

            if foto is not None:

                try:

                    agora = datetime.now(TZ_BRASILIA)

                    nome_arquivo = (
                        f"{t_ativa}_foto_"
                        f"{agora.strftime('%Y%m%d_%H%M%S')}.jpg"
                    )

                    caminho = os.path.join(
                        MEDIA_DIR,
                        nome_arquivo
                    )

                    imagem_bytes = foto.read()

                    with open(caminho, "wb") as f:
                        f.write(imagem_bytes)

                    registro = {
                        "tipo": "foto",
                        "arquivo": caminho,
                        "descricao": descricao,
                        "data": agora.strftime("%d/%m/%Y %H:%M")
                    }

                    st.session_state.dados[t_ativa]["midias"].append(
                        registro
                    )

                    salvar_dados(st.session_state.dados)

                    st.success("✅ Foto salva com sucesso!")

                    st.image(
                        caminho,
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"Erro ao salvar foto: {str(e)}"
                    )

        # =========================
        # VÍDEO
        # =========================
        else:

            st.warning(
                "O Streamlit não grava vídeo pela câmera nativamente.\n\n"
                "Foi corrigido para envio REAL de vídeo do celular."
            )

            video = st.file_uploader(
                "🎥 Grave um vídeo pelo celular e envie aqui",
                type=["mp4", "mov", "avi", "mkv"]
            )

            if video is not None:

                try:

                    agora = datetime.now(TZ_BRASILIA)

                    extensao = video.name.split(".")[-1]

                    nome_arquivo = (
                        f"{t_ativa}_video_"
                        f"{agora.strftime('%Y%m%d_%H%M%S')}.{extensao}"
                    )

                    caminho = os.path.join(
                        MEDIA_DIR,
                        nome_arquivo
                    )

                    video_bytes = video.read()

                    with open(caminho, "wb") as f:
                        f.write(video_bytes)

                    registro = {
                        "tipo": "video",
                        "arquivo": caminho,
                        "descricao": descricao,
                        "data": agora.strftime("%d/%m/%Y %H:%M")
                    }

                    st.session_state.dados[t_ativa]["midias"].append(
                        registro
                    )

                    salvar_dados(st.session_state.dados)

                    st.success("✅ Vídeo salvo com sucesso!")

                    st.video(caminho)

                except Exception as e:

                    st.error(
                        f"Erro ao salvar vídeo: {str(e)}"
                    )

        st.divider()

        st.info(
            "As mídias ficam disponíveis "
            "na aba 'Relatório Mensal'."
        )

    # =========================
    # RELATÓRIO
    # =========================
    with aba2:

        st.subheader("📂 Histórico de Fotos e Vídeos")

        lista_midias = st.session_state.dados[
            st.session_state.turma
        ].get("midias", [])

        if lista_midias:

            for item in reversed(lista_midias):

                st.markdown(
                    "<div class='media-card'>",
                    unsafe_allow_html=True
                )

                st.write(f"📅 {item['data']}")
                st.write(f"📝 {item['descricao']}")

                if os.path.exists(item["arquivo"]):

                    if item["tipo"] == "foto":
                        st.image(
                            item["arquivo"],
                            use_container_width=True
                        )

                    elif item["tipo"] == "video":
                        st.video(item["arquivo"])

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

        else:

            st.info("Nenhuma mídia encontrada.")
