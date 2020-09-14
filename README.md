# Trabalho 1 de Ciruitos Elétricos 2 UFRJ
### Setembro 2020
Este guia visa descrever o funcionamento do programa que resolve a netlist formatada estilo _SPICE_ de um circuito

## Escrita da netlist
O programa ceDC.py possui suporte para resolver circuitos compostos por resistores e fontes de corrente (controladas ou independentes). O programa ceAC.py adiciona suporte para capacitores, indutores e fontes AC
É possível utilizar uma netlist vinda diretamente de um programa que utilize _PSPICE_, desde que os nós sejam numerados, ou seja, sejam designados por um int.
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
  
**Transformador:**
  T1 <nó 1> <nó 2> <nó 3> <nó 4> <indutância nós 1 e 2> <indutância nós 3 e 4> <coeficiente de acoplamento M>
  
**Fonte de corrente AC:**
  I1 <nó de saída de corrente> <nó destino da corrente> <amplitude de corrente> 
  
**Exemplo**
I1 0 1 500m
R1 2 1 1
R2 5 2 2.3k
R3 3 2 2k
R6 0 4 1000
C1 3 5 10µ
L1 3 4 10µ
