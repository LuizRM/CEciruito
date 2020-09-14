from numpy import linalg, array, matmul
from sys import argv
import string

#definição de constantes
DISPOSITIVO = 0
NO_INICIAL = 1
NO_FINAL = 2
VALOR = 3
REFP = 3
REFN = 4
multiplicadores = {"n":0.000000001, "u":0.000001, "m":0.001, "k":1000, "Meg":1000000}

#vê qual o numero máximo de nós para montar as matrizes
def conta_nos(lista):
    maximo = 0
    for i in range(len(lista)):
        if(int(lista[i][NO_INICIAL]) > maximo):
            maximo = int(lista[i][NO_INICIAL])
        if(int(lista[i][NO_FINAL]) > maximo):
            maximo = int(lista[i][NO_FINAL])
    return maximo

def cria_matriz(linhas, colunas):
    matriz = []
    for i in range(linhas):
        linha = []
        for i in range(colunas):
            linha.append(0)
        matriz.append(linha)
    return matriz


#abertura do arquivo com a netlist
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

#leitura do arquivo e formatação das linhas
netlist = file.readlines()
file.close()
netlist  = [i.split(' ') for i in netlist]

dimensao = conta_nos(netlist)
mat_G = cria_matriz(dimensao+1,dimensao+1) #adiciona-se 1 para compensar a linha e a coluna 0 serem excluídas
mat_i = cria_matriz(dimensao+1,1)
for i in range(len(netlist)):
    dis = netlist[i][DISPOSITIVO][0]
    origem = int(netlist[i][NO_INICIAL])
    destino = int(netlist[i][NO_FINAL])
    if (dis == 'R'):
        if (netlist[i][VALOR][-2] in multiplicadores):
            netlist[i][VALOR] = float(netlist[i][VALOR][:-2]) * multiplicadores[netlist[i][VALOR][-2]]
        mat_G[origem][origem] += 1/float(netlist[i][VALOR])
        mat_G[origem][destino] += -1/float(netlist[i][VALOR])
        mat_G[destino][origem] += -1/float(netlist[i][VALOR])
        mat_G[destino][destino] += 1/float(netlist[i][VALOR])
    if (dis == 'I'):
        if (netlist[i][VALOR][-2] in multiplicadores):
            netlist[i][VALOR] = float(netlist[i][VALOR][:-2]) * multiplicadores[netlist[i][VALOR][-2]]
        mat_i[origem][0] += -float(netlist[i][VALOR])
        mat_i[destino][0] += float(netlist[i][VALOR])
    if(dis == 'G'):
        referenciaPos = int(netlist[i][REFP])
        referenciaNeg = int(netlist[i][REFN])
        mat_G[origem][referenciaPos] += float(netlist[i][VALOR+2])
        mat_G[origem][referenciaNeg] += -float(netlist[i][VALOR+2])
        mat_G[destino][referenciaPos] += -float(netlist[i][VALOR+2])
        mat_G[destino][referenciaNeg] += float(netlist[i][VALOR+2])

#Converte as matrizes para arrays do numpy
#e exclui a linha e a coluna do nó GND (nó 0)
mat_G = array(mat_G)
mat_G = mat_G[1:,1:]
mat_i = array(mat_i)
mat_i = mat_i[1:,0]

resultado =  matmul(linalg.inv(mat_G), mat_i)
print("Resultados---------------------------------------")
for i in range(len(resultado)):
    print(f'V({i+1}): {resultado[i]} V')
