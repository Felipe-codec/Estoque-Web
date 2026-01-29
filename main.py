from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI()
# ... logo abaixo de app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que qualquer origem (como seu site Docker) acesse a API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Modelo de dados para o Produto
class Produto(BaseModel):
    nome_produto: str
    preco: float
    tipo: str

# Função auxiliar para conectar ao banco
def get_db_connection():
    # Tenta pegar a URL completa do banco (padrão de nuvem como Render/Neon)
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Se existir a variável DATABASE_URL, conecta por ela
        return psycopg2.connect(database_url)
    else:
        # Fallback: Se não existir (estou no PC local), usa as variáveis individuais
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "suasenha")
        )

# --- ENDPOINTS ---

@app.get("/produtos")
def listar_produtos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome_produto, preco, tipo FROM produto ORDER BY id")
    consulta = cur.fetchall()
    cur.close()
    conn.close()
    
    # Transforma a tupla em uma lista de dicionários (formato JSON)
    return [{"id": produto[0], "nome": produto[1], "preco": produto[2], "tipo": produto[3]} for produto in consulta]

@app.post("/produtos", status_code=201)
def adicionar_produto(produto: Produto):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO produto (nome_produto, preco, tipo) VALUES (%s, %s, %s) RETURNING id",
            (produto.nome_produto, produto.preco, produto.tipo)
        )
        novo_id = cur.fetchone()[0]
        conn.commit()
        return {"mensagem": "Produto adicionado!", "id": novo_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.put("/produtos/{produto_id}")
def editar_produto(produto_id: int, produto: Produto):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE produto SET nome_produto = %s, preco = %s, tipo = %s WHERE id = %s",
        (produto.nome_produto, produto.preco, produto.tipo, produto_id)
    )
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    conn.commit()
    cur.close()
    conn.close()
    return {"mensagem": "Produto editado com sucesso!"}

@app.delete("/produtos/{produto_id}")
def excluir_produto(produto_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM produto WHERE id = %s", (produto_id,))
    
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    conn.commit()
    cur.close()
    conn.close()
    return {"mensagem": "Produto excluído!"}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 significa ouvir em todas as interfaces (localhost + IP da rede)
    uvicorn.run(app, host="0.0.0.0", port=8000)