from datetime import datetime
from collections import defaultdict

class GestorVeiculos:
    def __init__(self):
        self.veiculos = {}

    def adicionar_veiculo(self, matricula, marca, modelo, data, combustivel, quilometros, preco_dia): 
        # Validação de ano
        try:
            ano = int(data)
            ano_atual = datetime.now().year
            if ano < 1920 or ano > ano_atual:
                print(f"Erro: O ano do veículo ({ano}) deve estar entre 1920 e {ano_atual}.")
                return
        except ValueError:
            print("Erro: O ano do veículo deve ser um número inteiro.")
            return

        if matricula in self.veiculos:
            print(f"Erro: O veículo com a matrícula {matricula} já existe no sistema.")
            return

        self.veiculos[matricula] = {
            "Marca": marca,
            "Modelo": modelo,
            "Data": ano,
            "Combustível": combustivel,
            "Quilómetros": quilometros,
            "Preço/Dia": preco_dia
        }
        print(f"Veículo com matrícula {matricula} adicionado com sucesso!")

    def atualizar_veiculo(self, matricula, nova_matricula=None, marca=None, modelo=None, data=None, combustivel=None, quilometros=None, preco_dia=None):
        if matricula not in self.veiculos:
            print(f"Erro: O veículo com a matrícula {matricula} não existe no sistema.")
            return

        veiculo = self.veiculos.pop(matricula)

        if nova_matricula:
            if nova_matricula in self.veiculos:
                print(f"Erro: A nova matrícula {nova_matricula} já existe no sistema.")
                self.veiculos[matricula] = veiculo
                return
            matricula = nova_matricula

        if data:
            try:
                ano = int(data)
                ano_atual = datetime.now().year
                if ano < 1920 or ano > ano_atual:
                    print(f"Erro: O ano do veículo ({ano}) deve estar entre 1920 e {ano_atual}.")
                    self.veiculos[matricula] = veiculo
                    return
                veiculo["Data"] = ano
            except ValueError:
                print("Erro: O ano do veículo deve ser um número inteiro.")
                self.veiculos[matricula] = veiculo
                return

        if marca:
            veiculo["Marca"] = marca
        if modelo:
            veiculo["Modelo"] = modelo
        if combustivel:
            veiculo["Combustível"] = combustivel
        if quilometros is not None:
            veiculo["Quilómetros"] = quilometros
        if preco_dia is not None:
            veiculo["Preço/Dia"] = preco_dia

        self.veiculos[matricula] = veiculo
        print(f"Veículo atualizado com sucesso!")

    def listar_veiculos(self):
        if not self.veiculos:
            print("Nenhum veículo cadastrado.")
        else:
            print(f"\nLISTA DE VEÍCULOS")
            print("+------------+--------------+--------------+------+-------------+-------------+------------+")
            print("| Matrícula  | Marca        | Modelo       | Data | Combustível | Quilómetros | Preço/Dia  |")
            print("+------------+--------------+--------------+------+-------------+-------------+------------+")
            for matricula, dados in self.veiculos.items():
                print(f"| {matricula:<10} | {dados['Marca']:<12} | {dados['Modelo']:<12} | {dados['Data']:<4} | {dados['Combustível']:<11} | {dados['Quilómetros']:<11} | {dados['Preço/Dia']:<10.2f} |")
            print("+------------+--------------+--------------+------+-------------+-------------+------------+")
    
    def quilometragem_total(self):
        total = sum(veiculo["Quilómetros"] for veiculo in self.veiculos.values())
        print(f"\nDistância total percorrida pela frota: {total} km")
        return total

    def manutencao_preventiva(self, limite_km=100000):
        veiculos_para_manutencao = []

        for matricula, dados in self.veiculos.items():
            if dados["Quilómetros"] > limite_km:
                veiculos_para_manutencao.append((matricula, dados))

        if not veiculos_para_manutencao:
            print(f"\nNenhum veículo precisa de manutenção preventiva neste momento (limite: {limite_km} km).")
            return

        print(f"\nVEÍCULOS COM MAIS DE {limite_km} KM (SUGERIDO PARA MANUTENÇÃO PREVENTIVA)")
        print("+------------+--------------+--------------+---------------+")
        print("| Matrícula  | Marca        | Modelo       | Quilómetros   |")
        print("+------------+--------------+--------------+---------------+")
        for matricula, dados in veiculos_para_manutencao:
            print(f"| {matricula:<10} | {dados['Marca']:<12} | {dados['Modelo']:<12} | {dados['Quilómetros']:<13} |")
        print("+------------+--------------+--------------+---------------+")


class GestorClientes:
    def __init__(self):
        self.clientes = {}

    def adicionar_cliente(self, nif, nome, data_nascimento):
        if nif in self.clientes:
            print(f"Erro: O cliente com o NIF: {nif} já existe no sistema.")
            return
        
        self.clientes[nif] = {
            "Nome": nome,
            "Data de Nascimento": data_nascimento
        }
        print(f"Cliente com NIF: {nif} adicionado com sucesso!")

    def atualizar_cliente(self, nif, novo_nif=None, nome=None, data_nascimento=None):
        if nif not in self.clientes:
            print(f"Erro: O cliente com o NIF {nif} não existe no sistema.")
            return
        
        cliente = self.clientes.pop(nif)
        
        if novo_nif:
            if novo_nif in self.clientes:
                print(f"Erro: O novo NIF {novo_nif} já existe no sistema.")
                self.clientes[nif] = cliente
                return
            nif = novo_nif
        
        if nome:
            cliente["Nome"] = nome
        if data_nascimento:
            cliente["Data de Nascimento"] = data_nascimento
        
        self.clientes[nif] = cliente
        print(f"Cliente atualizado com sucesso!")

    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
        else:
            print(f"\nLISTA DE CLIENTES")
            print("+------------+----------------------+------------------+")
            print("| NIF        | Nome                 | Data de Nasc.    |")
            print("+------------+----------------------+------------------+")
            for nif, dados in self.clientes.items():
                print(f"| {nif:<10} | {dados['Nome']:<20} | {dados['Data de Nascimento']:<16} |")
            print("+------------+----------------------+------------------+")


class GestorAlugueres:
    def __init__(self):
        self.alugueres = []

    def adicionar_aluguer(self, nif_cliente, matricula_veiculo, data_inicio, data_fim, gestor_veiculos, gestor_clientes):
        if nif_cliente not in gestor_clientes.clientes:
            print(f"Erro: Cliente com NIF {nif_cliente} não existe.")
            return
        if matricula_veiculo not in gestor_veiculos.veiculos:
            print(f"Erro: Veículo com matrícula {matricula_veiculo} não existe.")
            return

        for aluguer in self.alugueres:
            if aluguer["Matrícula"] == matricula_veiculo:
                inicio_existente = datetime.strptime(aluguer["Início"], "%d-%m-%Y")
                fim_existente = datetime.strptime(aluguer["Fim"], "%d-%m-%Y")
                novo_inicio = datetime.strptime(data_inicio, "%d-%m-%Y")
                novo_fim = datetime.strptime(data_fim, "%d-%m-%Y")

                if (novo_inicio <= fim_existente and novo_fim >= inicio_existente):
                    print(f"Erro: Veículo {matricula_veiculo} já está alugado nesse intervalo.")
                    return

        inicio = datetime.strptime(data_inicio, "%d-%m-%Y")
        fim = datetime.strptime(data_fim, "%d-%m-%Y")
        dias = (fim - inicio).days + 1
        preco_dia = gestor_veiculos.veiculos[matricula_veiculo]["Preço/Dia"]
        total = dias * preco_dia

        self.alugueres.append({
            "NIF": nif_cliente,
            "Matrícula": matricula_veiculo,
            "Início": data_inicio,
            "Fim": data_fim,
            "Total": total
        })
        print(f"Aluguer registado: {nif_cliente} -> {matricula_veiculo} de {data_inicio} a {data_fim} | Total: {total:.2f}€")

    def listar_alugueres(self):
        if not self.alugueres:
            print("Nenhum aluguer registado.")
        else:
            print(f"\nLISTA DE ALUGUERES")
            print("+------------+------------+------------+------------+------------+")
            print("| NIF        | Matrícula  | Início     | Fim        | Total (€)  |")
            print("+------------+------------+------------+------------+------------+")
            for aluguer in self.alugueres:
                print(f"| {aluguer['NIF']:<10} | {aluguer['Matrícula']:<10} | {aluguer['Início']:<10} | {aluguer['Fim']:<10} | {aluguer['Total']:<10.2f} |")
            print("+------------+------------+------------+------------+------------+")

    def veiculos_disponiveis(self, data_inicio, data_fim, gestor_veiculos): 
        inicio = datetime.strptime(data_inicio, "%d-%m-%Y")
        fim = datetime.strptime(data_fim, "%d-%m-%Y")
        
        veiculos_ocupados = set()

        for aluguer in self.alugueres:
            aluguer_inicio = datetime.strptime(aluguer["Início"], "%d-%m-%Y")
            aluguer_fim = datetime.strptime(aluguer["Fim"], "%d-%m-%Y")

            # Verifica sobreposição de datas
            if (inicio <= aluguer_fim and fim >= aluguer_inicio):
                veiculos_ocupados.add(aluguer["Matrícula"])

        veiculos_disponiveis = [
            (matricula, dados) for matricula, dados in gestor_veiculos.veiculos.items()
            if matricula not in veiculos_ocupados
        ]

        print(f"\nVEÍCULOS DISPONÍVEIS de {data_inicio} a {data_fim}")
        
        if not veiculos_disponiveis:
            print("Nenhum veículo disponível neste período.")
            return

        print("+------------+--------------+--------------+------------+")
        print("| Matrícula  | Marca        | Modelo       | Preço/Dia  |")
        print("+------------+--------------+--------------+------------+")
        for matricula, dados in veiculos_disponiveis:
            print(f"| {matricula:<10} | {dados['Marca']:<12} | {dados['Modelo']:<12} | {dados['Preço/Dia']:<10.2f} |")
        print("+------------+--------------+--------------+------------+")

    def veiculos_mais_alugados(self, top_n=5): 
        contagem = defaultdict(int)

        for aluguer in self.alugueres:
            contagem[aluguer["Matrícula"]] += 1

        if not contagem:
            print("Nenhum aluguer registado.")
            return

        veiculos_top = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:top_n]

        if not veiculos_top:
            print("Nenhum veículo foi alugado até agora.")
            return

        print(f"\nTOP {top_n} VEÍCULOS MAIS ALUGADOS")
        print("+------------+----------------------+")
        print("| Matrícula  | Nº de Alugueres      |")
        print("+------------+----------------------+")
        for matricula, quantidade in veiculos_top:
            print(f"| {matricula:<10} | {quantidade:^20} |")
        print("+------------+----------------------+")

    def relatorio_faturacao(self, periodo='mes'):
        """Gera relatório de faturação agrupado por período"""
        faturamento = defaultdict(float)
        
        for aluguer in self.alugueres:
            data = datetime.strptime(aluguer['Início'], '%d-%m-%Y')
            
            if periodo == 'ano':
                chave = data.year
            elif periodo == 'mes':
                chave = f"{data.year}-{data.month:02d}"
            elif periodo == 'semana':
                chave = f"{data.year}-W{data.isocalendar()[1]:02d}"
            
            faturamento[chave] += aluguer['Total']
        
        # Exibir resultados
        print(f"\nRELATÓRIO DE FATURAÇÃO ({periodo.upper()})")
        print("="*40)
        for periodo, total in sorted(faturamento.items()):
            print(f"{periodo}: {total:.2f}€")
        print("="*40)
        print(f"TOTAL GERAL: {sum(faturamento.values()):.2f}€\n")

    def relatorio_detalhado(self, periodo='mes'): 
        """Relatório detalhado com aluguéis por período"""
        periodos = defaultdict(list)

        for aluguer in self.alugueres:
            data = datetime.strptime(aluguer['Início'], '%d-%m-%Y')
            
            if periodo == 'ano':
                chave = data.year
            elif periodo == 'mes':
                chave = f"{data.year}-{data.month:02d}"
            elif periodo == 'semana':
                chave = f"{data.year}-W{data.isocalendar()[1]:02d}"
            
            periodos[chave].append(aluguer)

        print(f"\nRELATÓRIO DETALHADO ({periodo.upper()})")
        print("=" * 90)
        for periodo_chave, alugueres in sorted(periodos.items()):
            print(f"\nPERÍODO: {periodo_chave}")
            print("+------------+------------+------------+------------+------------+")
            print("| Início     | Fim        | Matrícula  | NIF        | Total (€)  |")
            print("+------------+------------+------------+------------+------------+")
            total_periodo = 0
            for a in alugueres:
                print(f"| {a['Início']:<10} | {a['Fim']:<10} | {a['Matrícula']:<10} | {a['NIF']:<10} | {a['Total']:<10.2f} |")
                total_periodo += a['Total']
            print("+------------+------------+------------+------------+------------+")
            print(f"TOTAL DO PERÍODO: {total_periodo:.2f}€")
        print("=" * 90)


# ---------------- Exemplo de uso ----------------

#gestor_veiculos = GestorVeiculos()
#gestor_clientes = GestorClientes()
#gestor_alugueres = GestorAlugueres()

# Adição de veículos diferentes sem dar erros
#gestor_veiculos.adicionar_veiculo("AA-00-BB", "Ford", "Focus", "2019", "Diesel", 40000, 25.5) # Matricula, Marca, Modelo, Ano, Combustível, Quilómetros, Preço/Dia
#gestor_veiculos.adicionar_veiculo("ZZ-11-CC", "Peugeot", "208", "2021", "Gasolina", 30000, 30)
#gestor_veiculos.adicionar_veiculo("CC-00-BB", "Honda", "Civic", "2018", "Gasolina", 60000, 22)

# Adição de veículo para provocar o erro de matrícula repetida
#gestor_veiculos.adicionar_veiculo("AA-00-BB", "Honda", "Civic", "2018", "Gasolina", 60000, 25.5)

# Adição de veículo para provocar o erro de ano inválido
#gestor_veiculos.adicionar_veiculo("GG-00-BB", "Honda", "Civic", "1910", "Gasolina", 60000, 25.5)


# Atualização do veículo sem dar erros
#gestor_veiculos.atualizar_veiculo("AA-00-BB", nova_matricula="XY-98-ZT", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=120000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de matrícula inexistente
#gestor_veiculos.atualizar_veiculo("BB-00-BB", nova_matricula="XY-98-ZT", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=75000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de nova matrícula repetida
#gestor_veiculos.atualizar_veiculo("CC-00-BB", nova_matricula="ZZ-11-CC", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=75000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de ano inválido
#gestor_veiculos.atualizar_veiculo("ZZ-11-CC", nova_matricula="ZZ-11-CC", marca="Seat", modelo="Ibiza", data="2030", combustivel="Diesel", quilometros=75000, preco_dia=25.5)


# Adição de clientes diferentes sem dar erros
#gestor_clientes.adicionar_cliente("111222333", "Ana Costa", "10-03-1990") # NIF, Nome, Data Nascimento
#gestor_clientes.adicionar_cliente("444555666", "Carlos Martins", "21-07-1982")
#gestor_clientes.adicionar_cliente("555555666", "Maria Oliveira", "20-10-1985")

# Adição de clientes para provocar o erro de NIF repetido
#gestor_clientes.adicionar_cliente("111222333", "Maria Oliveira", "20-10-1985")


# Atualização dos dados do cliente sem dar erros
#gestor_clientes.atualizar_cliente("111222333", novo_nif="987654321", nome="João Pedro", data_nascimento="20-06-1991")

# Atualização dos dados do cliente para provocar o erro de NIF inexistente
#gestor_clientes.atualizar_cliente("131222333", novo_nif="982654321", nome="João Pedro", data_nascimento="20-06-1991")

# Atualização dos dados do cliente para provocar o erro de novo NIF repetido
#gestor_clientes.atualizar_cliente("555555666", novo_nif="444555666", nome="João Pedro", data_nascimento="20-06-1991")


# Criar alugueres
#gestor_alugueres.adicionar_aluguer("987654321", "XY-98-ZT", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes) # NIF Cliente, Matrícula Veículo, Data Início, Data Fim
#gestor_alugueres.adicionar_aluguer("444555666", "ZZ-11-CC", "05-05-2025", "15-05-2025", gestor_veiculos, gestor_clientes)

# Erro aluguer sobreposto
#gestor_alugueres.adicionar_aluguer("444555666", "XY-98-ZT", "08-05-2025", "12-05-2025", gestor_veiculos, gestor_clientes)

# Erro NIF inexistente
#gestor_alugueres.adicionar_aluguer("111222333", "XY-98-ZT", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes)

# Erro matrícula inexistente
#gestor_alugueres.adicionar_aluguer("987654321", "AA-00-BB", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes)


# Listar todos os veículos
#gestor_veiculos.listar_veiculos()

# Listar a distância total percorrida pela frota
#gestor_veiculos.quilometragem_total()

# Listar os veículos com mais de 100000km e com necessidade de manutenção preventiva
#gestor_veiculos.manutencao_preventiva(100000)

# Listar todos os clientes
#gestor_clientes.listar_clientes()

# Listar todos os alugueres
#gestor_alugueres.listar_alugueres()

# Lista dos 5 veículos mais alugados
#gestor_alugueres.veiculos_mais_alugados()

# Listar veículos disponíveis num determinado período
#gestor_alugueres.veiculos_disponiveis("13-05-2025", "15-05-2025", gestor_veiculos)


# Exibir Relatórios
#gestor_alugueres.relatorio_faturacao('semana')  # Por semana
#gestor_alugueres.relatorio_faturacao('mes')     # Por mês
#gestor_alugueres.relatorio_faturacao('ano')     # Por ano

# Exibir Relatórios Detalhados
#gestor_alugueres.relatorio_detalhado('semana')
#gestor_alugueres.relatorio_detalhado('mes')
#gestor_alugueres.relatorio_detalhado('ano')
