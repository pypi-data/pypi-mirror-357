# Gestão de Alugueres de Automóveis

## Explicação do Projeto

Este projeto tem como objetivo o desenvolvimento de um sistema completo de gestão de alugueres de automóveis, permitindo a administração eficiente dos clientes, da frota de veículos e dos alugueres realizados. Para além disso, a aplicação oferece relatórios e estatísticas operacionais úteis para apoiar a tomada de decisões.

O sistema contempla as seguintes funcionalidades:

- Gestão de Veículos
- Gestão de Clientes
- Gestão de Alugueres
- Relatórios e Estatísticas

## Como Utilizar

Siga os segintes passos:
```
from gestao_aluguer import GestorVeiculos, GestorClientes, GestorAlugueres
```
```
gestor_veiculos = GestorVeiculos()
gestor_clientes = GestorClientes()
gestor_alugueres = GestorAlugueres()
```

Dados para teste dos veículos:
```
# Adição de veículos diferentes sem dar erros
gestor_veiculos.adicionar_veiculo("AA-00-BB", "Ford", "Focus", "2019", "Diesel", 40000, 25.5) # Matricula, Marca, Modelo, Ano, Combustível, Quilómetros, Preço/Dia
gestor_veiculos.adicionar_veiculo("ZZ-11-CC", "Peugeot", "208", "2021", "Gasolina", 30000, 30)
gestor_veiculos.adicionar_veiculo("CC-00-BB", "Honda", "Civic", "2018", "Gasolina", 60000, 22)

# Adição de veículo para provocar o erro de matrícula repetida
gestor_veiculos.adicionar_veiculo("AA-00-BB", "Honda", "Civic", "2018", "Gasolina", 60000, 25.5)

# Adição de veículo para provocar o erro de ano inválido
gestor_veiculos.adicionar_veiculo("GG-00-BB", "Honda", "Civic", "1910", "Gasolina", 60000, 25.5)
```
```
# Atualização do veículo sem dar erros
gestor_veiculos.atualizar_veiculo("AA-00-BB", nova_matricula="XY-98-ZT", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=120000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de matrícula inexistente
gestor_veiculos.atualizar_veiculo("BB-00-BB", nova_matricula="XY-98-ZT", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=75000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de nova matrícula repetida
gestor_veiculos.atualizar_veiculo("CC-00-BB", nova_matricula="ZZ-11-CC", marca="Seat", modelo="Ibiza", data="2010", combustivel="Diesel", quilometros=75000, preco_dia=25.5)

# Atualização do veículo para provocar o erro de ano inválido
gestor_veiculos.atualizar_veiculo("ZZ-11-CC", nova_matricula="ZZ-11-CC", marca="Seat", modelo="Ibiza", data="2030", combustivel="Diesel", quilometros=75000, preco_dia=25.5)
```

Listagens dos veículos:
```
# Listar todos os veículos
gestor_veiculos.listar_veiculos()
```
```
# Listar a distância total percorrida pela frota
gestor_veiculos.quilometragem_total()
```
```
# Listar os veículos com mais de 100000km e com necessidade de manutenção preventiva
gestor_veiculos.manutencao_preventiva(100000)
```
```
# Listar veículos disponíveis num determinado período
gestor_alugueres.veiculos_disponiveis("13-05-2025", "15-05-2025", gestor_veiculos)
```

Dados para teste dos clientes:
```
# Adição de clientes diferentes sem dar erros
gestor_clientes.adicionar_cliente("111222333", "Ana Costa", "10-03-1990") # NIF, Nome, Data Nascimento
gestor_clientes.adicionar_cliente("444555666", "Carlos Martins", "21-07-1982")
gestor_clientes.adicionar_cliente("555555666", "Maria Oliveira", "20-10-1985")

# Adição de clientes para provocar o erro de NIF repetido
gestor_clientes.adicionar_cliente("111222333", "Maria Oliveira", "20-10-1985")

gestor_clientes.adicionar_cliente("245635465", "Carlos Oliveira", "20-10-1985")
```
```
# Atualização dos dados do cliente sem dar erros
gestor_clientes.atualizar_cliente("111222333", novo_nif="987654321", nome="João Pedro", data_nascimento="20-06-1991")

# Atualização dos dados do cliente para provocar o erro de NIF inexistente
gestor_clientes.atualizar_cliente("131222333", novo_nif="982654321", nome="João Pedro", data_nascimento="20-06-1991")

# Atualização dos dados do cliente para provocar o erro de novo NIF repetido
gestor_clientes.atualizar_cliente("555555666", novo_nif="444555666", nome="João Pedro", data_nascimento="20-06-1991")
```

Listagem dos clientes:
```
# Listar todos os clientes
gestor_clientes.listar_clientes()
```

Dados para teste dos alugueres:
```
# Criar alugueres
gestor_alugueres.adicionar_aluguer("987654321", "XY-98-ZT", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes) # NIF Cliente, Matrícula Veículo, Data Início, Data Fim
gestor_alugueres.adicionar_aluguer("444555666", "ZZ-11-CC", "05-05-2025", "15-05-2025", gestor_veiculos, gestor_clientes)
gestor_alugueres.adicionar_aluguer("245635465", "ZZ-11-CC", "25-05-2025", "28-05-2025", gestor_veiculos, gestor_clientes)

# Erro aluguer sobreposto
gestor_alugueres.adicionar_aluguer("444555666", "XY-98-ZT", "08-05-2025", "12-05-2025", gestor_veiculos, gestor_clientes)

# Erro NIF inexistente
gestor_alugueres.adicionar_aluguer("111222333", "XY-98-ZT", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes)

# Erro matrícula inexistente
gestor_alugueres.adicionar_aluguer("987654321", "AA-00-BB", "01-05-2025", "10-05-2025", gestor_veiculos, gestor_clientes)
```

Listagens dos alugueres:
```
# Listar todos os alugueres
gestor_alugueres.listar_alugueres()
```
```
# Lista dos 5 veículos mais alugados
gestor_alugueres.veiculos_mais_alugados()
```

Listagens dos relatórios de faturação:
```
# Exibir Relatórios
gestor_alugueres.relatorio_faturacao('semana')  # Por semana
```
```
gestor_alugueres.relatorio_faturacao('mes')     # Por mês
```
```
gestor_alugueres.relatorio_faturacao('ano')     # Por ano
```
```
# Exibir Relatórios Detalhados
gestor_alugueres.relatorio_detalhado('semana')
```
```
gestor_alugueres.relatorio_detalhado('mes')
```
```
gestor_alugueres.relatorio_detalhado('ano')
```

## Links

- [Pypi](https://pypi.org/project/gestao-aluguer-veiculos/)

- [Google Docs](https://docs.google.com/document/d/1SoMET9-RumovZsxgeDGHR2yywDy_AiDuqkgyWAjxqM8/edit?usp=sharing)

- [Notebook](https://colab.research.google.com/drive/1nCCzMtMVTlyqTaQs-Zk4OQb242BSLZD8?usp=sharing)
