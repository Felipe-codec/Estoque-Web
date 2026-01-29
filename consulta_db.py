import psycopg2

conexao = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="suasenha"
)

cursor = conexao.cursor()




def listar_produtos():
    cursor.execute("SELECT * FROM produto")
    consulta = cursor.fetchall()
    print("----- Lista de Produtos -----")
    for produto in consulta:
        print(f"ID: {produto[0]}, Nome: {produto[1]}, Preço: {produto[2]}, Tipo: {produto[3]}")
    print("-----------------------------")

def adicionar_produto():
    nome = input("Digite o nome do produto: ")
    preco = float(input("Digite o preço do produto: "))
    tipo = input("Digite o tipo do produto: ")

    cursor.execute("INSERT INTO produto (nome_produto, preco, tipo) VALUES (%s, %s, %s)", (nome, preco, tipo))
    conexao.commit()
    print("Produto adicionado com sucesso!")

def excluir_produto():
    cursor.execute("SELECT * FROM produto")
    consulta = cursor.fetchall()
    print("----- Lista de Produtos -----")
    for produto in consulta:
        print(f"ID: {produto[0]}, Nome: {produto[1]}, Preço: {produto[2]}, Tipo: {produto[3]}")
    print("-----------------------------")
    produto_id = int(input("Digite o ID do produto que deseja excluir: "))
    cursor.execute("DELETE FROM produto WHERE id = %s", (produto_id,))
    conexao.commit()
    print("Produto excluído com sucesso!")

def editar_produto():
    cursor.execute("SELECT * FROM produto")
    consulta = cursor.fetchall()
    print("----- Lista de Produtos -----")
    for produto in consulta:
        print(f"ID: {produto[0]}, Nome: {produto[1]}, Preço: {produto[2]}, Tipo: {produto[3]}")
    print("-----------------------------")
    produto_id = int(input("Digite o ID do produto que deseja editar: "))
    novo_nome = input("Digite o novo nome do produto: ")
    novo_preco = float(input("Digite o novo preço do produto: "))
    novo_tipo = input("Digite o novo tipo do produto: ")

    cursor.execute(
        "UPDATE produto SET nome_produto = %s, preco = %s, tipo = %s WHERE id = %s",
        (novo_nome, novo_preco, novo_tipo, produto_id)
    )
    conexao.commit()
    print("Produto editado com sucesso!")

def menu():
    print("----- Menu de Produtos -----")
    print("1 - Listar Produtos")
    print("2 - Adicionar Produto")
    print("3 - Editar Produto")
    print("4 - Excluir Produto")
    print("0 - Sair")
    print("----------------------------")

    decisao = input("Escolha uma opção: ")
    if decisao == "1":
        listar_produtos()
        menu()
    elif decisao == "2":
        adicionar_produto()
        menu()
    elif decisao == "3":
        editar_produto()
        menu()
    elif decisao == "4":
        excluir_produto()
        menu()
    elif decisao == "0":
        print("Saindo...")
        cursor.close()
        conexao.close()

menu()

