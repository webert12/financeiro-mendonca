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

    .media-card {
        background-color: #1e2129;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #00cfcc;
    }

    .stCameraInput video {
        border-radius: 15px;
        width: 100%;
    }

    .stFileUploader {
        background-color: #1e2129;
        padding: 10px;
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
                st.session_state.selecionou_usuario = "ADM_MONITORAMENTO"
                st.rerun()

            else:
                st.error("Senha de Administrador incorreta!")

    elif st.session_state.selecionou_usuario == "ADM_MONITORAMENTO":

        st.subheader("Painel de Monitoramento (ADM)")

        st.write(
            "Selecione uma das equipes abaixo para auditar ou clique em 'Entrar no Panel Geral':"
        )

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

    if st.session_state.perfil == "ADM":
        abas_menu.append("Painel ADM")

    aba1, aba2, aba_midia, *aba3 = st.tabs(abas_menu)

    # =========================
    # ABA REGISTRAR
    # =========================
    with aba1:

        if st.session_state.perfil == "ADM":

            st.warning(
                "O perfil Administrador serve apenas para monitoramento corporativo."
            )

        else:

            t_ativa = st.session_state.turma
            trans_semana = st.session_state.dados[t_ativa]["transacoes"]

            total_dinheiro = sum(
                t['valor']
                for t in trans_semana
                if t.get('metodo') == 'Dinheiro'
            )

            total_cartao = sum(
                t['valor']
                for t in trans_semana
                if t.get('metodo') == 'Cartão'
            )

            saldo_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_dinheiro

            c1, c2 = st.columns(2)

            c1.metric(
                "💵 Saldo Dinheiro",
                f"R$ {saldo_dinheiro:.2f}"
            )

            c2.metric(
                "💳 Cartão Acumulado",
                f"R$ {total_cartao:.2f}"
            )

            pct_consumido = (
                min(total_dinheiro / LIMITE_DINHEIRO_SEMANAL, 1.0)
                if LIMITE_DINHEIRO_SEMANAL > 0
                else 0
            )

            st.progress(pct_consumido)

            st.caption(
                f"Progresso de consumo do limite semanal ({int(pct_consumido*100)}%)"
            )

            st.divider()

            mostrar_painel = st.toggle(
                "📝 Registrar Despesas",
                value=False
            )

            if mostrar_painel:

                st.subheader("Nova Despesa")

                categoria_pai = st.selectbox(
                    "Selecione o que foi gasto",
                    [
                        "Café da Manhã",
                        "Café da tarde",
                        "Almoço",
                        "Jantar",
                        "Outros"
                    ]
                )

                sub_categoria = "Nenhum"
                detalhe_texto = ""

                if categoria_pai == "Outros":

                    sub_categoria = st.radio(
                        "Subcategoria",
                        [
                            "Mecânica",
                            "Pedágio",
                            "Transportes",
                            "Escrever motivo próprio"
                        ],
                        horizontal=True
                    )

                    if sub_categoria == "Escrever motivo próprio":
                        detalhe_texto = st.text_input("Escreva detalhadamente:")

                with st.form("form_final_envio", clear_on_submit=True):

                    opcao_pgto = st.radio(
                        "Método de pagamento?",
                        [
                            "💵 Dinheiro em Espécie",
                            "💳 Cartão de Crédito"
                        ],
                        horizontal=True
                    )

                    valor_input = st.text_input("Valor gasto R$")

                    if st.form_submit_button(
                        "CONFIRMAR E SALVAR LANÇAMENTO"
                    ):

                        try:

                            valor_limpo = valor_input.replace(",", ".").strip()
                            valor_final = float(valor_limpo)

                            metodo_final = (
                                "Dinheiro"
                                if "Dinheiro" in opcao_pgto
                                else "Cartão"
                            )

                            categoria_final = (
                                f"Outros ({detalhe_texto.strip()})"
                                if (
                                    categoria_pai == "Outros"
                                    and sub_categoria == "Escrever motivo próprio"
                                )
                                else (
                                    sub_categoria
                                    if categoria_pai == "Outros"
                                    else categoria_pai
                                )
                            )

                            agora = datetime.now(TZ_BRASILIA)

                            nova_trans = {
                                "data": agora.strftime("%d/%m %H:%M"),
                                "ano_mes": agora.strftime("%Y-%m"),
                                "categoria": categoria_final,
                                "metodo": metodo_final,
                                "valor": valor_final
                            }

                            st.session_state.dados[t_ativa]["transacoes"].append(
                                nova_trans
                            )

                            st.session_state.dados[t_ativa]["historico"].append(
                                nova_trans
                            )

                            salvar_dados(st.session_state.dados)

                            st.rerun()

                        except ValueError:

                            st.error(
                                "Erro no formato do valor. "
                                "Use apenas números."
                            )

            mostrar_pocos = st.toggle(
                "🚰 Poços Perfurados",
                value=False
            )

            if mostrar_pocos:

                st.subheader("Relatório de Poço Concluído")

                with st.form("form_pocos_perfurados", clear_on_submit=True):

                    data_p = datetime.now(TZ_BRASILIA).strftime("%d/%m/%Y")

                    data_input = st.text_input("Data", value=data_p)
                    cliente = st.text_input("Cliente")
                    cidade = st.text_input("Cidade")
                    metragem = st.text_input("Metragem")
                    material = st.text_area("Materiais")
                    fun = st.text_input("Funcionários")

                    if st.form_submit_button(
                        "SALVAR RELATÓRIO DO POÇO"
                    ):

                        novo_poco = {
                            "data": data_input,
                            "ano_mes": datetime.now(TZ_BRASILIA).strftime("%Y-%m"),
                            "cliente": cliente,
                            "cidade": cidade,
                            "metragem": metragem,
                            "material": material,
                            "funcionarios": fun
                        }

                        st.session_state.dados[t_ativa]["pocos"].append(
                            novo_poco
                        )

                        salvar_dados(st.session_state.dados)

                        st.rerun()

    # =========================
    # RELATÓRIOS
    # =========================
    with aba2:

        st.subheader("📅 Histórico Mensal")

        target_turma = (
            st.session_state.turma
            if st.session_state.perfil == "TURMA"
            else st.selectbox("Selecione o colaborador", TURMAS)
        )

        hist = st.session_state.dados[target_turma]["historico"]
        pocos = st.session_state.dados[target_turma].get("pocos", [])
        lista_midias = st.session_state.dados[target_turma].get("midias", [])

        meses = sorted(
            list(
                set(
                    t.get(
                        "ano_mes",
                        datetime.now(TZ_BRASILIA).strftime("%Y-%m")
                    )
                    for t in hist + pocos
                )
            ),
            reverse=True
        )

        if meses:

            mes_sel = st.selectbox("Escolha o mês", meses)

            sub_f, sub_p, sub_m = st.tabs(
                [
                    "💰 Controle de Custos",
                    "🚰 Poços Executados",
                    "📸 Fotos e Vídeos"
                ]
            )

            with sub_f:

                t_mes = [
                    t for t in hist
                    if t.get("ano_mes") == mes_sel
                ]

                resumo = (
                    "RELATÓRIO FINANCEIRO\n\n"
                    + "\n".join(
                        [
                            f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}"
                            for t in t_mes
                        ]
                    )
                )

                pdf_fin = gerar_pdf(
                    "Relatório Financeiro",
                    resumo
                )

                st.download_button(
                    "📥 Baixar PDF Financeiro",
                    pdf_fin,
                    f"financeiro_{target_turma}.pdf",
                    "application/pdf"
                )

                for t in reversed(t_mes):

                    st.write(
                        f"{t['data']} - {t['categoria']} - R${t['valor']:.2f}"
                    )

            with sub_p:

                p_mes = [
                    p for p in pocos
                    if p.get("ano_mes") == mes_sel
                ]

                if p_mes:

                    opcoes = [
                        f"{p.get('data', 'S/D')} - {p.get('cliente', 'Sem Nome')}"
                        for p in p_mes
                    ]

                    sel = st.selectbox("Escolha o poço", opcoes)

                    p_sel = next(
                        p for p in p_mes
                        if f"{p.get('data', 'S/D')} - {p.get('cliente', 'Sem Nome')}" == sel
                    )

                    resumo_p = (
                        f"RELATÓRIO DE POÇO\n"
                        f"Data: {p_sel.get('data')}\n"
                        f"Cliente: {p_sel.get('cliente')}\n"
                        f"Cidade: {p_sel.get('cidade')}\n"
                        f"Metragem: {p_sel.get('metragem')}\n"
                        f"Material: {p_sel.get('material')}\n"
                        f"Equipe: {p_sel.get('funcionarios')}"
                    )

                    pdf_poco = gerar_pdf(
                        "Relatório de Poço",
                        resumo_p
                    )

                    st.download_button(
                        "📥 Baixar PDF do Poço",
                        pdf_poco,
                        f"poco_{p_sel.get('cliente', 'poco')}.pdf",
                        "application/pdf"
                    )

                    for p in reversed(p_mes):

                        st.write(
                            f"📍 {p.get('data')} - "
                            f"{p.get('cliente')} "
                            f"({p.get('cidade')})"
                        )

            with sub_m:

                midias_mes = []

                for m in lista_midias:
                    try:
                        data_formatada = datetime.strptime(
                            m["data"],
                            "%d/%m/%Y %H:%M"
                        ).strftime("%Y-%m")

                        if data_formatada == mes_sel:
                            midias_mes.append(m)

                    except:
                        pass

                if midias_mes:

                    st.subheader("📂 Histórico de Fotos e Vídeos")

                    for item in reversed(midias_mes):

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

                    st.info(
                        "Nenhuma foto ou vídeo encontrado neste mês."
                    )

    # =========================
    # NOVA ABA DE MÍDIAS
    # =========================
    with aba_midia:

        if st.session_state.perfil == "ADM":

            st.warning(
                "Administrador possui acesso apenas de monitoramento."
            )

        else:

            t_ativa = st.session_state.turma

            st.subheader("📸 Capturar Fotos e Vídeos")

            st.info(
                "As mídias salvas aparecerão apenas "
                "na aba de Histórico Mensal."
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
                    "Ao abrir a câmera, utilize a câmera original do celular "
                    "para melhor qualidade."
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
                            caption="Pré-visualização",
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

                st.info(
                    "Clique em gravar vídeo usando a câmera do celular."
                )

                video = st.camera_input(
                    "🎥 Gravar Vídeo",
                    key="camera_video"
                )

                if video is not None:

                    try:

                        agora = datetime.now(TZ_BRASILIA)

                        nome_arquivo = (
                            f"{t_ativa}_video_"
                            f"{agora.strftime('%Y%m%d_%H%M%S')}.mp4"
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
                "As mídias ficam disponíveis apenas "
                "na aba 'Relatório Mensal'."
            )

    # =========================
    # PAINEL ADM
    # =========================
    if st.session_state.perfil == "ADM":

        with aba3[0]:

            if st.button("RESETAR GASTOS DA SEMANA"):

                for t in TURMAS:
                    st.session_state.dados[t]["transacoes"] = []

                salvar_dados(st.session_state.dados)

                st.rerun()
