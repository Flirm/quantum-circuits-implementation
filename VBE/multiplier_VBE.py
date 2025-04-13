from qiskit import *
from utils.helpers import *

#contrlled modular multiplication proposed by Vedral, Barenco and Erkert
#given a fixed a and N, does the following effect
#|c;x,0> ->  -{ |c;x,a*x mod N> if |c>==|1>
#            \{ |c;x,x>         if |c>==|0> 
def c_mult_mod_VBE(num_buqits: int):
    return