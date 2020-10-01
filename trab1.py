from numpy import linalg, array, matmul, zeros, append
from sys import argv, exit
from math import pi, sqrt
import string
import re
import os

os.system('cls')


# definição de constantes
DISPOSITIVO = 0
NO_INICIAL = 1
NO_FINAL = 2
VALOR = 3
REFP = 3
REFN = 4
# constantes para transformador ideal
NO_A = 1
NO_B = 2
VALOR_1 = 3
NO_C = 4
NO_D = 5
VALOR_2 = 6

multiplicadores = {"n": 0.000000001, "u": 0.000001,
                   "m": 0.001, "k": 1000, "Meg": 1000000}
resistor = {"no+": 1, "no-": 2, "resistencia": 3}
iS = {"noS": 1, "noE": 2, "corrente": 3}
icDC = {"noS": 1, "noE": 2, "ref+": 3, "ref-": 4, "transc": 5}

# vê qual o numero de nós e guarda seus nomes em um dicionário


def conta_nos(lista):
    numero_nos = 0
    nos = {'0': 0}  # cria um dicionário já com o nó 0
    for i in range(len(lista)):
        if(lista[i][NO_INICIAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_INICIAL]] = numero_nos
        if(lista[i][NO_FINAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_FINAL]] = numero_nos
    return numero_nos, nos

# trata casos de valores como por exemplo "1k, 500m"


def multiplica(valor):
    if (valor[-1] in multiplicadores):
        return float(valor[:-1]) * multiplicadores[valor[-1]]
    else:
        return valor

# verifica se existe alguma fonte senoidal e guarda a frequência


def encontra_omega(lista):
    frequencia = 0
    for i in range(len(lista)):
        if re.search("^SIN", lista[i][iS["corrente"]]):
            # retira o '\n' do final das linhas para evitar erros de leitura
            if netlist[i][-1][-1] == '\n':
                netlist[i][-1] = netlist[i][-1][:-1]
            frequencia = str(lista[i][6])
            # toma a frequencia em radianos
            frequencia = 2*pi*float(multiplica(frequencia))
    return frequencia


# abertura do arquivo com a netlist
# file_name = 'netlist.txt'
if len(argv) > 1:
    file_name = str(argv[1])
else:
    file_name = ''

arquivo_aberto = False
while not arquivo_aberto:
    if file_name == 'exit' or file_name == 'sair':
        exit()
    if len(file_name) < 1:
        file_name = input("Entre com o nome da netlist a ser lida: ")
    try:
        file = open(file_name)
    except FileNotFoundError:
        file_name = input(
            "Netlist não encontrada! Digite novamente COM CALMA: ")
    else:
        arquivo_aberto = True

os.system('cls')

# leitura do arquivo e formatação das linhas
print("-> Recebendo dados da netlist. Calma Gabriel...\n")
netlist = file.readlines()
file.close()
netlist = [i.split(' ') for i in netlist]

dimensao, nomes_nos = conta_nos(netlist)
omega = encontra_omega(netlist)
# Cria as matrizes G e i
# adiciona-se 1 para compensar a linha e a coluna 0 serem excluídas
mat_G = zeros((dimensao+1, dimensao+1), dtype=complex)
mat_i = zeros((dimensao+1, 1), dtype=complex)
print("-> Interpretando os dados. Segura aí...\n")
for i in range(len(netlist)):
    if netlist[i][-1][-1] == '\n':  # retira o '\n' do final das linhas para evitar erros de leitura
        netlist[i][-1] = netlist[i][-1][:-1]

    dis = netlist[i][DISPOSITIVO]  # Pega o nome do dispositivo
    # retorna um número correspondente do nó
    origem = nomes_nos[netlist[i][NO_INICIAL]]
    destino = nomes_nos[netlist[i][NO_FINAL]]
    # identificação do tipo de dispostivo e o adiciona às matrizes de acordo com sua estampa
    if (dis[0] == 'R'):
        netlist[i][resistor["resistencia"]] = float(
            multiplica(netlist[i][resistor["resistencia"]]))
        mat_G[origem][origem] += 1/float(netlist[i][resistor["resistencia"]])
        mat_G[origem][destino] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][origem] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][destino] += 1/float(netlist[i][resistor["resistencia"]])
    if (dis[0] == 'I'):
        # Se for uma corrente senoidal
        if re.search("^SIN", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]*(-1j)
        if re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        netlist[i][iS["corrente"]] = multiplica(netlist[i][iS["corrente"]])
        mat_i[origem][0] += -float(netlist[i][iS["corrente"]])
        mat_i[destino][0] += float(netlist[i][iS["corrente"]])
    if(dis[0] == 'V'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][5]
        if re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
        dimensao += 1
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array(
            [[-float(multiplica(netlist[i][iS["corrente"]]))]]), axis=0)
    if(dis[0] == 'C'):
        mat_G[origem][origem] += float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[origem][destino] += - \
            float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[destino][origem] += - \
            float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[destino][destino] += float(multiplica(netlist[i]
                                                    [VALOR]))*1j*omega
    if(dis[0] == 'L'):
        mat_G[origem][origem] += 1 / \
            (float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[origem][destino] += -1 / \
            (float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[destino][origem] += -1 / \
            (float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[destino][destino] += 1 / \
            (float(multiplica(netlist[i][VALOR]))*1j*omega)
    if(dis[0] == 'G'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        mat_G[origem][referenciaPos] += float(netlist[i][icDC["transc"]])
        mat_G[origem][referenciaNeg] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaPos] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaNeg] += float(netlist[i][icDC["transc"]])
    if(dis[0] == 'E'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
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
    if(dis[0] == 'F'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
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
    if(dis[0] == 'H'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
        dimensao += 1
        horizontal[0, referenciaPos] += -1
        horizontal[0, referenciaNeg] += 1
        vertical[referenciaPos, 0] += 1
        vertical[referenciaNeg, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
        dimensao += 1
        horizontal[0, origem] += -1
        horizontal[0, destino] += 1
        horizontal[0, -1] += ganho
        vertical[origem, 0] += 1
        vertical[destino, 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)
    if(dis[0] == 'K'):
        n = sqrt(
            float(multiplica(netlist[i][VALOR_2]))/float(multiplica(netlist[i][VALOR_1])))
        horizontal = zeros((1, dimensao+1))
        vertical = zeros((dimensao+2, 1))
        dimensao += 1
        horizontal[0, nomes_nos[netlist[i][NO_A]]] += n
        horizontal[0, nomes_nos[netlist[i][NO_B]]] += -n
        horizontal[0, nomes_nos[netlist[i][NO_C]]] += -1
        horizontal[0, nomes_nos[netlist[i][NO_D]]] += 1
        vertical[nomes_nos[netlist[i][NO_A]], 0] += -n
        vertical[nomes_nos[netlist[i][NO_B]], 0] += n
        vertical[nomes_nos[netlist[i][NO_C]], 0] += 1
        vertical[nomes_nos[netlist[i][NO_D]], 0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i, array([[0]]), axis=0)


print("-> Netlist lida com sucesso! (eu acho)\n")
# Exclui a linha e a coluna do nó GND (nó 0)
mat_G = mat_G[1:, 1:]
mat_i = mat_i[1:, 0]
del nomes_nos['0']
# if(linalg.det(mat_G)==0):
#     exit("Singular matrix! Check your netlist for non-closed circuits.")

print("-> Calculando matrizes.\n")
try:
    resultado = matmul(linalg.inv(mat_G), mat_i)
except linalg.LinAlgError:
    exit("Erro ao calcular a inversa da matriz. Verifique a netlist. (o programa tá perfeito. o problema com certeza é com você >:(   )")

print("----------------- Here we go! -----------------\n")
if(omega == 0):  # Se for um circuito DC
    for i in nomes_nos:
        print(f'V({i}): {round(resultado[nomes_nos[i]-1].real,4)} V')
else:
    for i in nomes_nos:
        função = f'V({i}): {round(resultado[nomes_nos[i]-1].real,3)}cos({round(omega,3)}t)'
        if (resultado[nomes_nos[i]-1].imag != 0.0):
            função += f'+ {round(resultado[nomes_nos[i]-1].imag,3)}sin({round(omega,3)}t) V'
        print(função)
