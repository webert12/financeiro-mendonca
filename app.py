import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
DATA_FILE = "gastos_dados.json"
LIMITE_DINHEIRO_SEMANAL = 500.00

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

# Função auxiliar para desenhar barras de progresso em texto
def gerar_barra(valor_atual, valor_maximo, tamanho_barra=20):
    if valor_maximo <= 0:
        return "□" * tamanho_barra, 0
    porcentagem = min(int((valor_atual / valor_maximo) * 100), 100)
    preenchido = int((porcentagem / 100) * tamanho_barra)
    barra = "■" * preenchido + "□" * (tamanho_barra - preenchido)
    return barra, porcentagem

# 2. Renderiza o Painel Visual com as barras por método de pagamento
def exibir_painel(dados):
    os.system("clear")
    console.print("[bold green]══ CONTROLADOR FINANCEIRO CORPORATIVO ══[/bold green]\n")
    
    # Separação e soma dos gastos da semana atual
    total_dinheiro = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo", "Dinheiro") == "Dinheiro")
    total_cartao = sum(t["valor"] for t in dados["transacoes"] if t.get("metodo", "Dinheiro") == "Cartão")
    restante_dinheiro = LIMITE_DINHEIRO_SEMANAL - total_dinheiro
    
    # --- VISUALIZAÇÃO DO DINHEIRO EM ESPÉCIE ---
    barra_din, pct_din = gerar_barra(total_dinheiro, LIMITE_DINHEIRO_SEMANAL)
    console.print(f"[bold cyan]💵 Dinheiro em Espécie (Limite: R$ {LIMITE_DINHEIRO_SEMANAL:.2f})[/bold cyan]")
    console.print(f"[{barra_din}] {pct_din}% consumido")
    console.print(f"Gasto: [bold red]R$ {total_dinheiro:.2f}[/bold red] | Restante: [bold green]R$ {restante_dinheiro:.2f}[/bold green]\n")
    
    # --- VISUALIZAÇÃO DO CARTÃO CORPORATIVO ---
    barra_card, _ = gerar_barra(total_cartao, max(total_cartao, 500.00))
    console.print(f"[bold magenta]💳 Cartão Corporativo (Fluxo Acumulado)[/bold magenta]")
    console.print(f"[{barra_card}] Acumulando...")
    console.print(f"Total Gasto no Cartão: [bold yellow]R$ {total_cartao:.2f}[/bold yellow]\n")
    
    console.print("[gray]--------------------------------------------------[/gray]")
    
    # Tabela de Histórico Recente da Semana Ativa
    table = Table(title="Gastos da Semana Atual", expand=True)
    table.add_column("Data", style="cyan", width=12)
    table.add_column("Descrição do Lançamento", style="white")
    table.add_column("Valor", justify="right", style="green", width=12)
    
    ultimas_transacoes = dados["transacoes"][-6:]
    for t in ultimas_transacoes:
        metodo = t.get("metodo", "Dinheiro")
        
        if metodo == "Cartão":
            descricao_formatada = f"{t['categoria']}, [magenta]pago com Cartão[/magenta]"
        else:
            descricao_formatada = f"{t['categoria']}, [cyan]pago com Dinheiro[/cyan]"
            
        table.add_row(t["data"], descricao_formatada, f"R$ {t['valor']:.2f}")
        
    console.print(table)

# 3. Fluxo de inserção de novos gastos
def adicionar_gasto(dados):
    console.print("\n[bold yellow]Selecione o que foi gasto:[/bold yellow]")
    categorias = [
        "Café da Manhã", 
        "Almoço", 
        "Café da Tarde", 
        "Jantar", 
        "Pedágio / Transporte", 
        "Outros"
    ]
    
    for idx, cat in enumerate(categorias, 1):
        console.print(f"[bold cyan]{idx}.[/bold cyan] {cat}")
        
    try:
        opcao_cat = int(input("\nEscolha o número: "))
        if not (1 <= opcao_cat <= len(categorias)):
            raise ValueError
        categoria_escolhida = categorias[opcao_cat - 1]
        
        console.print("\n[bold yellow]Qual foi o método de pagamento?[/bold yellow]")
        console.print("[bold cyan]1.[/bold cyan] Dinheiro em Espécie")
        console.print("[bold magenta]2.[/bold magenta] Cartão de Crédito")
        opcao_pgto = input("\nEscolha a forma (1 ou 2): ")
        
        if opcao_pgto == "1":
            metodo = "Dinheiro"
        elif opcao_pgto == "2":
            metodo = "Cartão"
        else:
            raise ValueError
            
        valor = float(input(f"Valor gasto no {metodo} R$: ").replace(",", "."))
        
        agora = datetime.now()
        nova_transacao = {
            "data": agora.strftime("%d/%m %H:%M"),
            "ano_mes": agora.strftime("%Y-%m"),   # Ex: "2026-05"
            "semana_ano": agora.strftime("%U"),
            "categoria": categoria_escolhida,
            "metodo": metodo,
            "valor": valor
        }
        
        # Se os registros antigos no histórico permanente não tiverem o campo "ano_mes", adicionamos por garantia
        dados["transacoes"].append(nova_transacao)
        dados["historico"].append(nova_transacao)
        
        salvar_dados(dados)
        console.print("\n[bold green]✓ Gasto registrado com sucesso de forma permanente![/bold green]")
    except (ValueError, IndexError):
        console.print("\n[bold red]Entrada inválida. Operação cancelada.[/bold red]")
    
    input("\nPressione Enter para retornar...")

# 5. Exibe os meses disponíveis e filtra os dados salvos permanentemente
def exibir_historico_acumulado(dados):
    os.system("clear")
    console.print("[bold green]══ HISTÓRICO MENSAL ARQUIVADO ══[/bold green]\n")
    
    if not dados["historico"]:
        console.print("[yellow]Nenhum dado arquivado ainda no histórico permanente.[/yellow]")
        input("\nPressione Enter para voltar...")
        return

    # 1. Coleta todos os meses únicos disponíveis de forma ordenada
    meses_disponiveis = sorted(list(set(t.get("ano_mes", datetime.now().strftime("%Y-%m")) for t in dados["historico"])), reverse=True)
    
    console.print("[bold yellow]Selecione o mês para consulta:[/bold yellow]")
    for idx, mes in enumerate(meses_disponiveis, 1):
        # Converte "2026-05" para um formato mais legível "05/2026"
        ano, mes_num = mes.split("-")
        console.print(f"[bold cyan]{idx}.[/bold cyan] {mes_num}/{ano}")
        
    try:
        escolha = int(input("\nDigite o número do mês desejado: "))
        if not (1 <= escolha <= len(meses_disponiveis)):
            raise ValueError
            
        mes_escolhido = meses_disponiveis[escolha - 1]
        ano_exib, mes_exib = mes_escolhido.split("-")
        
        # 2. Filtra as transações pertencentes àquele mês escolhido
        transacoes_mes = [t for t in dados["historico"] if t.get("ano_mes", "") == mes_escolhido]
        
        # Somas parciais do mês selecionado
        total_din_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Dinheiro")
        total_card_mes = sum(t["valor"] for t in transacoes_mes if t.get("metodo") == "Cartão")
        
        os.system("clear")
        console.print(f"[bold green]══ RELATÓRIO DE GASTOS: {mes_exib}/{ano_exib} ══[/bold green]\n")
        console.print(f"💵 Total em Dinheiro: [bold cyan]R$ {total_din_mes:.2f}[/bold cyan]")
        console.print(f"💳 Total no Cartão:   [bold magenta]R$ {total_card_mes:.2f}[/bold magenta]\n")
        
        # Monta a tabela para o mês filtrado
        table_mes = Table(title=f"Lançamentos Arquivados em {mes_exib}/{ano_exib}", expand=True)
        table_mes.add_column("Data", style="cyan", width=12)
        table_mes.add_column("Categoria", style="white")
        table_mes.add_column("Forma Pgto", style="yellow")
        table_mes.add_column("Valor", justify="right", style="green")
        
        for t in transacoes_mes:
            metodo = t.get("metodo", "Dinheiro")
            via_cor = f"[bold magenta]Cartão[/bold magenta]" if metodo == "Cartão" else f"[bold cyan]Dinheiro[/bold cyan]"
            table_mes.add_row(t["data"], t["categoria"], via_cor, f"R$ {t['valor']:.2f}")
            
        console.print(table_mes)
        
    except (ValueError, IndexError):
        console.print("\n[bold red]Opção inválida. Retornando ao menu...[/bold red]")
        
    input("\nPressione Enter para voltar ao menu principal...")

# 4. Loop Principal do Aplicativo
def main():
    dados = carregar_dados()
    while True:
        exibir_painel(dados)
        console.print("[bold yellow]Menu Principal:[/bold yellow]")
        console.print("[bold cyan]1.[/bold cyan] Registrar Novo Gasto")
        console.print("[bold cyan]2.[/bold cyan] Resetar Balanço Semanal (Limpa barras)")
        console.print("[bold cyan]3.[/bold cyan] Ver Histórico por Mês")
        console.print("[bold cyan]4.[/bold cyan] Sair")
        
        opcao = input("\nO que deseja fazer? ")
        
        if opcao == "1":
            adicionar_gasto(dados)
        elif opcao == "2":
            confirmar = input("Zerar barras da semana atual? O histórico permanente NÃO será apagado (s/n): ")
            if confirmar.lower() == 's':
                dados["transacoes"] = [] # Apaga apenas os gastos exibidos na semana atual
                salvar_dados(dados)
                console.print("\n[bold green]✓ Balanço da semana resetado com sucesso![/bold green]")
                input("\nPressione Enter...")
        elif opcao == "3":
            exibir_historico_acumulado(dados)
        elif opcao == "4":
            console.print("[bold green]Até mais e bom trabalho![/bold green]")
            break

if __name__ == "__main__":
    main()
