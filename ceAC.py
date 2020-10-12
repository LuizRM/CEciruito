print("Importing python libraries")
from numpy import linalg, array, matmul, zeros, append, sqrt
from sys import argv, exit
import re
import os

# definição de constantes
DISPOSITIVO = 0
NO_INICIAL = 1
NO_FINAL = 2
VALOR = 3
REFP = 3
REFN = 4
multiplicadores = {"n": 0.000000001, "u": 0.000001, "m": 0.001, "k": 1000, "Meg": 1000000, "µ":0.000001}
resistor = {"no+": 1, "no-": 2, "resistencia": 3}
iS = {"noS": 1, "noE": 2, "corrente": 3}
icDC = {"noS": 1, "noE": 2, "ref+": 3, "ref-": 4, "transc": 5}


# vê qual o numero de nós e guarda seus nomes em um dicionário
def conta_nos(lista):
    numero_nos = 0
    nos = {'0': 0}  # cria um dicionário já com o nó 0
    for i in range(len(lista)):
        if (lista[i][NO_INICIAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_INICIAL]] = numero_nos
        if (lista[i][NO_FINAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_FINAL]] = numero_nos
    return numero_nos, nos


# trata casos de valores como por exemplo "1k, 500m"
def multiplica(valor):
    if (valor[-1] in multiplicadores):
        return float(valor[:-1]) * multiplicadores[valor[-1]]
    else:
        return float(valor)


# verifica se existe alguma fonte senoidal e guarda a frequência
def encontra_omega(lista):
    frequencia = 0
    for i in range(len(lista)):
        if re.search("^SIN", lista[i][iS["corrente"]]):
            if netlist[i][-1][-1] == '\n':  # retira o '\n' do final das linhas para evitar erros de leitura
                netlist[i][-1] = netlist[i][-1][:-1]
            if lista[i][-1][-1] == ')':
                frequencia = str(lista[i][-1][:-1])  # retira o ')' do final do valor da frequencia
            else:
                frequencia = str(lista[i][-1])
            frequencia = float(multiplica(frequencia))  # toma a frequencia em radianos
    return frequencia


# abertura do arquivo com a netlist
file_name = str(argv[1])
arquivo_aberto = False
while not arquivo_aberto:
    # file_name = input("Digite o nome do arquivo a ser lido: ")
    try:
        file = open(file_name)
    except FileNotFoundError:
        file_name = input("Arquivo não encontrado!Digite novamente: ")
    else:
        arquivo_aberto = True

# leitura do arquivo e formatação das linhas
print("Fetching data from netlist file...")
netlist = file.readlines()
file.close()
if netlist[-1][0] == '\n':
    netlist = netlist[:-1]
netlist = [i.split(' ') for i in netlist]
nomes_correntes = {}

dimensao, nomes_nos = conta_nos(netlist)
nos = dimensao
numero_componentes = 0
omega = encontra_omega(netlist)
# Cria as matrizes G e i
mat_G = zeros((dimensao + 1, dimensao + 1),
              dtype=complex)  # adiciona-se 1 para compensar a linha e a coluna 0 serem excluídas
mat_i = zeros((dimensao + 1, 1), dtype=complex)
print("Reading netlist...")
for i in range(len(netlist)):
    if netlist[i][-1][-1] == '\n':  # retira o '\n' do final das linhas para evitar erros de leitura
        netlist[i][-1] = netlist[i][-1][:-1]

    numero_componentes += 1
    dis = netlist[i][DISPOSITIVO]  # Pega o nome do dispositivo
    origem = nomes_nos[netlist[i][NO_INICIAL]]  # retorna um número correspondente do nó
    destino = nomes_nos[netlist[i][NO_FINAL]]
    # identificação do tipo de dispostivo e o adiciona às matrizes de acordo com sua estampa
    if (dis[0] == 'R'):
        netlist[i][resistor["resistencia"]] = float(multiplica(netlist[i][resistor["resistencia"]]))
        mat_G[origem][origem] += 1 / float(netlist[i][resistor["resistencia"]])
        mat_G[origem][destino] += -1 / float(netlist[i][resistor["resistencia"]])
        mat_G[destino][origem] += -1 / float(netlist[i][resistor["resistencia"]])
        mat_G[destino][destino] += 1 / float(netlist[i][resistor["resistencia"]])
    elif (dis[0] == 'I'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):  # Se for uma corrente senoidal
            netlist[i][iS["corrente"]] = multiplica(netlist[i][5]) * (-1j)
        elif re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = multiplica(netlist[i][5])
        else:
            netlist[i][iS["corrente"]] = multiplica(netlist[i][iS["corrente"]])
        mat_i[origem][0] += -netlist[i][iS["corrente"]]
        mat_i[destino][0] += netlist[i][iS["corrente"]]
    elif (dis[0] == 'V'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):  # Se for uma corrente senoidal
            netlist[i][iS["corrente"]] = multiplica(netlist[i][5]) * (-1j)
        elif re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = multiplica(netlist[i][4])
        else:
            netlist[i][iS["corrente"]] = multiplica(netlist[i][iS["corrente"]])
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        nomes_correntes[dis] = dimensao
        dimensao += 1
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[-netlist[i][iS["corrente"]]]]), axis=0)
    elif (dis[0] == 'C'):
        mat_G[origem][origem] += multiplica(netlist[i][VALOR]) * 1j * omega
        mat_G[origem][destino] += -multiplica(netlist[i][VALOR]) * 1j * omega
        mat_G[destino][origem] += -multiplica(netlist[i][VALOR]) * 1j * omega
        mat_G[destino][destino] += multiplica(netlist[i][VALOR]) * 1j * omega
    elif (dis[0] == 'L'):
        mat_G[origem][origem] += 1 / (multiplica(netlist[i][VALOR]) * 1j * omega)
        mat_G[origem][destino] += -1 / (multiplica(netlist[i][VALOR]) * 1j * omega)
        mat_G[destino][origem] += -1 / (multiplica(netlist[i][VALOR]) * 1j * omega)
        mat_G[destino][destino] += 1 / (multiplica(netlist[i][VALOR]) * 1j * omega)
    elif (dis[0] == 'G'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        mat_G[origem][referenciaPos] += float(netlist[i][icDC["transc"]])
        mat_G[origem][referenciaNeg] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaPos] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaNeg] += float(netlist[i][icDC["transc"]])
    elif (dis[0] == 'E'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        horizontal[0, referenciaPos] += ganho
        horizontal[0, referenciaNeg] += -ganho
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
    elif (dis[0] == 'F'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        vertical[referenciaPos, 0] += 1
        vertical[referenciaNeg, 0] += -1
        vertical[origem, 0] += ganho
        vertical[destino, 0] += -ganho
        horizontal[0, referenciaPos] += -1
        horizontal[0, referenciaNeg] += 1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
    elif (dis[0] == 'H'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        horizontal[0, referenciaPos] += -1
        horizontal[0, referenciaNeg] += 1
        vertical[referenciaPos, 0] += 1
        vertical[referenciaNeg, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        horizontal[0, -1] += ganho
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
    elif (dis[0] == 'X'):
        referenciaPos = nomes_nos[netlist[i][4]]
        referenciaNeg = nomes_nos[netlist[i][5]]
        ganho = 1 / sqrt(float(netlist[i][3]) / float(netlist[i][6]))
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        vertical[referenciaPos, 0] += 1
        vertical[referenciaNeg, 0] += -1
        vertical[origem, 0] += ganho
        vertical[destino, 0] += -ganho
        horizontal[0, referenciaPos] += -1
        horizontal[0, referenciaNeg] += 1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
        referenciaPos = origem
        referenciaNeg = destino
        origem = nomes_nos[netlist[i][4]]
        destino = nomes_nos[netlist[i][5]]
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        horizontal[0, referenciaPos] += ganho
        horizontal[0, referenciaNeg] += -ganho
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
    elif (dis[0] == 'O'):
        destino = nomes_nos[netlist[i][1]]
        origem = nomes_nos[netlist[i][2]]
        referenciaPos = nomes_nos[netlist[i][3]]
        referenciaNeg = nomes_nos[netlist[i][4]]
        horizontal = zeros((1, dimensao + 1))
        vertical = zeros((dimensao + 2, 1))
        dimensao += 1
        vertical[destino, 0] += 1
        vertical[origem, 0] += -1
        horizontal[0, referenciaPos] += 1
        horizontal[0, referenciaNeg] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)

print("Netlist read!")
# Exclui a linha e a coluna do nó GND (nó 0)
mat_G = mat_G[1:, 1:]
mat_i = mat_i[1:, 0]
del nomes_nos['0']
# if(linalg.det(mat_G)==0):
#     exit("Singular matrix! Check your netlist for non-closed circuits.")

print("Calculating matrices...")
resultado = 0
try:
    resultado = matmul(linalg.inv(mat_G), mat_i)
except linalg.LinAlgError:
    exit("Singular matrix! Check your netlist.")

os.system('cls' if os.name == 'nt' else 'clear')
print(f"Número de nós: {nos}. Número de componentes: {numero_componentes}. Número de variáveis: {dimensao}")
print("Results---------------------------------------")
if (omega == 0):  # Se for um circuito DC
    for i in nomes_nos:
        print(f'V({i}): {round(resultado[nomes_nos[i] - 1].real, 4)} V')
    for i in nomes_correntes:
        print(f'I({i}): {round(resultado[nomes_correntes[i]].real, 4)} A')
else:
    for i in nomes_nos:
        funcao = f'V({i}): {round((-resultado[nomes_nos[i] - 1].imag), 5)}sin({round(omega, 3)}t)'
        if resultado[nomes_nos[i] - 1].real != 0.0:
            funcao += " %+f" % round(resultado[nomes_nos[i] - 1].real, 5)
            funcao += f'cos({round(omega, 3)}t) V'
        print(funcao)
    for i in nomes_correntes:
        funcao = f'I({i}): {round((-resultado[nomes_correntes[i]].imag), 5)}sin({round(omega, 3)}t)'
        if (resultado[nomes_correntes[i]].real != 0.0):
            funcao += " %+f" % round(resultado[nomes_correntes[i]].real, 5)
            funcao += f'cos({round(omega, 3)}t) V'
        print(funcao)
