#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 20:10:24 2022
E91: For the iQuHack
@author: Lucas Arenstein
refs: Ekert, Artur K. "Quantum cryptography based on Bell's theorem" - 1991
      https://github.com/kardashin/E91_protocol/blob/master/E91_tutorial/E91_tutorial.ipynb
"""



import sys

import random
import math
import re #regexp module

from qiskit import QuantumCircuit, execute, Aer, QuantumRegister, ClassicalRegister

from qiskit.visualization import plot_histogram


#First qubit Alice, second qubit Bob
#Classical Register (Cr): Alice = Cr[0], Bob = Cr[1], Eve = Cr[2,3]


def initial_setup():
    qr = QuantumRegister(2)
    cr = ClassicalRegister(4)
    
    ## Alice's measurement circuits
    
    # measure the spin projection of Alice's qubit onto the a_1 direction (X basis)
    measureA1 = QuantumCircuit(2,4)
    measureA1.h(0)
    measureA1.measure(0,0)
    
    # measure the spin projection of Alice's qubit onto the a_2 direction (W basis)
    measureA2 = QuantumCircuit(2,4)
    measureA2.s(0)
    measureA2.h(0)
    measureA2.t(0)
    measureA2.h(0)
    measureA2.measure(0,0)
    
    # measure the spin projection of Alice's qubit onto the a_3 direction (standard Z basis)
    measureA3 = QuantumCircuit(2,4)
    measureA3.measure(0,0)
    
    ## Bob's measurement circuits
    
    # measure the spin projection of Bob's qubit onto the b_1 direction (W basis)
    measureB1 = QuantumCircuit(2,4)
    measureB1.s(1)
    measureB1.h(1)
    measureB1.t(1)
    measureB1.h(1)
    measureB1.measure(1,1)
    
    # measure the spin projection of Bob's qubit onto the b_2 direction (standard Z basis)
    measureB2 = QuantumCircuit(2,4)
    measureB2.measure(1,1)
    
    # measure the spin projection of Bob's qubit onto the b_3 direction (V basis)
    measureB3 = QuantumCircuit(2,4)
    measureB3.s(1)
    measureB3.h(1)
    measureB3.tdg(1)
    measureB3.h(1)
    measureB3.measure(1,1)
    
    ## Lists of measurement circuits
    aliceMeasurements = [measureA1, measureA2, measureA3]
    bobMeasurements = [measureB1, measureB2, measureB3]
    
    #Alice and Bob record the results of their measurements as bits of the strings a and a'
    abPatterns = [
        re.compile('..00$'), # search for the '..00' output (Alice obtained -1 and Bob obtained -1)
        re.compile('..01$'), # search for the '..01' output
        re.compile('..10$'), # search for the '..10' output (Alice obtained -1 and Bob obtained 1)
        re.compile('..11$')  # search for the '..11' output
    ]

    
    return aliceMeasurements, bobMeasurements, abPatterns
# # # # #

# Supose Alice and Bob want to generate a secret key using N singlet states prepared by Charlie.


#The participants must choose the directions onto which they will measure the spin projections of their qubits. 
#To do this, Alice and Bob create the strings b and b' with randomly generated elements.

# Now we combine Charlie's device and Alice's and Bob's detectors into one circuit (singlet + Alice's measurement + Bob's measurement).


def run_circuits(numberOfSinglets, aliceMeasurements, bobMeasurements):
    
    aliceMeasurementChoices = [random.randint(1, 3) for i in range(numberOfSinglets)] # string b of Alice
    bobMeasurementChoices = [random.randint(1, 3) for i in range(numberOfSinglets)] # string b' of Bob

    circuits = [] # the list in which the created circuits will be stored
                  # circuitname,gen_circuit,circuitname,gen_circuit....
                  # gen_circuit
    circuitsNames = []    
    
    for i in range(numberOfSinglets):
        # create the name of the i-th circuit depending on Alice's and Bob's measurement choices
        circuitName = str(i) + ':A' + str(aliceMeasurementChoices[i]) + '_B' + str(bobMeasurementChoices[i])
        
        # create the joint measurement circuit
        # add Alice's and Bob's measurement circuits to the singlet state circuit
        gen_circuit = QuantumCircuit(2, 4)
    
        gen_circuit.x(0)
        gen_circuit.x(1)
        gen_circuit.h(0)
        gen_circuit.cx(0,1)
        
        gen_circuit.compose(aliceMeasurements[aliceMeasurementChoices[i]-1], inplace=True)
        
        gen_circuit.compose(bobMeasurements[bobMeasurementChoices[i]-1], inplace=True)
        
        circuitsNames.append(circuitName)
        circuits.append(gen_circuit)

    backend = Aer.get_backend('statevector_simulator')
    results = execute(circuits,backend, shots=1).result().get_counts()
    
    return aliceMeasurementChoices, bobMeasurementChoices, results

#print(circuits[0])
#0:A2_B3
#print(circuits[2])
#1:A2_B3
#It tells us about the number of the singlet state received from Charlie, 
#and the measurements applied by Alice and Bob.
#etc.



def build_key(results, aliceMeasurementChoices, bobMeasurementChoices, abPatterns):
    
    aliceResults = [] # Alice's results (string a)
    bobResults = [] # Bob's results (string a')
    
    for i in range(len(results)):
    
        #res = list(results.get_counts(circuitsNames[i]).keys())[0] # extract the key from the dict and transform it to str; execution result of the i-th circuit
        
        res = list(results[i])[0]
        
        if abPatterns[0].search(res): # check if the key is '..00' (if the measurement results are -1,-1)
            aliceResults.append(-1) # Alice got the result -1 
            bobResults.append(-1) # Bob got the result -1
        if abPatterns[1].search(res):
            aliceResults.append(1)
            bobResults.append(-1)
        if abPatterns[2].search(res): # check if the key is '..10' (if the measurement results are -1,1)
            aliceResults.append(-1) # Alice got the result -1 
            bobResults.append(1) # Bob got the result 1
        if abPatterns[3].search(res): 
            aliceResults.append(1)
            bobResults.append(1)
            

    aliceKey = [] # Alice's key string k
    bobKey = [] # Bob's key string k'


    # comparing the stings with measurement choices
    for i in range(len(results)):
        # if Alice and Bob have measured the spin projections onto the a_2/b_1 or a_3/b_2 directions
        if (aliceMeasurementChoices[i] == 2 and bobMeasurementChoices[i] == 1) or (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 2):
            aliceKey.append(aliceResults[i]) # record the i-th result obtained by Alice as the bit of the secret key k
            bobKey.append(- bobResults[i]) # record the multiplied by -1 i-th result obtained Bob as the bit of the secret key k'
            
    keyLength = len(aliceKey) # length of the secret key


    abKeyMismatches = 0 # number of mismatching bits in Alice's and Bob's keys
    
    for j in range(keyLength):
        if aliceKey[j] != bobKey[j]:
            abKeyMismatches += 1

    return keyLength, abKeyMismatches, aliceKey



# function that calculates CHSH correlation value
def chsh_corr(results, aliceMeasurementChoices, bobMeasurementChoices, abPatterns):
    
    # lists with the counts of measurement results
    # each element represents the number of (-1,-1), (-1,1), (1,-1) and (1,1) results respectively
    countA1B1 = [0, 0, 0, 0] # XW observable
    countA1B3 = [0, 0, 0, 0] # XV observable
    countA3B1 = [0, 0, 0, 0] # ZW observable
    countA3B3 = [0, 0, 0, 0] # ZV observable

    for i in range(len(results)):

        res = list(results[i])[0]


        # if the spins of the qubits of the i-th singlet were projected onto the a_1/b_1 directions
        if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 1):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA1B1[j] += 1

        if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 3):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA1B3[j] += 1

        if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 1):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA3B1[j] += 1
                    
        # if the spins of the qubits of the i-th singlet were projected onto the a_3/b_3 directions
        if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 3):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA3B3[j] += 1
                    
    # number of the results obtained from the measurements in a particular basis
    total11 = sum(countA1B1)
    total13 = sum(countA1B3)
    total31 = sum(countA3B1)
    total33 = sum(countA3B3)      
                    
    # expectation values of XW, XV, ZW and ZV observables (2)
    expect11 = (countA1B1[0] - countA1B1[1] - countA1B1[2] + countA1B1[3])/total11 # -1/sqrt(2)
    expect13 = (countA1B3[0] - countA1B3[1] - countA1B3[2] + countA1B3[3])/total13 # 1/sqrt(2)
    expect31 = (countA3B1[0] - countA3B1[1] - countA3B1[2] + countA3B1[3])/total31 # -1/sqrt(2)
    expect33 = (countA3B3[0] - countA3B3[1] - countA3B3[2] + countA3B3[3])/total33 # -1/sqrt(2) 
    
    corr = expect11 - expect13 + expect31 + expect33 # calculate the CHSC correlation value (3)
    
    return corr



#If C = -2*sqrt(2), then Alice and Bob can be sure that the states they had been receiving from Charlie were entangled indeed. 
#This fact tells the participants that there was no interference in the quantum channel.



#n is the desired lenght of the Key Alice and Bob want to generate

def main(n):
    
    if n<10:
        return print("Too few digits to distribute, try at least a 10")
    
    #Obtain this result after a series of simulations
    lower_bound_singlets = 8*n
    
    aliceMeasurements, bobMeasurements, abPatterns = initial_setup()
    
    aliceMeasurementChoices, bobMeasurementChoices, results = run_circuits(lower_bound_singlets, aliceMeasurements, bobMeasurements)
    
    keyLength, abKeyMismatches, CommonKey = build_key(results, aliceMeasurementChoices, bobMeasurementChoices, abPatterns)
    
    corr = chsh_corr(results, aliceMeasurementChoices, bobMeasurementChoices, abPatterns)
    
    #Print Results:
    print('CHSH correlation value: ' + str(round(corr, 3)))
    print('Length of the key: ' + str(keyLength))
    print('Number of mismatching bits: ' + str(abKeyMismatches) + '\n')
    
    
    print('All the key', CommonKey)
    print('Key to distribute', CommonKey[:n])
    return CommonKey[:n]


#To run using a IDE
#just run everything from line 1 to here  and call the function main
#with your desired input, that is the lenght of the Key Alice and Bob want to create
#> main(n)



#To run in the terminal
#python3 E91_local.py n
if __name__ == "__main__":
    n = int(sys.argv[1])
    main(n)
    
