import streamlit as st
import json
import os
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" ---
st.set_page_config(page_title="Mendonça Poços", page_icon="💧", layout="centered", initial_sidebar_state="collapsed")

# Estilização profissional para Celular (Mobile-First)
st.markdown("""""", unsafe_allow_html=True)

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

# Chaves de controle para resetar os uploaders de mídia
if 'foto_key' not in st.session_state:
    st.session_state.foto_key = 0
if 'video_key' not in st.session_state:
    st.session_state.video_key = 0

# --- DESIGN DA LOGO DA EMPRESA ---
def desenhar_logo():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("<h1 style='font-size: 50px; margin: 0;'>💧</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0047AB; font-family: sans-serif; margin: 5px 0;'>MENDONÇA POÇOS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; letter-spacing: 2px; font-size: 12px;'>======= GESTÃO CORPORATIVA =======</p>", unsafe_allow_html=True)
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
        identificacao = st.session_state.turma if st.session_state.perfil == "TURMA" else "Gestor Geral (ADM)"
        st.markdown(f"🟢 Logado: {identificacao}")
    with c_sair:
        if st.button("Sair"):
            st.session_state.perfil = None
            st.session_state.turma = None
            st.session_state.selecionou_usuario = None
            st.rerun()
    
    desenhar_logo()
    
    # Abas principais do menu
    abas_menu = ["Registrar", "Mídias", "Relatório Mensal"]
    if st.session_state.perfil == "ADM": 
        abas_menu.append("Painel ADM") 
    
    aba1, aba2, aba3, *aba4 = st.tabs(abas_menu)
    
    with aba1: 
        if st.session_state.perfil == "ADM": 
            st.warning("O perfil Administrador serve apenas para monitoramento.")
        else: 
            t_ativa = st.session_state.turma 
            trans_semana = st.session_state.dados[t_ativa]["transacoes"] 
            pocos_registrados = st.session_state.dados[t_ativa].get("pocos", []) 
            
            total_gasto_dinheiro = sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Dinheiro')
            saldo_restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_gasto_dinheiro
            
            c1, c2 = st.columns(2) 
            c1.metric("💵 Saldo Restante", f"R$ {saldo_restante_dinheiro:.2f}") 
            c2.metric("💳 Acumulado Cartão", f"R$ {sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Cartão'):.2f}") 
            
            mostrar_painel = st.toggle("📝 Registrar Despesas", value=False) 
            if mostrar_painel: 
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
            mostrar_pocos = st.toggle("🚰 Poços Perfurados", value=False) 
            if mostrar_pocos: 
                with st.form("form_pocos", clear_on_submit=True): 
                    cl = st.text_input("Cliente"); ci = st.text_input("Cidade"); mt = st.text_input("Metragem"); mat = st.text_area("Material"); fun = st.text_input("Funcionários") 
                    if st.form_submit_button("SALVAR RELATÓRIO"): 
                        st.session_state.dados[t_ativa]["pocos"].append({"data": datetime.now().strftime("%d/%m/%Y"), "ano_mes": datetime.now().strftime("%Y-%m"), "cliente": cl, "cidade": ci, "metragem": mt, "material": mat, "funcionarios": fun}) 
                        salvar_dados(st.session_state.dados); st.rerun()

    # --- ABA: MÍDIAS (CORRIGIDA COM PERSISTÊNCIA COMPLETA) ---
    with aba2:
        st.subheader("📷 Gerenciamento de Mídias")
        if st.session_state.perfil == "ADM":
            st.warning("O perfil Administrador serve apenas para monitoramento.")
        else:
            t_ativa = st.session_state.turma
            
            # Seleção de Categoria do Poço para vincular ao envio
            pocos_existentes = [f"{p['cliente']} ({p['cidade']})" for p in st.session_state.dados[t_ativa].get("pocos", [])]
            categoria_poco_sel = st.selectbox("📍 Vincular esta mídia a qual Poço/Cliente?", ["Geral / Sem Poço Específico"] + pocos_existentes)
            
            st.divider()
            
            # Opção 1: Câmera nativa para foto
            st.write("**Opção 1: Abrir Câmera para Foto (Qualidade FHD) 📸**")
            foto_capturada = st.file_uploader(
                "Clique abaixo para tirar foto com a câmera do celular:", 
                type=["jpg", "jpeg", "png"], 
                key=f"foto_camera_widget_{st.session_state.foto_key}"
            )
            
            if foto_capturada is not None:
                if st.button("💾 CONFIRMAR E SALVAR FOTO", key="btn_confirmar_foto"):
                    if not os.path.exists("saved_media"):
                        os.makedirs("saved_media")
                    nome_arquivo = f"saved_media/{t_ativa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_camera.jpg"
                    
                    with open(nome_arquivo, "wb") as f:
                        f.write(foto_capturada.getbuffer())
                    
                    nova_midia = {
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "ano_mes": datetime.now().strftime("%Y-%m"),
                        "caminho": nome_arquivo,
                        "tipo": "image/jpeg",
                        "poco": categoria_poco_sel
                    }
                    st.session_state.dados[t_ativa]["midias"].append(nova_midia)
                    salvar_dados(st.session_state.dados)
                    
                    # Altera a chave para resetar o uploader limpando a tela
                    st.session_state.foto_key += 1
                    st.success("Foto salva com sucesso no sistema!")
                    st.rerun()

            st.divider()

            # Opção 2: Câmera nativa para vídeo
            st.write("**Opção 2: Abrir Câmera para Gravar Vídeo 🎥**")
            video_gravado = st.file_uploader(
                "Clique abaixo para gravar um vídeo com a câmera do celular:", 
                type=["mp4", "mov", "avi", "3gp"], 
                key=f"video_recorder_widget_{st.session_state.video_key}"
            )
            
            if video_gravado is not None:
                if st.button("💾 CONFIRMAR E SALVAR VÍDEO", key="btn_confirmar_video"):
                    if not os.path.exists("saved_media"):
                        os.makedirs("saved_media")
                    extensao = video_gravado.name.split(".")[-1]
                    nome_arquivo = f"saved_media/{t_ativa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensao}"
                    
                    with open(nome_arquivo, "wb") as f:
                        f.write(video_gravado.getbuffer())
                    
                    nova_midia = {
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "ano_mes": datetime.now().strftime("%Y-%m"),
                        "caminho": nome_arquivo,
                        "tipo": video_gravado.type,
                        "poco": categoria_poco_sel
                    }
                    st.session_state.dados[t_ativa]["midias"].append(nova_midia)
                    salvar_dados(st.session_state.dados)
                    
                    # Altera a chave para resetar o uploader limpando a tela
                    st.session_state.video_key += 1
                    st.success("Vídeo gravado e salvo com sucesso!")
                    st.rerun()

            # --- SCRIPT DE INJEÇÃO (HTML5 CAPTURE) ---
            st.markdown("""
                <iframe src="about:blank" style="display:none;" onload="
                    const doc = window.parent.document;
                    const aplicarFiltrosCamera = () => {
                        const inputs = doc.querySelectorAll('input[type=\"file\"]');
                        inputs.forEach(input => {
                            if (input.accept.includes('mp4') || input.accept.includes('video')) {
                                input.setAttribute('capture', 'environment');
                            }
                            if (input.accept.includes('jpg') || input.accept.includes('jpeg') || input.accept.includes('png')) {
                                input.setAttribute('capture', 'environment');
                            }
                        });
                    };
                    setInterval(aplicarFiltrosCamera, 800);
                "></iframe>
            """, unsafe_allow_html=True)

    with aba3: 
        st.subheader("📅 Histórico Mensal") 
        target_turma = st.session_state.turma if st.session_state.perfil == "TURMA" else st.selectbox("Selecione o Colaborador", TURMAS) 
        hist = st.session_state.dados[target_turma]["historico"] 
        pocos = st.session_state.dados[target_turma].get("pocos", []) 
        midias = st.session_state.dados[target_turma].get("midias", [])
        
        meses = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in hist + pocos + midias)), reverse=True) 
        if meses: 
            mes_sel = st.selectbox("Escolha o mês", meses) 
            sub_f, sub_p, sub_m = st.tabs(["💰 Custos", "🚰 Poços", "📷 Mídias"]) 
            
            with sub_f: 
                t_mes = [t for t in hist if t.get("ano_mes") == mes_sel] 
                linhas_pdf_fin = [f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}" for t in t_mes]
                pdf_financeiro = exportar_para_pdf(f"Relatorio Financeiro - {target_turma} - {mes_sel}", linhas_pdf_fin)
                
                st.download_button("📥 Baixar Relatório Financeiro (PDF)", pdf_financeiro, f"financeiro_{target_turma}_{mes_sel}.pdf", "application/pdf") 
                for t in reversed(t_mes): 
                    st.write(f"{t['data']} - {t['categoria']} - R${t['valor']:.2f}") 
            
            with sub_p: 
                p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                if p_mes: 
                    sel_poco = st.selectbox("Escolha o poço para baixar:", [f"{p['data']} - {p['cliente']}" for p in p_mes]) 
                    p_baixar = next(p for p in p_mes if f"{p['data']} - {p['cliente']}" == sel_poco) 
                    
                    linhas_pdf_poco = [
                        f"Data de Registro: {p_baixar['data']}",
                        f"Cliente: {p_baixar['cliente']}",
                        f"Cidade: {p_baixar['cidade']}",
                        f"Metragem Perfurada: {p_baixar['metragem']} metros",
                        f"Funcionarios na Obra: {p_baixar['funcionarios']}",
                        f"Materiais Utilizados: {p_baixar['material']}"
                    ]
                    pdf_poco = exportar_para_pdf(f"Relatorio de Poco - {p_baixar['cliente']}", linhas_pdf_poco)
                    
                    st.download_button("📥 Baixar este Poço (PDF)", pdf_poco, f"poco_{p_baixar['cliente']}_{p_baixar['data'].replace('/','-')}.pdf", "application/pdf") 
                    for p in reversed(p_mes): 
                        st.write(f"📍 {p['data']} - {p['cliente']} ({p['cidade']})") 
                else: 
                    st.caption("Nenhum poço encontrado.")
            
            # Sub-aba organizada e filtrada previamente por Poço Escolhido
            with sub_m:
                m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                
                if m_mes:
                    # Lista dinâmica de poços vinculados às mídias salvas do mês
                    pocos_disponiveis = sorted(list(set(m.get("poco", "Geral / Sem Poço Específico") for m in m_mes)))
                    
                    # EXIGÊNCIA DO USUÁRIO: Função prévia de escolha antes de mostrar os arquivos
                    poco_selecionado = st.selectbox("🔍 Escolha o Poço para visualizar fotos e vídeos:", pocos_disponiveis)
                    
                    # Filtra os dados reais baseado na escolha prévia
                    m_filtrado = [m for m in m_mes if m.get("poco", "Geral / Sem Poço Específico") == poco_selecionado]
                    
                    fotos_filtradas = [m for m in m_filtrado if "video" not in m.get("tipo", "").lower() and not m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                    videos_filtrados = [m for m in m_filtrado if "video" in m.get("tipo", "").lower() or m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp'))]
                    
                    st.markdown(f"### 📁 Arquivos de: *{poco_selecionado}*")
                    
                    with st.expander("📸 FOTOS SALVAS"):
                        if fotos_filtradas:
                            for f in reversed(fotos_filtradas):
                                st.write(f"📅 {f['data']}")
                                if os.path.exists(f['caminho']):
                                    st.image(f['caminho'], use_container_width=True)
                                else:
                                    st.caption("Arquivo físico não localizado.")
                                st.divider()
                        else:
                            st.caption("Nenhuma foto localizada para este poço.")
                    
                    with st.expander("🎥 VÍDEOS SALVOS"):
                        if videos_filtrados:
                            for v in reversed(videos_filtrados):
                                st.write(f"📅 {v['data']}")
                                if os.path.exists(v['caminho']):
                                    st.video(v['caminho'])
                                else:
                                    st.caption("Arquivo físico não localizado.")
                                st.divider()
                        else:
                            st.caption("Nenhum vídeo localizado para este poço.")
                else:
                    st.caption("Nenhuma mídia registrada para este colaborador neste mês.")

    if st.session_state.perfil == "ADM": 
        with aba4[0]: 
            if st.button("RESETAR GASTOS DA SEMANA"): 
                for t in TURMAS: 
                    st.session_state.dados[t]["transacoes"] = [] 
                salvar_dados(st.session_state.dados); st.rerun()
