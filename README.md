# Controle de Gastos

Uma aplicação de controle financeiro pessoal feita com Python, CustomTkinter para a interface gráfica e SQL Server para armazenamento dos dados.

## 💻 Tecnologias Utilizadas

- Python 3.x
- CustomTkinter
- pyodbc
- SQL Server

## 🛠️ Funcionalidades

- Adicionar receitas e despesas
- Selecionar categorias e tipos
- Listar transações em uma tabela
- Calcular e exibir o saldo atual
- Excluir transações
- Interface amigável com CustomTkinter

## 🗃️ Configuração do Banco de Dados

1. Crie um banco no SQL Server com o nome **ControleGastos**
2. Execute os scripts na pasta `database/`:
   - `create_tables.sql`: cria as tabelas
   - `insert_data.sql`: adiciona categorias iniciais

> 💡 Use SQL Server Express localmente ou edite a string de conexão no `main.py`.

```python
conexao = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=(local)\\SQLEXPRESS;'
    'DATABASE=ControleGastos;'
    'Trusted_Connection=yes;'
)
