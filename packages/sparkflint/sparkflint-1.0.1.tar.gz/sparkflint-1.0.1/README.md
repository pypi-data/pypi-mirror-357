# SparkFlintCLI

[![PyPI version](https://badge.fury.io/py/sparkflint.svg)](https://badge.fury.io/py/sparkflint)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/sparkflint)](https://pypi.org/project/sparkflint/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)

## Descrição

Esse projeto é um CLI desenvolvido com python, typer e ansible.

**SparkFlintCLI** é uma ferramenta de linha de comando que permite a **gestão** e a **submissão** de aplicações Apache Spark em ambientes remotos.

## Instalação

### Pré-requisitos

- Python 3.8
- Typer
- Ansible
- Rich

O método mais fácil para instalar é usando `pip`:

`pip install sparkflint`

Para instalar do repositório Github:

```bash
git clone https://github.com/RibeiroWiliam/sparkflint-cli.git
cd sparkflint-cli
pip install -e .
```

Para detalhes de uso, verifique `sparkflint --help`.

## Modo de Uso

### 1. Inicie o sparkflint

Antes de começar a usar sparkflint, é importante definir as principais configurações, como:

- origin: endereço http da origem dos metadados
- username: nome de usuário da origem dos metadados
- password: senha da origem dos metadados

Para isso, use `sparkflint init`:

```bash
sparkflint init
```

```bash
Iniciando configuração...
Origin: http://host-example:8000
Usuário: user_example1
Senha:
✔ URL de Origin válida.
✔ Usuário e senha válidos.


✔ Configuração salva em /Users/UserExample/.sparkflint/config.toml.
Configuração concluída! Você já pode usar os comandos da CLI normalmente.
```

### 2. Configurando os hosts

O próximo passo é configurar os hosts de seu ambiente remoto.

Para isso, use `sparkflint add host`:

```bash
sparkflint add host [hostname]
```

```bash
sparkflint add host host-example2.net
sparkflint a h 12.34.56.78
```

## Principais comandos

- `sparkflint add`
- `sparkflint init`
- `sparkflint kill`
- `sparkflint list`
- `sparkflint open`
- `sparkflint remove`
- `sparkflint run`
- `sparkflint set`
- `sparkflint show`
- `sparkflint status`
- `sparkflint test`

### sparkflint add

Use `sparkflint add` para adicionar hosts.

```bash
sparkflint add host [hostname1],[hostname2]    # Adiciona 2 novos hosts
```

Exemplos:

```bash
sparkflint add host host-example2.net
sparkflint a h 12.34.56.78
```

Opções:

```bash
sparkflint add host [hostname]
```

### sparkflint init

Use `sparkflint init` para inicializar a SparkFlintCLI ou reescrever todas as configs.

```bash
sparkflint init     # Inicializa a SparkFlintCLI.
```

```bash
Iniciando configuração...
Origin: http://host-example:8000
Usuário: user_example1
Senha:
✔ URL de Origin válida.
✔ Usuário e senha válidos.


✔ Configuração salva em /Users/UserExample/.sparkflint/config.toml.
Configuração concluída! Você já pode usar os comandos da CLI normalmente.
```

Options:

```bash
sparkflint init --file [filename]     # Inicializa a SparkFlintCLI a partir de um arquivo de config.
```

### sparkflint list

Use `sparkflint list` para listar aplicações spark, pipelines disponíveis ou dags Airflow

```bash
sparkflint list apps     # Lista aplicações YARN em andamento
```

```bash
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━┳━━━━━━┳━━━┳━━━━━━━━┳━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Application-Id            ┃ Application-Name                    ┃ Application ┃ U ┃ Queu ┃ S ┃ Final- ┃ Pr ┃ Tracking-URL                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━╇━━━━━━╇━━━╇━━━━━━━━╇━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ application_1741779469365 │ llap0                               │ yarn-servic │ h │ defa │ R │ UNDEFI │ 10 │ N/A                                 │
│ application_1749125299497 │ sped_processar                      │ SPARK       │ a │ work │ R │ UNDEFI │ 10 │ http://WN04-SEPLAD.fazenda.net:3555 │
│ application_1749125299497 │ HIVE-cb4adc8c-41cd-4401-9eb6-d8d318 │ TEZ         │ h │ defa │ R │ UNDEFI │ 0% │ http://WN31-SEPLAD.fazenda.net:4153 │
│ application_1749125299497 │ NFe_etl_PRD                         │ SPARK       │ a │ work │ R │ UNDEFI │ 10 │ http://WN31-SEPLAD.fazenda.net:3733 │
│ application_1749125299497 │ NFCe_etl_PRD                        │ SPARK       │ a │ work │ R │ UNDEFI │ 10 │ http://red04-seplad.fazenda.net:359 │
│ application_1740086204351 │ Thrift JDBC/ODBC Server             │ SPARK       │ h │ defa │ R │ UNDEFI │ 10 │ http://MN05-SEPLAD.fazenda.net:4040 │
└───────────────────────────┴─────────────────────────────────────┴─────────────┴───┴──────┴───┴────────┴────┴─────────────────────────────────────
```

```bash
sparkflint list pipelines     # Lista pipelines disponíveis na origin
```

```bash
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Nome           ┃ Responsável    ┃ ID                                   ┃ Criado em                  ┃ Atualizado em ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ PIPELINE_01    │ user_example1  │ 7f3231a6-5c35-466b-9114-5ce861c4fc3c │ 2025-05-27T17:05:51.533397 │ -             │
│ PIPELINE_02    │ user_example2  │ 64546d84-f5e3-41a3-8cba-e5ba6aa88f8f │ 2025-05-27T17:33:07.875804 │ -             │
│ PIPELINE_03    │ user_example3  │ 5b0f007b-225e-4952-88b2-956bb2e0f1ea │ 2025-05-27T17:34:07.606807 │ -             │
└────────────────┴────────────────┴──────────────────────────────────────┴────────────────────────────┴───────────────┘
```

```bash
sparkflint list dags     # Lista dags Airflow
```

```bash
# Nao implementado
```

### sparkflint run

Use `sparkflint run` para executar aplicações spark no ambiente remoto a partir de metadados da origin

```bash
sparkflint run [pipeline]   # Executa aplicação
```

```bash
# Não implementado
```

Options:

```bash
sparkflint run [pipeline] --tables [table1],[table2]
sparkflint run [pipeline] --queue [queue]
sparkflint run [pipeline] --name [app-name]
```

### sparkflint logs

Use `sparkflint logs` para mostrar o log de uma aplicação Spark

```bash
sparkflint logs [app-id] # Exibe log de uma aplicação Spark
```

### sparkflint origin

Use `sparkflint origin` para configurar e acessar a origem de metadados

```bash
sparkflint origin set [https-link] # Altera o endereço https da origin
```

```bash
sparkflint origin view [https-link] # Acessa a origin no navegador
```

## Licença de Uso

## Contribuicao

## Contribuidores

## Autocomplete (Zsh ou Bash)

Para ativar o autocompletar dos comandos, adicione ao seu shell:

### Zsh

```bash
echo 'source <(sparkflint --show-completion zsh)' >> ~/.zshrc
```

### Bash

```bash
echo 'source <(sparkflint --show-completion bash)' >> ~/.bashrc
```

Depois reinicie o terminal.
