import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc

# Configuração do customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Conexão com o banco de dados
conexao = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=(local)\\SQLEXPRESS;'
    'DATABASE=ControleGastos;'
    'Trusted_Connection=yes;'
)
cursor = conexao.cursor()


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
        cursor.execute(
            "SELECT id FROM categorias WHERE nome = ?", (categoria,))
        resultado = cursor.fetchone()

        if resultado:
            categoria_id = resultado[0]
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


def atualizar_saldo():
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Receita'")
    receitas = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Despesa'")
    despesas = cursor.fetchone()[0] or 0

    saldo = receitas - despesas
    label_saldo.configure(text=f"Saldo Total: R$ {saldo:.2f}")


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


janela = ctk.CTk()
janela.title("Controle de Gastos")
janela.geometry("620x580")

# Campos de entrada
ctk.CTkLabel(janela, text="Descrição:").grid(
    row=0, column=0, padx=10, pady=5, sticky="e")
entrada_descricao = ctk.CTkEntry(janela, width=300)
entrada_descricao.grid(row=0, column=1, pady=5)

ctk.CTkLabel(janela, text="Valor:").grid(
    row=1, column=0, padx=10, pady=5, sticky="e")
entrada_valor = ctk.CTkEntry(janela, width=300)
entrada_valor.grid(row=1, column=1, pady=5)

ctk.CTkLabel(janela, text="Data (YYYY-MM-DD):").grid(row=2,
                                                     column=0, padx=10, pady=5, sticky="e")
entrada_data = ctk.CTkEntry(janela, width=300)
entrada_data.grid(row=2, column=1, pady=5)

ctk.CTkLabel(janela, text="Tipo:").grid(
    row=3, column=0, padx=10, pady=5, sticky="e")
tipo_var = ctk.StringVar(value="Receita")
dropdown_tipo = ctk.CTkComboBox(
    janela, variable=tipo_var, values=["Receita", "Despesa"])
dropdown_tipo.grid(row=3, column=1, pady=5)

cursor.execute("SELECT nome FROM categorias")
lista_categorias = [linha[0] for linha in cursor.fetchall()]

ctk.CTkLabel(janela, text="Categoria:").grid(
    row=4, column=0, padx=10, pady=5, sticky="e")
categoria_var = ctk.StringVar(
    value=lista_categorias[0] if lista_categorias else "")
dropdown_categoria = ctk.CTkComboBox(
    janela, variable=categoria_var, values=lista_categorias)
dropdown_categoria.grid(row=4, column=1, pady=5)

btn_adicionar = ctk.CTkButton(
    janela, text="Adicionar Transação", command=adicionar_transacao)
btn_adicionar.grid(row=5, column=0, columnspan=2, pady=10)

# Treeview
colunas = ("ID", "Descrição", "Valor", "Data", "Tipo", "Categoria")
tree = ttk.Treeview(janela, columns=colunas, show="headings", height=10)
for coluna in colunas:
    tree.heading(coluna, text=coluna)
    tree.column(coluna, width=100)
tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Saldo
label_saldo = ctk.CTkLabel(
    janela, text="Saldo Total: R$ 0.00", font=ctk.CTkFont(size=14, weight="bold"))
label_saldo.grid(row=7, column=0, columnspan=2, pady=10)

# Botão de excluir
btn_excluir = ctk.CTkButton(
    janela, text="Excluir Transação", command=excluir_transacao, fg_color="red")
btn_excluir.grid(row=8, column=0, columnspan=2, pady=10)

exibir_transacoes()
janela.mainloop()
