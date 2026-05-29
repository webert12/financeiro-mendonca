import streamlit as st
import json
import os
from datetime import datetime

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

# --- FUNÇÕES DE ARMAZENAMENTO ISOLADO ---
def carregar_dados():
    estrutura_limpa = {t: {"transacoes": [], "historico": [], "pocos": [], "midias": []} for t in TURMAS}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                dados = json.load(f)
                if "transacoes" in dados or isinstance(dados, list):
                    return estrutura_limpa
                # Garante que chaves novas como 'pocos' e 'midias' existam mesmo em arquivos antigos
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
            
            # --- CORREÇÃO DO SALDO DO DINHEIRO (SUBTRAI CONFORME GASTA) ---
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

    # --- ABA: MÍDIAS (CÂMERA DIRETA E ENVIOS) ---
    with aba2:
        st.subheader("📷 Gerenciamento de Mídias")
        if st.session_state.perfil == "ADM":
            st.warning("O perfil Administrador serve apenas para monitoramento.")
        else:
            t_ativa = st.session_state.turma
            
            # Opção 1: Força o dispositivo móvel a abrir o aplicativo nativo de câmera para tirar foto em resolução FHD/Máxima
            st.write("**Opção 1: Abrir Câmera para Foto (Qualidade FHD) 📸**")
            foto_capturada = st.file_uploader("Clique abaixo para tirar foto com a câmera do celular:", type=["jpg", "jpeg", "png"], key="foto_camera")
            if foto_capturada is not None:
                if st.button("💾 SALVAR FOTO CAPTURADA"):
                    if not os.path.exists("saved_media"):
                        os.makedirs("saved_media")
                    nome_arquivo = f"saved_media/{t_ativa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_camera.jpg"
                    with open(nome_arquivo, "wb") as f:
                        f.write(foto_capturada.getbuffer())
                    
                    nova_midia = {
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "ano_mes": datetime.now().strftime("%Y-%m"),
                        "caminho": nome_arquivo,
                        "tipo": "image/jpeg"
                    }
                    st.session_state.dados[t_ativa]["midias"].append(nova_midia)
                    salvar_dados(st.session_state.dados)
                    st.success("Foto salva com sucesso!")
                    st.rerun()

            st.divider()

            # Opção 2: Força o dispositivo móvel a abrir a Filmadora/Câmera nativa diretamente para gravar vídeo
            st.write("**Opção 2: Abrir Câmera para Gravar Vídeo 🎥**")
            video_gravado = st.file_uploader("Clique abaixo para gravar um vídeo com a câmera do celular:", type=["mp4", "mov", "avi", "3gp"], key="video_recorder")
            if video_gravado is not None:
                if st.button("💾 SALVAR VÍDEO GRAVADO"):
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
                        "tipo": video_gravado.type
                    }
                    st.session_state.dados[t_ativa]["midias"].append(nova_midia)
                    salvar_dados(st.session_state.dados)
                    st.success("Vídeo gravado com sucesso!")
                    st.rerun()

            # --- SCRIPT DE INJEÇÃO (HTML5 CAPTURE) ---
            # Este bloco força o navegador do celular a abrir diretamente a câmera traseira do sistema em alta definição.
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
                resumo_fin = f"Relatório Financeiro - {target_turma} - {mes_sel}\n\n" + "\n".join([f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}" for t in t_mes]) 
                st.download_button("📥 Baixar Relatório Financeiro", resumo_fin, f"financeiro_{target_turma}_{mes_sel}.txt") 
                for t in reversed(t_mes): 
                    st.write(f"{t['data']} - {t['categoria']} - R${t['valor']:.2f}") 
            with sub_p: 
                p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                if p_mes: 
                    sel_poco = st.selectbox("Escolha o poço para baixar:", [f"{p['data']} - {p['cliente']}" for p in p_mes]) 
                    p_baixar = next(p for p in p_mes if f"{p['data']} - {p['cliente']}" == sel_poco) 
                    resumo_poco = f"RELATÓRIO DE POÇO\nData: {p_baixar['data']}\nCliente: {p_baixar['cliente']}\nCidade: {p_baixar['cidade']}\nMetragem: {p_baixar['metragem']}\nFuncionários: {p_baixar['funcionarios']}\nMaterial: {p_baixar['material']}" 
                    st.download_button("📥 Baixar este Poço (PDF/TXT)", resumo_poco, f"poco_{p_baixar['cliente']}_{p_baixar['data'].replace('/','-')}.txt") 
                    for p in reversed(p_mes): 
                        st.write(f"📍 {p['data']} - {p['cliente']} ({p['cidade']})") 
                else: 
                    st.caption("Nenhum poço encontrado.")
            
            # Sub-aba exclusiva de Mídias vinculada ao histórico mensal do funcionário selecionado
            with sub_m:
                m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                if m_mes:
                    for m in reversed(m_mes):
                        st.write(f"📅 Enviado em: {m['data']}")
                        if os.path.exists(m['caminho']):
                            if "video" in m['tipo'] or m['caminho'].endswith(('.mp4', '.mov', '.avi', '.3gp')):
                                st.video(m['caminho'])
                            else:
                                st.image(m['caminho'], use_container_width=True)
                        else:
                            st.caption("Arquivo físico não localizado.")
                        st.divider()
                else:
                    st.caption("Nenhuma mídia registrada para este funcionário neste mês.")
        else:
            st.caption("Nenhum histórico encontrado.")

    if st.session_state.perfil == "ADM": 
        with aba4[0]: 
            if st.button("RESETAR GASTOS DA SEMANA"): 
                for t in TURMAS: 
                    st.session_state.dados[t]["transacoes"] = [] 
                salvar_dados(st.session_state.dados); st.rerun()
