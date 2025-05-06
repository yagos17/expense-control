CREATE TABLE categorias (
    id INT PRIMARY KEY IDENTITY(1,1),
    nome NVARCHAR(100) NOT NULL
);

CREATE TABLE transacoes (
    id INT PRIMARY KEY IDENTITY(1,1),
    descricao NVARCHAR(255) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_transacao DATE NOT NULL,
    tipo NVARCHAR(20) NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
    categoria_id INT NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);