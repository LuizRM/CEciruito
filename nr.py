import os
from sympy import *
import numpy as np

def nraphson(fn, dfn,x,tol=0.001,maxiter=100):
    for i in range(maxiter):
        try:
            xnew = x - fn(x)/dfn(x)
        except ZeroDivisionError:
            x = x+1
        if abs(xnew-x)/x < tol: break
        x = xnew
    return x, i

#Getting expression
x = Symbol('x')
funcao = input('Entre com a equação da tensão desejada: ')
try:
    y = lambda x: eval(funcao)  #transforms a string into a python math expression
    dy = lambdify(x,diff(funcao),'numpy') #takes the derivative of the expression
except:
    exit("Há um erro na sua expressão! Revise-a!") #Error when reading expression
resultado, iterations = nraphson(y,dy,1)

#Printing
os.system('cls' if os.name == 'nt' else 'clear')
print('Resultado encontrado após %d iterações: %.4f' % (iterations, round(resultado,4)))
