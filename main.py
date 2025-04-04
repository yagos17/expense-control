import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Conexão com o banco de dados
conexao = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=(local)\\SQLEXPRESS;'
    'DATABASE=ControleGastos;'
    'Trusted_Connection=yes;'
)
cursor = conexao.cursor()

# Função para adicionar uma nova transação


def adicionar_transacao():
    descricao = entrada_descricao.get()
    valor = entrada_valor.get()
    data = entrada_data.get()
    tipo = tipo_var.get()
    categoria = categoria_var.get()

    if not (descricao and valor and data and tipo and categoria):
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    try:
        valor = float(valor)

        # Busca o ID da categoria
        cursor.execute(
            "SELECT id FROM categorias WHERE nome = ?", (categoria,))
        resultado = cursor.fetchone()

        if resultado:
            categoria_id = resultado[0]

            # Insere a transação no banco
            cursor.execute(
                "INSERT INTO transacoes (descricao, valor, data_transacao, tipo, categoria_id) VALUES (?, ?, ?, ?, ?)",
                (descricao, valor, data, tipo, categoria_id)
            )
            conexao.commit()
            messagebox.showinfo("Sucesso", "Transação adicionada!")
            exibir_transacoes()
        else:
            messagebox.showerror("Erro", "Categoria não encontrada.")

    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao adicionar: {erro}")

# Função para exibir todas as transações


def exibir_transacoes():
    tree.delete(*tree.get_children())

    cursor.execute("""
        SELECT t.id, t.descricao, t.valor, t.data_transacao, t.tipo, c.nome
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        ORDER BY t.data_transacao DESC
    """)
    for id, desc, val, data, tipo, cat in cursor.fetchall():
        tree.insert("", "end", values=(
            id, desc, f"R$ {val:.2f}", data, tipo, cat))

    atualizar_saldo()

# Função para atualizar o saldo total


def atualizar_saldo():
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Receita'")
    receitas = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Despesa'")
    despesas = cursor.fetchone()[0] or 0

    saldo = receitas - despesas
    label_saldo.config(text=f"Saldo Total: R$ {saldo:.2f}")

# Função para excluir a transação selecionada


def excluir_transacao():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning(
            "Aviso", "Selecione uma transação para excluir.")
        return

    transacao_id = tree.item(selecionado[0], "values")[0]

    try:
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Transação excluída.")
        exibir_transacoes()
    except Exception as erro:
        messagebox.showerror("Erro", f"Erro ao excluir: {erro}")

# ==== Interface Gráfica ====


# Janela principal
janela = tk.Tk()
janela.title("Controle de Gastos")

# Campos de entrada
tk.Label(janela, text="Descrição:").grid(row=0, column=0)
entrada_descricao = tk.Entry(janela, width=30)
entrada_descricao.grid(row=0, column=1)

tk.Label(janela, text="Valor:").grid(row=1, column=0)
entrada_valor = tk.Entry(janela, width=30)
entrada_valor.grid(row=1, column=1)

tk.Label(janela, text="Data (YYYY-MM-DD):").grid(row=2, column=0)
entrada_data = tk.Entry(janela, width=30)
entrada_data.grid(row=2, column=1)

tk.Label(janela, text="Tipo:").grid(row=3, column=0)
tipo_var = tk.StringVar()
dropdown_tipo = ttk.Combobox(
    janela, textvariable=tipo_var, values=["Receita", "Despesa"])
dropdown_tipo.grid(row=3, column=1)
dropdown_tipo.current(0)

# Carrega categorias do banco
cursor.execute("SELECT nome FROM categorias")
lista_categorias = [linha[0] for linha in cursor.fetchall()]

tk.Label(janela, text="Categoria:").grid(row=4, column=0)
categoria_var = tk.StringVar()
dropdown_categoria = ttk.Combobox(
    janela, textvariable=categoria_var, values=lista_categorias)
dropdown_categoria.grid(row=4, column=1)
dropdown_categoria.current(0)

# Botão de adicionar
btn_adicionar = tk.Button(
    janela, text="Adicionar Transação", command=adicionar_transacao)
btn_adicionar.grid(row=5, column=0, columnspan=2, pady=10)

# Tabela (Treeview) para listar transações
colunas = ("ID", "Descrição", "Valor", "Data", "Tipo", "Categoria")
tree = ttk.Treeview(janela, columns=colunas, show="headings")
for coluna in colunas:
    tree.heading(coluna, text=coluna)
    tree.column(coluna, width=100)
tree.grid(row=6, column=0, columnspan=2, pady=10)

# Saldo
label_saldo = tk.Label(janela, text="Saldo Total: R$ 0.00",
                       font=("Arial", 12, "bold"))
label_saldo.grid(row=7, column=0, columnspan=2, pady=10)

# Botão de excluir
btn_excluir = tk.Button(janela, text="Excluir Transação",
                        command=excluir_transacao, bg="red", fg="white")
btn_excluir.grid(row=8, column=0, columnspan=2, pady=10)

# Inicializa a interface com os dados
exibir_transacoes()

# Executa a janela
janela.mainloop()
