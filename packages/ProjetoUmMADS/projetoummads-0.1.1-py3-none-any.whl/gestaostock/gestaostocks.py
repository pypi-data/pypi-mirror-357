armas = []


import matplotlib.pyplot as plt

class Armazem:

    def __init__(self, nome, capacidade, Lat, Lon):
        # Verifica se já existe um armazém com o mesmo nome
        for armazem in armas:
            if armazem.nome == nome:
                print(f"❌ Erro: já existe um armazém com o nome '{nome}'.")
                return  # Interrompe a criação

        self.nome = nome
        self.capacidade = capacidade
        self.Lat = Lat
        self.Lon = Lon
        self.stock = {}
        self.logs = []
        self.historico_margens = {}
        armas.append(self)
        print(f"✅ Sucesso: Armazém criando [ '{nome}' ].")

    def adicionar_mercadoria(self, nome, quantidade, preco, peso):
        if quantidade < 0 or preco < 0 or peso < 0:
            print("❌ Erro: Introduza apenas valores positivos!")
            return
        if sum(produto["quantidade"] for produto in self.stock.values()) + quantidade > self.capacidade:
            print("❌ Erro: Capacidade excedida!")
            return

        if nome in self.stock:
            stock_antigo = self.stock[nome]
            qtd_antiga = stock_antigo["quantidade"]
            preco_antigo = stock_antigo["preço"]

            # Calcular média ponderada
            novo_preco_medio = ((qtd_antiga * preco_antigo) + (quantidade * preco)) / (qtd_antiga + quantidade)

            self.stock[nome]["quantidade"] += quantidade
            self.stock[nome]["preço"] = novo_preco_medio
        else:
            self.stock[nome] = {"quantidade": quantidade, "preço": preco, "peso": peso}

        print(f"📦 {quantidade} unidades de {nome} adicionadas ao {self.nome}.")

    def remover_mercadoria(self, nome, quantidade):
        if nome in self.stock and self.stock[nome]["quantidade"] >= quantidade:
            self.stock[nome]["quantidade"] -= quantidade
            if self.stock[nome]["quantidade"] == 0:
                del self.stock[nome]
            print(f"🗑️ {quantidade} unidades de {nome} removidas do {self.nome}.")
        else:
            print("❌ Erro: Quantidade insuficiente ou produto inexistente.")

    def transferir_mercadoria(self, destino, nome, quantidade):
        if nome in self.stock and self.stock[nome]["quantidade"] >= quantidade:
            destino.adicionar_mercadoria(nome, quantidade, self.stock[nome]["preço"], self.stock[nome]["peso"])
            self.remover_mercadoria(nome, quantidade)
        else:
            print("❌ Erro: Transferência inválida.")

    def listar_armazens():
        if not armas:
            print("❌ Não existem armazéns registados.")
            return

        for armazem in armas:
            print(f"\n📦 Armazém: {armazem.nome} (Capacidade: {armazem.capacidade})")
            if not armazem.stock:
                print("  - 🏷️ Sem mercadoria.")
            else:
                for produto, detalhes in armazem.stock.items():
                    print(f"  - {produto}: {detalhes['quantidade']} unidades | Preço: {detalhes['preço']}€ | Peso: {detalhes['peso']}kg")

    def verificar_capacidade(self):
        total = sum(produto["quantidade"] for produto in self.stock.values())
        if total == self.capacidade:
            print(f"⚠️ Aviso: O armazém '{self.nome}' atingiu a sua capacidade máxima.")
            self.logs.append("Capacidade máxima atingida.")
        elif total > self.capacidade:
            print(f"⚠️ Aviso: O armazém '{self.nome}' ultrapassou a capacidade!")
            self.logs.append("Capacidade ultrapassada.")
        elif total >= self.capacidade * 0.9:
            print(f"⚠️ Aviso: O armazém '{self.nome}' está a 90% da capacidade.")
            self.logs.append("Capacidade a 90%.")

    def mostrar_logs(self):
        print(f"--- 📜 LOGS DO ARMAZÉM '{self.nome}' ---")
        for log in self.logs:
            print(log)

    def custo_medio_produto(self, nome):
        if nome in self.stock:
            preco = self.stock[nome]["preço"]
            print(f"💰 Custo médio de '{nome}' no armazém '{self.nome}': {preco:.2f}€")
            return preco
        else:
            print(f"❌ Produto '{nome}' não encontrado no armazém '{self.nome}'.")
            return None

    def valor_medio_venda_produto(self, nome):
        if nome in self.stock:
            # Calcular o preço médio de venda
            qtd = self.stock[nome]["quantidade"]
            preco_venda = self.stock[nome]["preço"]

            # Valor médio de venda = preço médio * quantidade total
            valor_medio_venda = preco_venda * qtd

            print(f"💰 Valor médio de venda de '{nome}' no armazém '{self.nome}': {valor_medio_venda:.2f}€")
            return valor_medio_venda
        else:
            print(f"❌ Produto '{nome}' não encontrado no armazém '{self.nome}'.")
            return None

    def listar_produtos_maior_margem(self):
        produtos_com_margem = []

        for nome, info in self.stock.items():
            preco_custo = info["preço"]
            quantidade = info["quantidade"]

            if "preço_venda" in info:
                preco_venda = info["preço_venda"]
                margem = ((preco_venda - preco_custo) / preco_venda) * 100
                produtos_com_margem.append((nome, margem, quantidade))

                # Guardar histórico
                if nome not in self.historico_margens:
                    self.historico_margens[nome] = []
                self.historico_margens[nome].append(margem)

        produtos_com_margem.sort(key=lambda x: x[1], reverse=True)

        print(f"📊 --- Produtos com maior margem de lucro no armazém '{self.nome}' ---")
        for nome, margem, quantidade in produtos_com_margem:
            print(f"📈 Produto: {nome} | Margem: {margem:.2f}% | Quantidade: {quantidade}")

    def alerta_quase_cheio(self):
        total = sum(produto["quantidade"] for produto in self.stock.values())
        if total >= self.capacidade * 0.9:
            print(f"⚠️ Aviso: O armazém '{self.nome}' está a 90% da sua capacidade!")

    def alerta_quase_vazio(self):
        total = sum(produto["quantidade"] for produto in self.stock.values())
        if total <= self.capacidade * 0.1:
            print(f"⚠️ Aviso: O armazém '{self.nome}' está quase vazio (menos de 10% da capacidade).")

    def grafico_evolucao_margens(self):
        if not self.historico_margens:
            print("📉 Ainda não há histórico de margens.")
            return

        plt.figure(figsize=(10, 5))

        for produto, margens in self.historico_margens.items():
            plt.plot(margens, label=produto)

        plt.title(f"📈 Evolução da Margem por Produto - Armazém {self.nome}")
        plt.xlabel("Registos")
        plt.ylabel("Margem (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def listar_armazens_mais_lucrativos():
        if not armas:
            print("❌ Não existem armazéns registados.")
            return

        lucros = []

        armazens_filtrados = [armazem for armazem in armas if not armazem.nome.startswith("Armazém")]

        for armazem in armazens_filtrados:
            total_lucro = 0
            for produto, info in armazem.stock.items():
                if "preço_venda" in info:
                    preco_custo = info["preço"]
                    preco_venda = info["preço_venda"]
                    quantidade = info["quantidade"]
                    lucro = (preco_venda - preco_custo) * quantidade
                    total_lucro += lucro
            lucros.append((armazem.nome, total_lucro))

        lucros.sort(key=lambda x: x[1], reverse=True)

        print("\n💰 Armazéns mais lucrativos:")
        for nome, lucro in lucros:
            print(f"💵 - {nome}: {lucro:.2f}€ de lucro estimado")