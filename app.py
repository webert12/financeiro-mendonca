import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta, timezone
import io
import base64
import psycopg2
import psycopg2.extras
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# =========================================================================
# CONFIGURAÇÕES DO SISTEMA (SENHA ADM)
# =========================================================================
SENHA_ADM_SISTEMA = "adm9988"
# =========================================================================

# --- CONFIGURAÇÃO VISUAL ESTILO "APK" ---
st.set_page_config(page_title="Mendonça Poços", page_icon="💧", layout="centered", initial_sidebar_state="collapsed")

# CONFIGURAÇÃO DO FUSO HORÁRIO DE BRASÍLIA (UTC-3)
FUSO_BRASILIA = timezone(timedelta(hours=-3))

LIMITE_DINHEIRO_SEMANAL = 500.00

# Lista estática de equipes autorizadas no sistema
TURMAS = ["Rafael", "Ednaldo", "Luiz Felipe", "Carlos", "Cardoso", "Guilherme", "Paulo"]

# --- FUNÇÃO DE CONEXÃO DIRETA WITH O STREAMLIT SECRETS ---
def obter_conexao():
    return psycopg2.connect(st.secrets["URL_BANCO"])

# Trata dados do banco garantindo que venham como listas/dicionários legíveis
def processar_json_db(campo):
    if isinstance(campo, str):
        try:
            return json.loads(campo)
        except:
            return []
    return campo if campo is not None else []

# --- FUNÇÃO DE CRIPTOGRAFIA (HASHING SHA-256) ---
def gerar_hash(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

# --- FUNÇÃO PARA GERAR PDF EM MEMÓRIA ---
def exportar_para_pdf(titulo, linhas_conteudo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle(titulo)
    
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.0, 0.28, 0.67)
    c.drawString(50, 750, titulo.upper())
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(50, 740, 550, 740)
    
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

# --- FUNÇÕES DE ARMAZENAMENTO VIA POSTGRESQL ---
def carregar_dados():
    SENHA_PADRAO_PROVISORIA = gerar_hash("1234")
    dados_app = {}
    
    try:
        conn = obter_conexao()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT nome, senha_hash, transacoes, historico, pocos, midias FROM equipes;")
        dados_db = cur.fetchall()
        
        db_turmas = {row["nome"]: row for row in dados_db}
        
        for t in TURMAS:
            if t in db_turmas:
                row = db_turmas[t]
                dados_app[t] = {
                    "senha_hash": row.get("senha_hash") or SENHA_PADRAO_PROVISORIA,
                    "transacoes": processar_json_db(row.get("transacoes")),
                    "historico": processar_json_db(row.get("historico")),
                    "pocos": processar_json_db(row.get("pocos")),
                    "midias": processar_json_db(row.get("midias"))
                }
            else:
                cur.execute("""
                    INSERT INTO equipes (nome, senha_hash, transacoes, historico, pocos, midias)
                    VALUES (%s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb);
                """, (t, SENHA_PADRAO_PROVISORIA))
                dados_app[t] = {
                    "senha_hash": SENHA_PADRAO_PROVISORIA,
                    "transacoes": [],
                    "historico": [],
                    "pocos": [],
                    "midias": []
                }
        conn.commit()
        cur.close()
        conn.close()
        return dados_app
    except Exception as e:
        st.error(f"Erro ao carregar dados do Banco de Dados: {e}")
        return {t: {"senha_hash": SENHA_PADRAO_PROVISORIA, "transacoes": [], "historico": [], "pocos": [], "midias": []} for t in TURMAS}

def salvar_dados(dados):
    try:
        conn = obter_conexao()
        cur = conn.cursor()
        for t in TURMAS:
            if t in dados:
                cur.execute("""
                    INSERT INTO equipes (nome, senha_hash, transacoes, historico, pocos, midias)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nome) DO UPDATE SET
                        senha_hash = EXCLUDED.senha_hash,
                        transacoes = EXCLUDED.transacoes,
                        historico = EXCLUDED.historico,
                        pocos = EXCLUDED.pocos,
                        midias = EXCLUDED.midias;
                """, (
                    t,
                    dados[t]["senha_hash"],
                    json.dumps(dados[t]["transacoes"]),
                    json.dumps(dados[t]["historico"]),
                    json.dumps(dados[t]["pocos"]),
                    json.dumps(dados[t]["midias"])
                ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao sincronizar dados com o Banco de Dados: {e}")

# Inicialização do Estado da Sessão
if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()
if 'perfil' not in st.session_state:
    st.session_state.perfil = None
if 'turma' not in st.session_state:
    st.session_state.turma = None
if 'selecionou_usuario' not in st.session_state:
    st.session_state.selecionou_usuario = None
if 'foto_key' not in st.session_state:
    st.session_state.foto_key = 0
if 'video_key' not in st.session_state:
    st.session_state.video_key = 0
if 'msg_sucesso' not in st.session_state:
    st.session_state.msg_sucesso = None

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
            if usuario_digitado in TURMAS: 
                hash_digitada = gerar_hash(senha_digitada)
                hash_salva = st.session_state.dados[usuario_digitado].get("senha_hash")
                
                if hash_digitada == hash_salva: 
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
            if senha_adm == SENHA_ADM_SISTEMA: 
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
    
    if st.session_state.perfil == "ADM":
        aba_relatorio, aba_adm = st.tabs(["📅 Relatório Mensal", "⚙️ Painel ADM"])
        
        with aba_relatorio:
            st.subheader("📅 Histórico Mensal de Equipes") 
            target_turma = st.selectbox("Selecione o Colaborador para Auditar", TURMAS) 
            hist = st.session_state.dados[target_turma]["historico"] 
            pocos = st.session_state.dados[target_turma].get("pocos", []) 
            midias = st.session_state.dados[target_turma].get("midias", [])
            
            meses = sorted(list(set(t.get("ano_mes", datetime.now(FUSO_BRASILIA).strftime("%Y-%m")) for t in hist + pocos + midias)), reverse=True) 
            if meses: 
                mes_sel = st.selectbox("Escolha o mês", meses, key="mes_sel_adm") 
                sub_f, sub_p, sub_m = st.tabs(["💰 Custos", "𚚰 Poços", "📷 Mídias"]) 
                
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
                            st.write(f"💵 {t['data']} - {t['categoria']} - R${t['valor']:.2f}") 
                    else:
                        st.caption("Nenhum custo registrado.")
                
                with sub_p: 
                    p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                    if p_mes: 
                        sel_poco = st.selectbox("Escolha o poço para analisar/baixar:", [f"{p.get('data', 'Sem Data')} - {p.get('cliente', 'Sem Nome')}" for p in p_mes], key="sel_poco_adm") 
                        p_baixar = next(p for p in p_mes if f"{p.get('data', 'Sem Data')} - {p.get('cliente', 'Sem Nome')}" == sel_poco) 
                        
                        st.markdown(f"""
                        <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid #0047AB; margin-bottom: 15px;'>
                            <h4 style='margin-top:0;'>📋 Dados do Relatório</h4>
                            <b>📍 Cliente:</b> {p_baixar.get('cliente', '')}<br>
                            <b>📞 Telefone:</b> {p_baixar.get('telefone', '')}<br>
                            <b>🏠 Endereço do Poço:</b> {p_baixar.get('endereco_poco', '')}<br>
                            <b>🏙️ Cidade:</b> {p_baixar.get('cidade', '')}<br>
                            <b>📅 Data da Elaboração:</b> {p_baixar.get('data_elaboracao', '')}<br>
                            <b>⚙️ Método de Perfuração:</b> {p_baixar.get('metodo_perfuracao', '')}<br>
                            <b>📏 Profundidade do Poço:</b> {p_baixar.get('profundidade_poco', '')}<br>
                            <b>🌱 Perfuração em Solo (Metros):</b> {p_baixar.get('perfuracao_solo_metros', '')}<br>
                            <b>🛡️ Tipo de Revestimento:</b> {p_baixar.get('tipo_revestimento', '')}<br>
                            <b>📦 Quantidade de Revestimento:</b> {p_baixar.get('quantidade_revestimento', '')}<br>
                            <b>🚰 Tubo de Retirada de Água e Qtd (MT):</b> {p_baixar.get('tubo_retirada_agua_qtde', '')}<br>
                            <b>🔌 Tipo de Cabo e Qtd (MT):</b> {p_baixar.get('tipo_cabo_qtde', '')}<br>
                            <b>🧹 Tipo de Filtro:</b> {p_baixar.get('tipo_filtro', '')}<br>
                            <b>📏 Metros de Filtro:</b> {p_baixar.get('quantos_metros_filtro', '')}<br>
                            <b>⏳ Tipo de Pré Filtro:</b> {p_baixar.get('tipo_pre_filtro', '')}<br>
                            <b>🧱 Cimentação do Espaço Anelar?:</b> {p_baixar.get('fez_cimentacao', '')}<br>
                            <b>🧰 Laje de Proteção Sanitária?:</b> {p_baixar.get('fez_laje_protecao', '')}<br>
                            <b>🪨 Qtd de Pré Filtro (Brita):</b> {p_baixar.get('quantidade_pre_filtro_brita', '')}<br>
                            <b>🔒 Tampa:</b> {p_baixar.get('tampa', '')}<br>
                            <b>🔗 Conexões Utilizadas:</b> {p_baixar.get('conexoes_utilizadas', '')}<br>
                            <b>💧 Nível Estático:</b> {p_baixar.get('nivel_estatico', '')}<br>
                            <b>🌊 Nível Dinâmico:</b> {p_baixar.get('nivel_dinamico', '')}<br>
                            <b>📉 Profundidade da Bomba:</b> {p_baixar.get('profundidade_bomba', '')}<br>
                            <b>🚀 Modelo da Bomba:</b> {p_baixar.get('modelo_bomba', '')}<br>
                            <b>💨 Vazão:</b> {p_baixar.get('vazao', '')}<br>
                            <b>⚡ Fendas de Água:</b> {p_baixar.get('fendas_agua', '')}<br>
                            <b>🌐 Coordenadas:</b> {p_baixar.get('coordenadas', '')}<br>
                            <b>💎 Diâmetro Perf. em Rocha (MM):</b> {p_baixar.get('diametro_perf_rocha_mm', '')}<br>
                            <b>🪵 Diâmetro Perf. em Solo (MM):</b> {p_baixar.get('diametro_perf_solo_mm', '')}<br>
                            <b>⏳ Solo Argiloso ou Arenoso:</b> {p_baixar.get('solo_argiloso_arenoso', '')}<br>
                            <b>📏 Metragem Perfurada:</b> {p_baixar.get('metragem', '')} metros<br>
                            <b>👥 Funcionários na Obra:</b> {p_baixar.get('funcionarios', '')}<br>
                            <b>🧱 Materiais Utilizados:</b><br>{p_baixar.get('material', '')}<br>
                            <b>🛠️ Obs. Técnica:</b> {p_baixar.get('obs_tecnica', 'Nenhuma')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.checkbox("✏️ Corrigir/Editar este Relatório (ADM)", key="edit_mode_adm"):
                            with st.form("form_editar_poco_adm"):
                                novo_cl = st.text_input("Cliente", value=p_baixar.get('cliente', ''))
                                novo_tel = st.text_input("Telefone", value=p_baixar.get('telefone', ''))
                                novo_end_poco = st.text_input("Endereço do Poço", value=p_baixar.get('endereco_poco', ''))
                                novo_ci = st.text_input("Cidade", value=p_baixar.get('cidade', ''))
                                novo_data_elab = st.text_input("Data da Elaboração", value=p_baixar.get('data_elaboracao', ''))
                                novo_metodo_perf = st.text_input("Método de Perfuração", value=p_baixar.get('metodo_perfuracao', ''))
                                novo_prof_poco = st.text_input("Profundidade do Poço", value=p_baixar.get('profundidade_poco', ''))
                                novo_perf_solo_mt = st.text_input('Perfuração em Solo "Quantos Metros"', value=p_baixar.get('perfuracao_solo_metros', ''))
                                novo_tipo_revest = st.text_input("Tipo de Revestimento", value=p_baixar.get('tipo_revestimento', ''))
                                novo_qtd_revest = st.text_input("Quantidade de Revestimento", value=p_baixar.get('quantidade_revestimento', ''))
                                novo_tubo_retirada = st.text_input("Tubo de Retirada de Água e Qtde. (MT)", value=p_baixar.get('tubo_retirada_agua_qtde', ''))
                                novo_tipo_cabo = st.text_input("Tipo de Cabo e Qtde. (MT)", value=p_baixar.get('tipo_cabo_qtde', ''))
                                novo_tipo_filtro = st.text_input("Tipo de Filtro", value=p_baixar.get('tipo_filtro', ''))
                                novo_metros_filtro = st.text_input("Quantos Metros de Filtro", value=p_baixar.get('quantos_metros_filtro', ''))
                                novo_tipo_pre_filtro = st.text_input("Tipo de Pré Filtro", value=p_baixar.get('tipo_pre_filtro', ''))
                                
                                opcoes_cimentacao = ["Sim", "Não"]
                                idx_cim = opcoes_cimentacao.index(p_baixar.get('fez_cimentacao', 'Sim')) if p_baixar.get('fez_cimentacao', 'Sim') in opcoes_cimentacao else 0
                                novo_fez_cimentacao = st.selectbox("Fez Cimentação do Espaço Anelar?", opcoes_cimentacao, index=idx_cim)
                                
                                opcoes_laje = ["Sim", "Não"]
                                idx_laj = opcoes_laje.index(p_baixar.get('fez_laje_protecao', 'Sim')) if p_baixar.get('fez_laje_protecao', 'Sim') in opcoes_laje else 0
                                novo_fez_laje = st.selectbox("Fez Laje de Proteção Sanitária?", opcoes_laje, index=idx_laj)
                                
                                novo_qtd_pre_filtro = st.text_input("Quantidade de Pré Filtro? (Brita)", value=p_baixar.get('quantidade_pre_filtro_brita', ''))
                                novo_tampa = st.text_input("Tampa", value=p_baixar.get('tampa', ''))
                                novo_conexoes = st.text_area("Conexões Utilizadas", value=p_baixar.get('conexoes_utilizadas', ''))
                                novo_nivel_estatico = st.text_input("Nível Estático", value=p_baixar.get('nivel_estatico', ''))
                                novo_nivel_dinamico = st.text_input("Nível Diâmico", value=p_baixar.get('nivel_dinamico', ''))
                                novo_prof_bomba = st.text_input("Profundidade da Bomba", value=p_baixar.get('profundidade_bomba', ''))
                                novo_mod_bomba = st.text_input("Modelo da Bomba", value=p_baixar.get('modelo_bomba', ''))
                                novo_vazao = st.text_input("Vazão", value=p_baixar.get('vazao', ''))
                                novo_fendas_agua = st.text_input("Fendas de Água", value=p_baixar.get('fendas_agua', ''))
                                novo_coordenadas = st.text_input("Coordenadas", value=p_baixar.get('coordenadas', ''))
                                novo_diam_rocha = st.text_input("Diâmetro Perf. em Rocha e MM", value=p_baixar.get('diametro_perf_rocha_mm', ''))
                                novo_diam_solo = st.text_input("Diâmetro Perf. em Solo e MM", value=p_baixar.get('diametro_perf_solo_mm', ''))
                                
                                opcoes_solo = ["Argiloso", "Arenoso", "Misto", "Outro"]
                                idx_solo = opcoes_solo.index(p_baixar.get('solo_argiloso_arenoso', 'Argiloso')) if p_baixar.get('solo_argiloso_arenoso', 'Argiloso') in opcoes_solo else 0
                                novo_tipo_solo = st.selectbox("Solo Argiloso ou Arenoso", opcoes_solo, index=idx_solo)
                                
                                novo_mt = st.text_input("Metragem", value=p_baixar.get('metragem', ''))
                                novo_fun = st.text_input("Funcionários", value=p_baixar.get('funcionarios', ''))
                                novo_mat = st.text_area("Material", value=p_baixar.get('material', ''))
                                novo_obs = st.text_area("Observações Técnicas", value=p_baixar.get('obs_tecnica', ''))
                                
                                if st.form_submit_button("💾 Salvar Alterações"):
                                    idx_original = next(i for i, p in enumerate(st.session_state.dados[target_turma]["pocos"]) if id(p) == id(p_baixar))
                                    st.session_state.dados[target_turma]["pocos"][idx_original].update({
                                        "cliente": novo_cl, "telefone": novo_tel, "endereco_poco": novo_end_poco, "cidade": novo_ci,
                                        "data_elaboracao": novo_data_elab, "metodo_perfuracao": novo_metodo_perf, "profundidade_poco": novo_prof_poco,
                                        "perfuracao_solo_metros": novo_perf_solo_mt, "tipo_revestimento": novo_tipo_revest, "quantidade_revestimento": novo_qtd_revest,
                                        "tubo_retirada_agua_qtde": novo_tubo_retirada, "tipo_cabo_qtde": novo_tipo_cabo, "tipo_filtro": novo_tipo_filtro,
                                        "quantos_metros_filtro": novo_metros_filtro, "tipo_pre_filtro": novo_tipo_pre_filtro, "fez_cimentacao": novo_fez_cimentacao,
                                        "fez_laje_protecao": novo_fez_laje, "quantidade_pre_filtro_brita": novo_qtd_pre_filtro, "tampa": novo_tampa,
                                        "conexoes_utilizadas": novo_conexoes, "nivel_estatico": novo_nivel_estatico, "nivel_dinamico": novo_nivel_dinamico,
                                        "profundidade_bomba": novo_prof_bomba, "modelo_bomba": novo_mod_bomba, "vazao": novo_vazao, "fendas_agua": novo_fendas_agua,
                                        "coordenadas": novo_coordenadas, "diametro_perf_rocha_mm": novo_diam_rocha, "diametro_perf_solo_mm": novo_diam_solo,
                                        "solo_argiloso_arenoso": novo_tipo_solo, "metragem": novo_mt, "material": novo_mat, "funcionarios": novo_fun,
                                        "obs_tecnica": novo_obs
                                    })
                                    salvar_dados(st.session_state.dados)
                                    st.success("Relatório atualizado com sucesso!")
                                    st.rerun()
                        
                        linhas_pdf_poco = [
                            f"Data de Registro: {p_baixar.get('data', '')}",
                            f"Cliente: {p_baixar.get('cliente', '')}", f"Telefone: {p_baixar.get('telefone', '')}", f"Endereço do Poço: {p_baixar.get('endereco_poco', '')}", f"Cidade: {p_baixar.get('cidade', '')}",
                            f"Data da Elaboração: {p_baixar.get('data_elaboracao', '')}", f"Método de Perfuração: {p_baixar.get('metodo_perfuracao', '')}", f"Profundidade do Poço: {p_baixar.get('profundidade_poco', '')}",
                            f"Perfuração em Solo (m): {p_baixar.get('perfuracao_solo_metros', '')}", f"Tipo de Revestimento: {p_baixar.get('tipo_revestimento', '')}", f"Quantidade de Revestimento: {p_baixar.get('quantidade_revestimento', '')}",
                            f"Tubo Retirada e Qtd: {p_baixar.get('tubo_retirada_agua_qtde', '')}", f"Tipo de Cabo e Qtd (m): {p_baixar.get('tipo_cabo_qtde', '')}", f"Tipo de Filtro: {p_baixar.get('tipo_filtro', '')}",
                            f"Metros de Filtro: {p_baixar.get('quantos_metros_filtro', '')}", f"Tipo de Pré Filtro: {p_baixar.get('tipo_pre_filtro', '')}", f"Fez Cimentação?: {p_baixar.get('fez_cimentacao', '')}",
                            f"Fez Laje Proteção?: {p_baixar.get('fez_laje_protecao', '')}", f"Qtd Pré Filtro (Brita): {p_baixar.get('quantidade_pre_filtro_brita', '')}", f"Tampa: {p_baixar.get('tampa', '')}",
                            f"Conexões Utilizadas: {p_baixar.get('conexoes_utilizadas', '')}", f"Nível Estático: {p_baixar.get('nivel_estatico', '')}", f"Nível Dinâmico: {p_baixar.get('nivel_dinamico', '')}",
                            f"Profundidade da Bomba: {p_baixar.get('profundidade_bomba', '')}", f"Modelo da Bomba: {p_baixar.get('modelo_bomba', '')}", f"Vazão: {p_baixar.get('vazao', '')}",
                            f"Fendas de Água: {p_baixar.get('fendas_agua', '')}", f"Coordenadas: {p_baixar.get('coordenadas', '')}", f"Diâmetro Perf. Rocha (mm): {p_baixar.get('diametro_perf_rocha_mm', '')}",
                            f"Diâmetro Perf. Solo (mm): {p_baixar.get('diametro_perf_solo_mm', '')}", f"Solo Argiloso/Arenoso: {p_baixar.get('solo_argiloso_arenoso', '')}",
                            f"Metragem Perfurada: {p_baixar.get('metragem', '')} metros", f"Funcionarios na Obra: {p_baixar.get('funcionarios', '')}", 
                            f"Materiais Utilizados: {p_baixar.get('material', '')}", f"Obs. Técnica: {p_baixar.get('obs_tecnica', '')}"
                        ]
                        pdf_poco = exportar_para_pdf(f"Relatorio de Poco - {p_baixar.get('cliente', 'Sem Nome')}", linhas_pdf_poco)
                        st.download_button("📥 Baixar este Poço (PDF)", pdf_poco, f"poco_{p_baixar.get('cliente', 'SemNome')}_{p_baixar.get('data', '').replace('/','-')}.pdf", "application/pdf") 
                    else: 
                        st.caption("Nenhum poço encontrado.")
                
                with sub_m:
                    m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                    if m_mes:
                        pocos_disponiveis = sorted(list(set(m.get("poco", "Geral / Sem Poço Específico") for m in m_mes)))
                        poco_selecionado = st.selectbox("🔍 Escolha o Poço para visualizar fotos e vídeos:", pocos_disponiveis, key="poco_sel_midia_adm")
                        m_filtrado = [m for m in m_mes if m.get("poco", "Geral / Sem Poço Específico") == poco_selecionado]
                        
                        fotos_filtradas = [m for m in m_filtrado if "video" not in m.get("tipo", "").lower()]
                        videos_filtrados = [m for m in m_filtrado if "video" in m.get("tipo", "").lower()]
                        
                        st.markdown(f"### 📁 Arquivos de: *{poco_selecionado}*")
                        with st.expander("📸 FOTOS SALVAS"):
                            if fotos_filtradas:
                                for f in reversed(fotos_filtradas):
                                    st.write(f"📅 {f['data']}")
                                    st.image(f['caminho'], use_container_width=True)
                                    st.divider()
                            else: st.caption("Nenhuma foto localizada para este poço.")
                        
                        with st.expander("🎥 VÍDEOS SALVOS"):
                            if videos_filtrados:
                                for v in reversed(videos_filtrados):
                                    st.write(f"📅 {v['data']}")
                                    st.video(v['caminho'])
                                    st.divider()
                            else: st.caption("Nenhum vídeo localizado para este poço.")
            else:
                st.info("Nenhum registro encontrado para este colaborador.")

        with aba_adm:
            st.subheader("⚙️ Controle Global e Segurança")
            st.markdown("### 🔑 Gerenciador de Senhas das Equipes")
            with st.form("form_mudar_senha"):
                func_sel = st.selectbox("Selecione o Funcionário", TURMAS)
                nova_senha = st.text_input("Definir Nova Senha", type="password")
                if st.form_submit_button("🔒 ATUALIZAR SENHA"):
                    if nova_senha.strip() != "":
                        st.session_state.dados[func_sel]["senha_hash"] = gerar_hash(nova_senha)
                        salvar_dados(st.session_state.dados)
                        st.success(f"Senha do colaborador {func_sel} modificada e criptografada!")
                    else:
                        st.error("A senha não pode ser enviada em branco.")
            
            st.divider()
            if st.button("❌ RESETAR GASTOS DA SEMANA (TODAS AS EQUIPES)", type="primary"): 
                for t in TURMAS: 
                    st.session_state.dados[t]["transacoes"] = [] 
                salvar_dados(st.session_state.dados)
                st.success("Limites semanais resetados com sucesso!")
                st.rerun()

    else:
        aba1, aba2 = st.tabs(["📝 Registrar", "📅 Relatório Mensal"])
        
        with aba1: 
            t_ativa = st.session_state.turma 
            trans_semana = st.session_state.dados[t_ativa]["transacoes"] 
            
            total_gasto_dinheiro = sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Dinheiro')
            saldo_restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_gasto_dinheiro
            
            c1, c2 = st.columns(2) 
            c1.metric("💵 Saldo Restante", f"R$ {saldo_restante_dinheiro:.2f}") 
            c2.metric("💳 Acumulado Cartão", f"R$ {sum(t['valor'] for t in trans_semana if t.get('metodo') == 'Cartão'):.2f}") 
            
            mostrar_painel = st.toggle("📝 Registrar Despesas", value=False) 
            if mostrar_painel: 
                cat_principal = st.selectbox("Categoria", ["Café da Manhã", "Almoço", "Cafe da tarde", "Jantar", "Outros"]) 
                categoria_final = cat_principal
                
                if cat_principal == "Outros":
                    sub_cat = st.selectbox("Detalhe do Gasto", ["Pedágio", "Oficinas", "Lojas", "Outro (Especificar)"])
                    if sub_cat == "Lojas":
                        nome_loja = st.text_input("Qual o nome da loja?")
                        categoria_final = f"Loja: {nome_loja}"
                    elif sub_cat == "Outro (Especificar)":
                        desc_gasto = st.text_input("O que foi gasto?")
                        categoria_final = f"Outro: {desc_gasto}"
                    else:
                        categoria_final = sub_cat

                with st.form("form_final_envio", clear_on_submit=True): 
                    opcao_pgto = st.radio("Método de Pagamento", ["💵 Dinheiro", "💳 Cartão"], horizontal=True) 
                    valor_input = st.text_input("Valor R$") 
                    
                    if st.form_submit_button("SALVAR"): 
                        if not valor_input:
                            st.error("Informe o valor!")
                        else:
                            valor_final = float(valor_input.replace(",", ".")) 
                            novo_trans = {
                                "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m %H:%M"), 
                                "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"), 
                                "categoria": categoria_final, 
                                "metodo": "Dinheiro" if "Dinheiro" in opcao_pgto else "Cartão", 
                                "valor": valor_final
                            } 
                            st.session_state.dados[t_ativa]["transacoes"].append(novo_trans) 
                            st.session_state.dados[t_ativa]["historico"].append(novo_trans) 
                            salvar_dados(st.session_state.dados)
                            st.success("Despesa salva!")
                            st.rerun() 
                        
            mostrar_pocos = st.toggle("🚰 Poços Perfurados", value=False) 
            if mostrar_pocos: 
                with st.form("form_pocos", clear_on_submit=True): 
                    cl = st.text_input("Cliente")
                    tel = st.text_input("Telefone")
                    end_poco = st.text_input("Endereço do Poço")
                    ci = st.text_input("Cidade")
                    data_elab = st.text_input("Data da Elaboração (Dia que foi feito)")
                    metodo_perf = st.text_input("Método de Perfuração")
                    prof_poco = st.text_input("Profundidade do Poço")
                    perf_solo_mt = st.text_input('Perfuração em Solo "Quantos Metros"')
                    tipo_revest = st.text_input("Tipo de Revestimento")
                    qtd_revest = st.text_input("Quantidade de Revestimento")
                    tubo_retirada = st.text_input("Tubo de Retirada de Água e Qtde. (MT)")
                    tipo_cabo = st.text_input("Tipo de Cabo e Qtde. (MT)")
                    tipo_filtro = st.text_input("Tipo de Filtro")
                    metros_filtro = st.text_input("Quantos Metros de Filtro")
                    tipo_pre_filtro = st.text_input("Tipo de Pré Filtro")
                    
                    fez_cimentacao = st.selectbox("Fez Cimentação do Espaço Anelar?", ["Sim", "Não"])
                    fez_laje = st.selectbox("Fez Laje de Proteção Sanitária?", ["Sim", "Não"])
                    
                    qtd_pre_filtro = st.text_input("Quantidade de Pré Filtro? (Brita)")
                    tampa = st.text_input("Tampa")
                    conexoes = st.text_area("Conexões Utilizadas")
                    nivel_estatico = st.text_input("Nível Estático")
                    nivel_dinamico = st.text_input("Nível Dinâmico")
                    prof_bomba = st.text_input("Profundidade da Bomba")
                    mod_bomba = st.text_input("Modelo da Bomba")
                    vazao = st.text_input("Vazão")
                    fendas_agua = st.text_input("Fendas de Água")
                    coordenadas = st.text_input("Coordenadas")
                    diam_rocha = st.text_input("Diâmetro Perf. em Rocha e MM")
                    diam_solo = st.text_input("Diâmetro Perf. em Solo e MM")
                    
                    tipo_solo = st.selectbox("Solo Argiloso ou Arenoso", ["Argiloso", "Arenoso", "Misto", "Outro"])
                    
                    mt = st.text_input("Metragem")
                    mat = st.text_area("Material")
                    fun = st.text_input("Funcionários")
                    
                    st.subheader("Dados Técnicos Adicionais")
                    obs_tecnica = st.text_area("Observações Técnicas")
                    
                    st.markdown("---")
                    st.write("**Anexar Mídias desta Obra 📷**")
                    
                    foto_capturada = st.file_uploader("Câmera (Foto):", type=["jpg", "jpeg", "png"], key=f"foto_auto_{st.session_state.foto_key}")
                    video_gravado = st.file_uploader("Câmera (Vídeo):", type=["mp4", "mov", "avi", "3gp"], key=f"video_auto_{st.session_state.video_key}")
                    
                    if st.form_submit_button("SALVAR RELATÓRIO"): 
                        st.session_state.dados[t_ativa]["pocos"].append({
                            "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y"), 
                            "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"), 
                            "cliente": cl, "telefone": tel, "endereco_poco": end_poco, "cidade": ci,
                            "data_elaboracao": data_elab, "metodo_perfuracao": metodo_perf, "profundidade_poco": prof_poco,
                            "perfuracao_solo_metros": perf_solo_mt, "tipo_revestimento": tipo_revest, "quantidade_revestimento": qtd_revest,
                            "tubo_retirada_agua_qtde": tubo_retirada, "tipo_cabo_qtde": tipo_cabo, "tipo_filtro": tipo_filtro,
                            "quantos_metros_filtro": metros_filtro, "tipo_pre_filtro": tipo_pre_filtro, "fez_cimentacao": fez_cimentacao,
                            "fez_laje_protecao": fez_laje, "quantidade_pre_filtro_brita": qtd_pre_filtro, "tampa": tampa,
                            "conexoes_utilizadas": conexoes, "nivel_estatico": nivel_estatico, "nivel_dinamico": nivel_dinamico,
                            "profundidade_bomba": prof_bomba, "modelo_bomba": mod_bomba, "vazao": vazao, "fendas_agua": fendas_agua,
                            "coordenadas": coordenadas, "diametro_perf_rocha_mm": diam_rocha, "diametro_perf_solo_mm": diam_solo,
                            "solo_argiloso_arenoso": tipo_solo, "metragem": mt, "material": mat, "funcionarios": fun,
                            "obs_tecnica": obs_tecnica
                        }) 
                        
                        nome_poco_vinculo = f"{cl} ({ci})" if (cl or ci) else "Geral / Sem Poço Específico"
                        
                        if foto_capturada is not None:
                            bytes_foto = foto_capturada.getvalue()
                            encoded_foto = base64.b64encode(bytes_foto).decode('utf-8')
                            data_uri_foto = f"data:image/jpeg;base64,{encoded_foto}"
                            
                            st.session_state.dados[t_ativa]["midias"].append({
                                "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M"), 
                                "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"),
                                "caminho": data_uri_foto, "tipo": "image/jpeg", "poco": nome_poco_vinculo
                            })
                            st.session_state.foto_key += 1

                        if video_gravado is not None:
                            bytes_video = video_gravado.getvalue()
                            encoded_video = base64.b64encode(bytes_video).decode('utf-8')
                            data_uri_video = f"data:{video_gravado.type};base64,{encoded_video}"
                            
                            st.session_state.dados[t_ativa]["midias"].append({
                                "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M"), 
                                "ano_mes": datetime.now(FUSO_BRASILIA).strftime("%Y-%m"),
                                "caminho": data_uri_video, "tipo": video_gravado.type, "poco": nome_poco_vinculo
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
            st.subheader("📅 Histórico Mensal") 
            t_ativa = st.session_state.turma 
            
            if st.session_state.msg_sucesso:
                st.success(st.session_state.msg_sucesso)
                st.session_state.msg_sucesso = None
                
            hist = st.session_state.dados[t_ativa]["historico"] 
            pocos = st.session_state.dados[t_ativa].get("pocos", []) 
            midias = st.session_state.dados[t_ativa].get("midias", [])
            
            meses = sorted(list(set(t.get("ano_mes", datetime.now(FUSO_BRASILIA).strftime("%Y-%m")) for t in hist + pocos + midias)), reverse=True) 
            if meses: 
                mes_sel = st.selectbox("Escolha o mês", meses, key="mes_sel_turma") 
                sub_f, sub_p, sub_m = st.tabs(["💰 Custos", "𚚰 Poços", "📷 Mídias"]) 
                
                with sub_f: 
                    t_mes = [t for t in hist if t.get("ano_mes") == mes_sel] 
                    dias_disponiveis = sorted(list(set(t['data'][:5] for t in t_mes if 'data' in t)), reverse=True)
                    
                    if dias_disponiveis:
                        dias_pdf_sel = st.multiselect("📄 Selecione os dias para incluir no PDF:", dias_disponiveis, default=dias_disponiveis, key="dias_pdf_turma")
                        if dias_pdf_sel:
                            t_filtrado_pdf = [t for t in t_mes if t.get('data', '')[:5] in dias_pdf_sel]
                            linhas_pdf_fin = [f"{t['data']} | {t['categoria']}: R${t['valor']:.2f}" for t in t_filtrado_pdf]
                            # LINHA CORRIGIDA ABAIXO (linhas_pdf_fin em vez de lines_pdf_fin)
                            pdf_financeiro = exportar_para_pdf(f"Relatorio Financeiro - {t_ativa}", linhas_pdf_fin) 
                            st.download_button("📥 Baixar Relatório Financeiro (PDF)", pdf_financeiro, f"financeiro_{t_ativa}_{mes_sel}.pdf", "application/pdf") 
                        else:
                            st.warning("Selecione pelo menos um dia para gerar o relatório PDF.")
                            
                        st.markdown("---")
                        dia_sel = st.selectbox("🔍 Escolha o dia para analisar custos na tela:", dias_disponiveis, key="dia_sel_turma_custos")
                        t_dia = [t for t in t_mes if t.get('data', '')[:5] == dia_sel]
                        for t in reversed(t_dia): 
                            st.write(f"💵 {t['data']} - {t['categoria']} - R${t['valor']:.2f}") 
                    else:
                        st.caption("Nenhum custo registrado.")
                
                with sub_p: 
                    p_mes = [p for p in pocos if p.get("ano_mes") == mes_sel] 
                    if p_mes: 
                        sel_poco = st.selectbox("Escolha o poço para analisar/baixar:", [f"{p.get('data', 'Sem Data')} - {p.get('cliente', 'Sem Nome')}" for p in p_mes], key="sel_poco_turma") 
                        p_baixar = next(p for p in p_mes if f"{p.get('data', 'Sem Data')} - {p.get('cliente', 'Sem Nome')}" == sel_poco) 
                        
                        st.markdown(f"""
                        <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid #0047AB; margin-bottom: 15px;'>
                            <h4 style='margin-top:0;'>📋 Dados Atuais do Relatório</h4>
                            <b>📍 Cliente:</b> {p_baixar.get('cliente', '')}<br>
                            <b>📞 Telefone:</b> {p_baixar.get('telefone', '')}<br>
                            <b>🏠 Endereço do Poço:</b> {p_baixar.get('endereco_poco', '')}<br>
                            <b>🏙️ Cidade:</b> {p_baixar.get('cidade', '')}<br>
                            <b>📅 Data da Elaboração:</b> {p_baixar.get('data_elaboracao', '')}<br>
                            <b>⚙️ Método de Perfuração:</b> {p_baixar.get('metodo_perfuracao', '')}<br>
                            <b>📏 Profundidade do Poço:</b> {p_baixar.get('profundidade_poco', '')}<br>
                            <b>🌱 Perfuração em Solo (Metros):</b> {p_baixar.get('perfuracao_solo_metros', '')}<br>
                            <b>🛡️ Tipo de Revestimento:</b> {p_baixar.get('tipo_revestimento', '')}<br>
                            <b>📦 Quantidade de Revestimento:</b> {p_baixar.get('quantidade_revestimento', '')}<br>
                            <b>🚰 Tubo de Retirada de Água e Qtd (MT):</b> {p_baixar.get('tubo_retirada_agua_qtde', '')}<br>
                            <b>🔌 Tipo de Cabo e Qtd (MT):</b> {p_baixar.get('tipo_cabo_qtde', '')}<br>
                            <b>🧹 Tipo de Filtro:</b> {p_baixar.get('tipo_filtro', '')}<br>
                            <b>📏 Metros de Filtro:</b> {p_baixar.get('quantos_metros_filtro', '')}<br>
                            <b>⏳ Tipo de Pré Filtro:</b> {p_baixar.get('tipo_pre_filtro', '')}<br>
                            <b>🧱 Cimentação do Espaço Anelar?:</b> {p_baixar.get('fez_cimentacao', '')}<br>
                            <b>🧰 Laje de Proteção Sanitária?:</b> {p_baixar.get('fez_laje_protecao', '')}<br>
                            <b>🪨 Qtd de Pré Filtro (Brita):</b> {p_baixar.get('quantidade_pre_filtro_brita', '')}<br>
                            <b>🔒 Tampa:</b> {p_baixar.get('tampa', '')}<br>
                            <b>🔗 Conexões Utilizadas:</b> {p_baixar.get('conexoes_utilizadas', '')}<br>
                            <b>💧 Nível Estático:</b> {p_baixar.get('nivel_estatico', '')}<br>
                            <b>🌊 Nível Dinâmico:</b> {p_baixar.get('nivel_dinamico', '')}<br>
                            <b>📉 Profundidade da Bomba:</b> {p_baixar.get('profundidade_bomba', '')}<br>
                            <b>🚀 Modelo da Bomba:</b> {p_baixar.get('modelo_bomba', '')}<br>
                            <b>💨 Vazão:</b> {p_baixar.get('vazao', '')}<br>
                            <b>⚡ Fendas de Água:</b> {p_baixar.get('fendas_agua', '')}<br>
                            <b>🌐 Coordenadas:</b> {p_baixar.get('coordenadas', '')}<br>
                            <b>💎 Diâmetro Perf. em Rocha (MM):</b> {p_baixar.get('diametro_perf_rocha_mm', '')}<br>
                            <b>🪵 Diâmetro Perf. em Solo (MM):</b> {p_baixar.get('diametro_perf_solo_mm', '')}<br>
                            <b>⏳ Solo Argiloso ou Arenoso:</b> {p_baixar.get('solo_argiloso_arenoso', '')}<br>
                            <b>📏 Metragem Perfurada:</b> {p_baixar.get('metragem', '')} metros<br>
                            <b>👥 Funcionários na Obra:</b> {p_baixar.get('funcionarios', '')}<br>
                            <b>🧱 Materiais Utilizados:</b><br>{p_baixar.get('material', '')}<br>
                            <b>🛠️ Obs. Técnica:</b> {p_baixar.get('obs_tecnica', 'Nenhuma')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.checkbox("✏️ Editar este Relatório", key="edit_mode_turma"):
                            with st.form("form_editar_poco_turma"):
                                novo_cl = st.text_input("Cliente", value=p_baixar.get('cliente', ''))
                                novo_tel = st.text_input("Telefone", value=p_baixar.get('telefone', ''))
                                novo_end_poco = st.text_input("Endereço do Poço", value=p_baixar.get('endereco_poco', ''))
                                novo_ci = st.text_input("Cidade", value=p_baixar.get('cidade', ''))
                                novo_data_elab = st.text_input("Data da Elaboração", value=p_baixar.get('data_elaboracao', ''))
                                novo_metodo_perf = st.text_input("Método de Perfuração", value=p_baixar.get('metodo_perfuracao', ''))
                                novo_prof_poco = st.text_input("Profundidade do Poço", value=p_baixar.get('profundidade_poco', ''))
                                novo_perf_solo_mt = st.text_input('Perfuração em Solo "Quantos Metros"', value=p_baixar.get('perfuracao_solo_metros', ''))
                                novo_tipo_revest = st.text_input("Tipo de Revestimento", value=p_baixar.get('tipo_revestimento', ''))
                                novo_qtd_revest = st.text_input("Quantidade de Revestimento", value=p_baixar.get('quantidade_revestimento', ''))
                                novo_tubo_retirada = st.text_input("Tubo de Retirada de Água e Qtde. (MT)", value=p_baixar.get('tubo_retirada_agua_qtde', ''))
                                novo_tipo_cabo = st.text_input("Tipo de Cabo e Qtde. (MT)", value=p_baixar.get('tipo_cabo_qtde', ''))
                                novo_tipo_filtro = st.text_input("Tipo de Filtro", value=p_baixar.get('tipo_filtro', ''))
                                novo_metros_filtro = st.text_input("Quantos Metros de Filtro", value=p_baixar.get('quantos_metros_filtro', ''))
                                novo_tipo_pre_filtro = st.text_input("Tipo de Pré Filtro", value=p_baixar.get('tipo_pre_filtro', ''))
                                
                                opcoes_cimentacao = ["Sim", "Não"]
                                idx_cim = opcoes_cimentacao.index(p_baixar.get('fez_cimentacao', 'Sim')) if p_baixar.get('fez_cimentacao', 'Sim') in opcoes_cimentacao else 0
                                novo_fez_cimentacao = st.selectbox("Fez Cimentação do Espaço Anelar?", opcoes_cimentacao, index=idx_cim)
                                
                                opcoes_laje = ["Sim", "Não"]
                                idx_laj = opcoes_laje.index(p_baixar.get('fez_laje_protecao', 'Sim')) if p_baixar.get('fez_laje_protecao', 'Sim') in opcoes_laje else 0
                                novo_fez_laje = st.selectbox("Fez Laje de Proteção Sanitária?", opcoes_laje, index=idx_laj)
                                
                                novo_qtd_pre_filtro = st.text_input("Quantidade de Pré Filtro? (Brita)", value=p_baixar.get('quantidade_pre_filtro_brita', ''))
                                novo_tampa = st.text_input("Tampa", value=p_baixar.get('tampa', ''))
                                novo_conexoes = st.text_area("Conexões Utilizadas", value=p_baixar.get('conexoes_utilizadas', ''))
                                novo_nivel_estatico = st.text_input("Nível Estático", value=p_baixar.get('nivel_estatico', ''))
                                novo_nivel_dinamico = st.text_input("Nível Dinâmico", value=p_baixar.get('nivel_dinamico', ''))
                                novo_prof_bomba = st.text_input("Profundidade da Bomba", value=p_baixar.get('profundidade_bomba', ''))
                                novo_mod_bomba = st.text_input("Modelo da Bomba", value=p_baixar.get('modelo_bomba', ''))
                                novo_vazao = st.text_input("Vazão", value=p_baixar.get('vazao', ''))
                                novo_fendas_agua = st.text_input("Fendas de Água", value=p_baixar.get('fendas_agua', ''))
                                novo_coordenadas = st.text_input("Coordenadas", value=p_baixar.get('coordenadas', ''))
                                novo_diam_rocha = st.text_input("Diâmetro Perf. em Rocha e MM", value=p_baixar.get('diametro_perf_rocha_mm', ''))
                                novo_diam_solo = st.text_input("Diâmetro Perf. em Solo e MM", value=p_baixar.get('diametro_perf_solo_mm', ''))
                                
                                opcoes_solo = ["Argiloso", "Arenoso", "Misto", "Outro"]
                                idx_solo = opcoes_solo.index(p_baixar.get('solo_argiloso_arenoso', 'Argiloso')) if p_baixar.get('solo_argiloso_arenoso', 'Argiloso') in opcoes_solo else 0
                                novo_tipo_solo = st.selectbox("Solo Argiloso ou Arenoso", opcoes_solo, index=idx_solo)
                                
                                novo_mt = st.text_input("Metragem", value=p_baixar.get('metragem', ''))
                                novo_fun = st.text_input("Funcionários", value=p_baixar.get('funcionarios', ''))
                                novo_mat = st.text_area("Material", value=p_baixar.get('material', ''))
                                novo_obs = st.text_area("Observações Técnicas", value=p_baixar.get('obs_tecnica', ''))
                                
                                if st.form_submit_button("💾 Salvar Alterações"):
                                    idx_original = next(i for i, p in enumerate(st.session_state.dados[t_ativa]["pocos"]) if id(p) == id(p_baixar))
                                    st.session_state.dados[t_ativa]["pocos"][idx_original].update({
                                        "cliente": novo_cl, "telefone": novo_tel, "endereco_poco": novo_end_poco, "cidade": novo_ci,
                                        "data_elaboracao": novo_data_elab, "metodo_perfuracao": novo_metodo_perf, "profundidade_poco": novo_prof_poco,
                                        "perfuracao_solo_metros": novo_perf_solo_mt, "tipo_revestimento": novo_tipo_revest, "quantidade_revestimento": novo_qtd_revest,
                                        "tubo_retirada_agua_qtde": novo_tubo_retirada, "tipo_cabo_qtde": novo_tipo_cabo, "tipo_filtro": novo_tipo_filtro,
                                        "quantos_metros_filtro": novo_metros_filtro, "tipo_pre_filtro": novo_tipo_pre_filtro, "fez_cimentacao": novo_fez_cimentacao,
                                        "fez_laje_protecao": novo_fez_laje, "quantidade_pre_filtro_brita": novo_qtd_pre_filtro, "tampa": novo_tampa,
                                        "conexoes_utilizadas": novo_conexoes, "nivel_estatico": novo_nivel_estatico, "nivel_dinamico": novo_nivel_dinamico,
                                        "profundidade_bomba": novo_prof_bomba, "modelo_bomba": novo_mod_bomba, "vazao": novo_vazao, "fendas_agua": novo_fendas_agua,
                                        "coordenadas": novo_coordenadas, "diametro_perf_rocha_mm": novo_diam_rocha, "diametro_perf_solo_mm": novo_diam_solo,
                                        "solo_argiloso_arenoso": novo_tipo_solo, "metragem": novo_mt, "material": novo_mat, "funcionarios": novo_fun, 
                                        "obs_tecnica": novo_obs
                                    })
                                    salvar_dados(st.session_state.dados)
                                    st.success("Relatório corrigido com sucesso!")
                                    st.rerun()
                        
                        linhas_pdf_poco = [
                            f"Data de Registro: {p_baixar.get('data', '')}",
                            f"Cliente: {p_baixar.get('cliente', '')}", f"Telefone: {p_baixar.get('telefone', '')}", f"Endereço do Poço: {p_baixar.get('endereco_poco', '')}", f"Cidade: {p_baixar.get('cidade', '')}",
                            f"Data da Elaboração: {p_baixar.get('data_elaboracao', '')}", f"Método de Perfuração: {p_baixar.get('metodo_perfuracao', '')}", f"Profundidade do Poço: {p_baixar.get('profundidade_poco', '')}",
                            f"Perfuração em Solo (m): {p_baixar.get('perfuracao_solo_metros', '')}", f"Tipo de Revestimento: {p_baixar.get('tipo_revestimento', '')}", f"Quantidade de Revestimento: {p_baixar.get('quantidade_revestimento', '')}",
                            f"Tubo Retirada e Qtd: {p_baixar.get('tubo_retirada_agua_qtde', '')}", f"Tipo de Cabo e Qtd (m): {p_baixar.get('tipo_cabo_qtde', '')}", f"Tipo de Filtro: {p_baixar.get('tipo_filtro', '')}",
                            f"Metros de Filtro: {p_baixar.get('quantos_metros_filtro', '')}", f"Tipo de Pré Filtro: {p_baixar.get('tipo_pre_filtro', '')}", f"Fez Cimentação?: {p_baixar.get('fez_cimentacao', '')}",
                            f"Fez Laje Proteção?: {p_baixar.get('fez_laje_protecao', '')}", f"Qtd Pré Filtro (Brita): {p_baixar.get('quantidade_pre_filtro_brita', '')}", f"Tampa: {p_baixar.get('tampa', '')}",
                            f"Conexões Utilizadas: {p_baixar.get('conexoes_utilizadas', '')}", f"Nível Estático: {p_baixar.get('nivel_estatico', '')}", f"Nível Dinâmico: {p_baixar.get('nivel_dinamico', '')}",
                            f"Profundidade da Bomba: {p_baixar.get('profundidade_bomba', '')}", f"Modelo da Bomba: {p_baixar.get('modelo_bomba', '')}", f"Vazão: {p_baixar.get('vazao', '')}",
                            f"Fendas de Água: {p_baixar.get('fendas_agua', '')}", f"Coordenadas: {p_baixar.get('coordenadas', '')}", f"Diâmetro Perf. Rocha (mm): {p_baixar.get('diametro_perf_rocha_mm', '')}",
                            f"Diâmetro Perf. Solo (mm): {p_baixar.get('diametro_perf_solo_mm', '')}", f"Solo Argiloso/Arenoso: {p_baixar.get('solo_argiloso_arenoso', '')}",
                            f"Metragem Perfurada: {p_baixar.get('metragem', '')} metros", f"Funcionarios na Obra: {p_baixar.get('funcionarios', '')}", 
                            f"Materiais Utilizados: {p_baixar.get('material', '')}", f"Obs. Técnica: {p_baixar.get('obs_tecnica', '')}"
                        ]
                        pdf_poco = exportar_para_pdf(f"Relatorio de Poco - {p_baixar.get('cliente', 'Sem Nome')}", linhas_pdf_poco)
                        st.download_button("📥 Baixar este Poço (PDF)", pdf_poco, f"poco_{p_baixar.get('cliente', 'SemNome')}_{p_baixar.get('data', '').replace('/','-')}.pdf", "application/pdf") 
                    else: 
                        st.caption("Nenhum poço encontrado.")
                
                with sub_m:
                    m_mes = [m for m in midias if m.get("ano_mes") == mes_sel]
                    if m_mes:
                        pocos_disponiveis = sorted(list(set(m.get("poco", "Geral / Sem Poço Específico") for m in m_mes)))
                        poco_selecionado = st.selectbox("🔍 Escolha o Poço para visualizar fotos e vídeos:", pocos_disponiveis, key="poco_sel_midia_turma")
                        m_filtrado = [m for m in m_mes if m.get("poco", "Geral / Sem Poço Específico") == poco_selecionado]
                        
                        fotos_filtradas = [m for m in m_filtrado if "video" not in m.get("tipo", "").lower()]
                        videos_filtrados = [m for m in m_filtrado if "video" in m.get("tipo", "").lower()]
                        
                        st.markdown(f"### 📁 Arquivos de: *{poco_selecionado}*")
                        with st.expander("📸 FOTOS SALVAS"):
                            if fotos_filtradas:
                                for f in reversed(fotos_filtradas):
                                    st.write(f"📅 {f['data']}")
                                    st.image(f['caminho'], use_container_width=True)
                                    st.divider()
                            else: st.caption("Nenhuma foto localizada para este poço.")
                        with st.expander("🎥 VÍDEOS SALVOS"):
                            if videos_filtrados:
                                for v in reversed(videos_filtrados):
                                    st.write(f"📅 {v['data']}")
                                    st.video(v['caminho'])
                                    st.divider()
                            else: st.caption("Nenhum vídeo localizado para este poço.")
                    else: st.caption("Nenhuma mídia registrada para este colaborador neste mês.")
