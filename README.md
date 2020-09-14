# Trabalho 1 de Ciruitos Elétricos 2 UFRJ
### Setembro 2020
Este guia visa descrever o funcionamento do programa que resolve a netlist formatada estilo _SPICE_ de um circuito

## Escrita da netlist
O programa ceAC.py possui suporte para resolver circuitos compostos por resistores e fontes de corrente (controladas ou independentes), capacitores, indutores e fontes AC senoidais
É possível utilizar uma netlist vinda diretamente de um programa que utilize _PSPICE_
Caso seja necessário montar o circuito manualmente, os padrões são os seguintes:
**Resistor:**
  R1 <nó 1> <nó 2> <valor da resistência>

**Fonte de corrente DC:**
  I1 <nó de saída de corrente> <nó destino da corrente> <valor da corrente>

**Fonte de corrente controlada DC:**
  G1 <nó de saída de corrente> <nó destino da corrente> <nó de referência> <valor da corrente>

**Capacitor:**
  C1 <nó 1> <nó 2> <valor da capacitância>

**Indutor:**
  L1 <nó 1> <nó 2> <valor da indutância>

**Fonte de corrente AC:**
  I1 <nó de saída de corrente> <nó destino da corrente> SIN(0 <amplitude de corrente> <frequencia em Hz)

**Exemplo**
I1 0 1 500m
R1 2 1 1
R2 5 2 2.3k
R3 3 2 2k
R6 0 4 1000
C1 3 5 10µ
L1 3 4 10µ
