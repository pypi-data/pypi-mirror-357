class GestaoAluguerAutomoveis:
    def __init__(self):
        # Dicionário para guardar os alugueres
        self.alugueres = {}

    def adicionar_aluguer(self, id_aluguer, cliente, automovel, data_inicio, data_fim, valor):

        if id_aluguer in self.alugueres:
            print(f"Erro: Aluguer com ID {id_aluguer} já existe.")
            return

        self.alugueres[id_aluguer] = {
            'cliente': cliente,
            'automovel': automovel,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'valor': valor
        }
        print(f"Aluguer {id_aluguer} adicionado com sucesso.")

    def modificar_aluguer(self, id_aluguer, **kwargs):

        if id_aluguer not in self.alugueres:
            print(f"Erro: Aluguel com ID {id_aluguer} não encontrado.")
            return

        for key, value in kwargs.items():
            if key in self.alugueres[id_aluguer]:
                self.alugueres[id_aluguer][key] = value
                print(f"Campo '{key}' do aluguer {id_aluguer} atualizado para '{value}'.")
            else:
                print(f"Erro: Campo '{key}' não existe no aluguer {id_aluguer}.")

    def visualizar_alugueres(self):

        print("Resumo dos Alugueres:")
        for id_aluguer, info in self.alugueres.items():
            print(f"Cliente: {info['cliente']}")
            print(f"ID Aluguer: {id_aluguer}")
            print(f"Automóvel: {info['automovel']}")
            print(f"Data Início: {info['data_inicio']}")
            print(f"Data Fim: {info['data_fim']}")
            print(f"Valor: {info['valor']}")
            print("-" * 30)

# from gestao_aluguer import GestaoAluguerAutomoveis

# gestor = GestaoAluguerAutomoveis()

# gestor.adicionar_aluguer( 1, 'N. Cartao de cidadão', 64, '12-12-2014', '12-1-2015', 1000)

# --------------------------------------------------------------------------------------------------------------

class GestorVeiculos:
    def __init__(self):
        self.veiculos = {}

    # Adicionar novo veículo ao sistema
    def adicionar_veiculo(self, matricula, marca, modelo, data, combustivel, quilometros):
        if matricula in self.veiculos:
            print(f"Erro: O veículo com a matrícula {matricula} já existe no sistema.")
            return
        
        self.veiculos[matricula] = {
            "Marca": marca,
            "Modelo": modelo,
            "Data": data,
            "Combustível": combustivel,
            "Quilómetros": quilometros
        }
        print(f"Veículo com matrícula {matricula} adicionado com sucesso!")
    
    # Atualizar dados do veículo
    def atualizar_veiculo(self, matricula, nova_matricula=None, marca=None, modelo=None, data=None, combustivel=None, quilometros=None):
        if matricula not in self.veiculos:
            print(f"Erro: O veículo com a matrícula {matricula} não existe no sistema.")
            return
        
        veiculo = self.veiculos.pop(matricula)
        
        if nova_matricula:
            if nova_matricula in self.veiculos:
                print(f"Erro: A nova matrícula {nova_matricula} já existe no sistema.")
                self.veiculos[matricula] = veiculo  # Reverter a remoção
                return
            matricula = nova_matricula
        
        if marca:
            veiculo["Marca"] = marca
        if marca:
            veiculo["Modelo"] = modelo
        if data:
            veiculo["Data"] = data
        if combustivel:
            veiculo["Combustível"] = combustivel
        if quilometros is not None:
            veiculo["Quilómetros"] = quilometros
        
        self.veiculos[matricula] = veiculo
        print(f"Veículo atualizado com sucesso!")

    # Listar todos os veículos no sistema
    def listar_veiculos(self):
        if not self.veiculos:
            print("Nenhum veículo cadastrado.")
        else:
            print("+------------+--------------+--------------+------+-------------+-------------+")
            print("| Matrícula  | Marca        | Modelo       | Data | Combustível | Quilómetros |")
            print("+------------+--------------+--------------+------+-------------+-------------+")
            for matricula, dados in self.veiculos.items():
                print(f"| {matricula:<10} | {dados['Marca']:<12} | {dados['Modelo']:<12} | {dados['Data']:<4} | {dados['Combustível']:<11} | {dados['Quilómetros']:<11} |")
            print("+------------+--------------+--------------+------+-------------+-------------+")

# Exemplo de uso
# gestor = GestorVeiculos()
# gestor.adicionar_veiculo("AB-12-CD", "Toyota", "Corolla", "2020", "Diesel", 50000)
# gestor.adicionar_veiculo("AB-55-CD", "Honda", "Civic", "2018", "Gasolina", 60000)
# gestor.adicionar_veiculo("AB-12-CD", "Honda", "Civic", "2018", "Gasolina", 60000)  # Deve exibir erro
# gestor.atualizar_veiculo("AB-12-CD", nova_matricula="XY-98-ZT", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=75000)
# gestor.listar_veiculos()

# --------------------------------------------------------------------------------------------------------------

class GestorClientes:
    def __init__(self):
        self.clientes = {}

    # Adicionar novo cliente ao sistema
    def adicionar_cliente(self, nif, nome, data_nascimento):
        if nif in self.clientes:
            print(f"Erro: O cliente com o NIF: {nif} já existe no sistema.")
            return
        
        self.clientes[nif] = {
            "Nome": nome,
            "Data de Nascimento": data_nascimento
        }
        print(f"Cliente com NIF: {nif} adicionado com sucesso!")

    # Atualizar dados do cliente
    def atualizar_cliente(self, nif, novo_nif=None, nome=None, data_nascimento=None):
        if nif not in self.clientes:
            print(f"Erro: O cliente com o NIF {nif} não existe no sistema.")
            return
        
        cliente = self.clientes.pop(nif)
        
        if novo_nif:
            if novo_nif in self.clientes:
                print(f"Erro: O novo NIF {novo_nif} já existe no sistema.")
                self.clientes[nif] = cliente  # Reverter a remoção
                return
            nif = novo_nif
        
        if nome:
            cliente["Nome"] = nome
        if data_nascimento:
            cliente["Data de Nascimento"] = data_nascimento
        
        self.clientes[nif] = cliente
        print(f"Cliente atualizado com sucesso!")

    # Listar todos os clientes no sistema
    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
        else:
            print("+------------+----------------------+------------------+")
            print("| NIF        | Nome                 | Data de Nasc.    |")
            print("+------------+----------------------+------------------+")
            for nif, dados in self.clientes.items():
                print(f"| {nif:<10} | {dados['Nome']:<20} | {dados['Data de Nascimento']:<16} |")
            print("+------------+----------------------+------------------+")

# Exemplo de uso
# gestor = GestorClientes()
# gestor.adicionar_cliente("123456789", "João Silva", "15-05-1995")
# gestor.adicionar_cliente("999999999", "Maria Oliveira", "20-10-1985")
# gestor.adicionar_cliente("123456789", "Maria Oliveira", "20-10-1985")
# gestor.atualizar_cliente("123456789", novo_nif="987654321", nome="João Pedro", data_nascimento="20-06-1991")
# gestor.listar_clientes()
