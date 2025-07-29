# @app.command()
# @app.command(name="l", hidden=True)
# def log(application_id: str):
#     """
#     Exibe log do YARN por applicationId.
#     """

#     console = Console()
#     extra_vars = {"app_id": application_id}
#     with console.status("[bold green]Buscando logs...[/bold green]", spinner="dots"):
#         result = run_playbook("show_logs.yml", extra_vars=extra_vars)

#     match = re.search(r'"msg":\s*"(.+?)"\s*}', result, re.DOTALL)
#     if not match:
#         console.print(
#             "[red]❌ Não foi possível encontrar a saída 'msg' no retorno do playbook.[/red]"
#         )
#         return

#     msg_encoded = match.group(1)

#     try:
#         # Decodifica escapes unicode e converte encoding para UTF-8 corretamente
#         msg_decoded = codecs.decode(msg_encoded, "unicode_escape")
#         msg_decoded = msg_decoded.encode("latin1").decode("utf-8")
#     except Exception as e:
#         console.print(f"[red]❌ Erro ao decodificar os logs: {e}[/red]")
#         return

#     # Extrai cargas concluídas com sucesso e erros
#     cargas_ok = re.findall(r"✅ Carga concluída para ([^\n!]+)!", msg_decoded)
#     cargas_erro = re.findall(
#         r"❌ (?:Erro ao carregar dados|Erro ao extrair dados) para ([^\n:]+)",
#         msg_decoded,
#     )

#     # Prepara dados para a tabela
#     rows = []
#     for tabela in cargas_ok:
#         rows.append(["✅ Sucesso", tabela.strip()])
#     for tabela in cargas_erro:
#         rows.append(["❌ Erro", tabela.strip()])

#     # Define colunas da tabela
#     columns = [
#         {"header": "Status", "style": "bold"},
#         {"header": "Tabela", "style": "cyan"},
#     ]

#     # Gera tabela no console
#     generate_table(title="Resumo da Carga", columns=columns, rows=rows)

#     # Imprime resumo final
#     console.print(
#         f"[bold green]✅ Cargas concluídas:[/bold green] {len(cargas_ok)} | "
#         f"[bold red]❌ Erros:[/bold red] {len(cargas_erro)}"
#     )
