import flet as ft
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


# Carregar variáveis do arquivo .env
load_dotenv()

# URL da API desde variáveis de ambiente
API_URL = os.getenv("API_URL", "http://localhost:8000/produtos") # fallback local

class ProdutoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Gestão de Estoque"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 900
        self.page.window.height = 1000
        
        self.produtos = []
        self.editando_id = None
        
        # Componentes
        self.titulo = ft.Text("📦 Estoque", size=32, weight="bold")
        self.status = ft.Text("Pronto", size=14, color="green")
        
        # Formulário
        self.input_nome = ft.TextField(label="Nome do Produto", width=400)
        self.input_preco = ft.TextField(label="Preço (R$)", width=400)
        self.input_tipo = ft.TextField(label="Tipo/Categoria", width=400)
        
        # Lista de produtos
        self.lista_view = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        
        # Dialog do formulário - será criada dinamicamente
        self.criar_bottomsheet()
        
        # Botões principais
        self.btn_novo = ft.Button(
            "➕ Novo",
            on_click=self.abrir_novo
        )
        self.btn_atualizar = ft.Button(
            "🔄 Atualizar",
            on_click=self.carregar_produtos
        )
        
        # Layout
        self.page.add(
            self.titulo,
            self.status,
            ft.Row([self.btn_novo, self.btn_atualizar], spacing=20),
            ft.Divider(),
            self.lista_view
        )
        
        # Carregar dados iniciais
        self.carregar_produtos()
    def criar_bottomsheet(self):
        self.bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Text("Produto", size=20, weight="bold"),
                    self.input_nome,
                    self.input_preco,
                    self.input_tipo,
                    ft.Row([
                        ft.Button("Salvar", on_click=self.salvar_produto),
                        ft.Button("Cancelar", on_click=self.fechar_dialog)
                    ], spacing=10)
                ], spacing=15),
                padding=20
            )
        )
        self.page.overlay.append(self.bs)
    
    def carregar_produtos(self, e=None):
        print(">>> Buscando produtos...")
        self.status.value = "Carregando..."
        self.status.color = "orange"
        self.lista_view.controls.clear()
        self.page.update()
        
        try:
            resp = requests.get(API_URL, timeout=5)
            print(f">>> Status: {resp.status_code}")
            
            if resp.status_code == 200:
                self.produtos = resp.json()
                print(f">>> Encontrados: {len(self.produtos)} produtos")
                self.status.value = f"✓ {len(self.produtos)} produtos"
                self.status.color = "green"
                self.renderizar_produtos()
            else:
                self.status.value = f"Erro {resp.status_code}"
                self.status.color = "red"
        except Exception as e:
            print(f">>> ERRO: {e}")
            self.status.value = f"Erro: {str(e)}"
            self.status.color = "red"
        
        self.page.update()
    
    def renderizar_produtos(self):
        for p in self.produtos:
            pid = p['id']
            
            btn_edit = ft.Button(
                "✏️ Editar",
                on_click=lambda e, product_id=pid: self.abrir_edicao(product_id)
            )
            btn_del = ft.Button(
                "🗑️ Deletar",
                on_click=lambda e, product_id=pid: self.deletar(product_id)
            )
            
            item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(p['nome'], size=16, weight="bold"),
                            ft.Text(f"Tipo: {p['tipo']}", size=12, color="gray"),
                            ft.Text(f"R$ {p['preco']:.2f}", size=14, weight="bold", color="green")
                        ], expand=True),
                        ft.Row([btn_edit, btn_del], spacing=5)
                    ])
                ]),
                padding=15,
                margin=ft.Margin(bottom=5, left=0, right=0, top=0),
                bgcolor="#f5f5f5",
                border_radius=8,
                border=ft.Border(bottom=ft.BorderSide(1, "lightgray"), top=ft.BorderSide(1, "lightgray"), 
                                 left=ft.BorderSide(1, "lightgray"), right=ft.BorderSide(1, "lightgray"))
            )
            self.lista_view.controls.append(item)
    
    def abrir_novo(self, e):
        print(">>> Abrindo novo produto")
        self.editando_id = None
        self.input_nome.value = ""
        self.input_preco.value = ""
        self.input_tipo.value = ""
        self.bs.open = True
        self.page.update()
    
    def abrir_edicao(self, produto_id):
        print(f">>> Abrindo edição de {produto_id}")
        produto = next((p for p in self.produtos if p['id'] == produto_id), None)
        if not produto:
            print(">>> Produto não encontrado!")
            return
        
        self.editando_id = produto_id
        self.input_nome.value = produto['nome']
        self.input_preco.value = str(produto['preco'])
        self.input_tipo.value = produto['tipo']
        self.bs.open = True
        self.page.update()
        print(">>> BottomSheet aberta")
    
    def fechar_dialog(self, e=None):
        self.bs.open = False
        self.page.update()
    
    def salvar_produto(self, e):
        if not self.input_nome.value or not self.input_preco.value or not self.input_tipo.value:
            self.status.value = "❌ Preencha todos os campos!"
            self.status.color = "red"
            self.page.update()
            return
        
        try:
            dados = {
                "nome_produto": self.input_nome.value,
                "preco": float(self.input_preco.value),
                "tipo": self.input_tipo.value
            }
            
            if self.editando_id:
                # UPDATE
                resp = requests.put(f"{API_URL}/{self.editando_id}", json=dados, timeout=5)
                msg = "Atualizado!"
            else:
                # CREATE
                resp = requests.post(API_URL, json=dados, timeout=5)
                msg = "Adicionado!"
            
            if resp.status_code in [200, 201]:
                self.status.value = f"✓ {msg}"
                self.status.color = "green"
                self.fechar_dialog()
                self.carregar_produtos()
            else:
                self.status.value = f"❌ Erro {resp.status_code}"
                self.status.color = "red"
        except Exception as e:
            self.status.value = f"❌ {str(e)}"
            self.status.color = "red"
        
        self.page.update()
    
    def deletar(self, produto_id):
        print(f">>> Deletando produto {produto_id}")
        try:
            resp = requests.delete(f"{API_URL}/{produto_id}", timeout=5)
            
            if resp.status_code == 200:
                self.status.value = "✓ Deletado!"
                self.status.color = "green"
                self.carregar_produtos()
            else:
                self.status.value = f"❌ Erro {resp.status_code}"
                self.status.color = "red"
        except Exception as e:
            self.status.value = f"❌ {str(e)}"
            self.status.color = "red"
            print(f">>> ERRO ao deletar: {e}")
        
        self.page.update()

def main(page: ft.Page):
    app = ProdutoApp(page)

if __name__ == "__main__":
    ft.run(main)
