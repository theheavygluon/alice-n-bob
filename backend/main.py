from typing import Optional
import os
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import subprocess
from fastapi import File, UploadFile, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenData(BaseModel):
    bit: str
    basis: str
    email: str
    protocol: str
    


def execute_code(source_code, language_id=71, stdin=None):
    URL = "http://18.219.240.65/submissions"

    querystring = {"base64_encoded": "false",
                   "wait": "true",
                   "fields": "stdout,time,memory,stderr,token,compile_output,message,status"}

    payload = {
        "language_id": language_id,
        "source_code": source_code,
        "stdin": stdin,
    }
    headers = {
        'content-type': "application/json",
    }

    response = requests.request("POST", URL, data=json.dumps(payload), headers=headers, params=querystring)
    return response.json()



@app.post("/")
async def index(item: TokenData):
    print(item.bit, item.basis, item.email, item.protocol)
    source_code = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"""\nCreated on Sat Jan 29 13:57:51 2022\nBB84: For the iQuHack \n@author: alejomonbar\n"""\nimport numpy as np\nfrom qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer\nfrom qiskit import Aer\nfrom qiskit.visualization import plot_histogram\n#from quantuminspire.qiskit import QI\n\n# email, pasword = "ja.montanezbarrera@ugto.mx", "YZYKHjC6I4c7hUpTyIAo"\n# QI.set_authentication_details(email=email, password=pasword)\n# backend = QI.get_backend(\'QX single-node simulator\')\n\nmorse = { \'a\':\'.-\', \'b\':\'-...\',\'c\':\'-.-.\', \'d\':\'-..\', \'e\':\'.\', \n         \'f\':\'..-.\', \'g\':\'--.\', \'h\':\'....\', \'i\':\'..\', \'j\':\'.---\', \'k\':\'-.-\', \n         \'l\':\'.-..\', \'m\':\'--\', \'n\':\'-.\', \'o\':\'---\', \'p\':\'.--.\', \'q\':\'--.-\', \n         \'r\':\'.-.\', \'s\':\'...\', \'t\':\'-\', \'u\':\'..-\', \'v\':\'...-\', \'w\':\'.--\', \n         \'x\':\'-..-\', \'y\':\'-.--\', \'z\':\'--..\', \'1\':\'.----\', \'2\':\'..---\', \'3\':\'...--\', \n         \'4\':\'....-\', \'5\':\'.....\', \'6\':\'-....\', \'7\':\'--...\', \'8\':\'---..\', \'9\':\'----.\', \n         \'0\':\'-----\', \', \':\'--..--\', \'.\':\'.-.-.-\', \'?\':\'..--..\', \'/\':\'-..-.\', \'-\':\'-....-\', \n         \'(\':\'-.--.\', \')\':\'-.--.-\'} \n\nbackend = Aer.get_backend("aer_simulator")\n\ndef Alice(n, key=[], basis=[]):\n    qr = QuantumRegister(n, name=\'qr\')\n    cr = ClassicalRegister(n, name=\'cr\')\n    \n    circuit = QuantumCircuit(qr, cr, name=\'Alice\')\n    if len(key) == 0:\n        key = np.binary_repr(np.random.randint(0, high=2**n) , n)\n    \n    for index, digit in enumerate(key):\n        if digit == \'1\':\n            circuit.x(qr[index])\n    \n    if len(basis) == 0:\n        for index in range(n):\n            if 0.5 < np.random.random():  \n                circuit.h(qr[index]) \n                basis.append(\'X\')\n            else:\n                basis.append(\'Z\') \n    else:\n        for index, i in enumerate(basis):\n            if i == "X":\n                circuit.h(qr[index])\n    return circuit, basis, key\n\n\ndef Bob(n, basis=[]):\n    qr = QuantumRegister(n, name=\'qr\')\n    cr = ClassicalRegister(n, name=\'cr\')\n    circuit = QuantumCircuit(qr, cr, name=\'Bob\')\n    \n    if len(basis) == 0:\n        for index in range(n):\n            if 0.5 < np.random.random():  \n                circuit.h(qr[index]) \n                basis.append(\'X\')\n            else:\n                basis.append(\'Z\') \n    else:\n        for index, i in enumerate(basis):\n            if i == "X":\n                circuit.h(qr[index])\n    return circuit, basis \n\n\ndef interface(alice_cir, bob_circ, intruder=False):\n    "This is what the interface should do."\n    n = alice_cir.num_qubits\n    circuit = alice_cir\n    if intruder: # Eve is trying to read the key?\n        circuit.measure(range(n), range(n))\n    circuit = circuit.compose(bob_circ)\n    circuit.measure(range(n), range(n))\n    result = backend.run(circuit, shots=1).result().get_counts()\n    return list(result)[0][::-1]\n\ndef get_shared_key(basis_alice, basis_bob, key):\n    n = len(basis_alice)\n    new_key = ""\n    for _ in range(n):\n        if basis_alice[_] == basis_bob[_]:\n            new_key += key[_]\n    return new_key\n\ndef encode_message(message, key):\n    bin_message = message_to_bin(message)\n    n = len(key)\n    l = len(bin_message)\n    div_message = [bin_message[i:i+n] for i in range(0, l, n)]\n    encoded_message = ""\n    for m in div_message:\n        for j, k in enumerate(m):\n            if k == key[j]:\n                encoded_message += "0"\n            else:\n                encoded_message += "1"\n    return encoded_message\n\ndef decode_message(bin_message, key):\n    n = len(key)\n    l = len(bin_message)\n    div_message = [bin_message[i:i+n] for i in range(0, l, n)]\n    decoded_message = ""\n    for m in div_message:\n        for j, k in enumerate(m):\n            if k == key[j]:\n                decoded_message += "0"\n            else:\n                decoded_message += "1"\n    decoded_message = bin_to_message(decoded_message)\n    return decoded_message\n\ndef morse_to_bin(m):\n    bin_ = ""\n    for i in m:\n        if i == ".":\n            bin_ += "1"\n        elif i == "-":\n            bin_ += "11"\n        bin_ += "0"\n    bin_ += "0"\n    return bin_\n\ndef bin_to_morse(bin_message):\n    bin_message = bin_message.split("00")\n    message = []\n    for lett in bin_message:\n        lett = lett.split("0")\n        morse_ = ""\n        for char in lett:\n            if char == "11":\n                morse_ += "-"\n            elif char == "1":\n                morse_ += "."\n        message.append(morse_)\n    return message\n\ndef morse_to_string(morse_message):\n    message = ""\n    for lett in morse_message:\n        try:\n            message += list(morse.keys())[list(morse.values()).index(lett)]\n        except:\n            pass\n    return message\n    \ndef message_to_bin(message):\n    binary_mess = ""\n    for char in message:\n        m = morse[char]\n        binary_mess += morse_to_bin(m)\n    return binary_mess[:-2]\n\ndef bin_to_message(bin_message):\n    morse = bin_to_morse(bin_message)\n    return morse_to_string(morse)\n\ndef check_intruder(part_key_bob, part_key_alice):\n    n = len(part_key_bob)\n    for i in range(n):\n        if part_key_alice[i] != part_key_bob[i]:\n            print("Someone is trying to access the key!")\n            return\n    print(f"The probability that someone is accessing the info is {np.round(100*(3/4)**n,3)}%")\n\n\n\n\n\n\nn = len(str('+str(item.bit)+'))\nalice, basis_alice, key_alice = Alice(n, str('+str(item.bit)+'), list('+str(item.basis)+'))\nbob, basis_bob = Bob(n)\n\nkey_bob = interface(alice, bob, intruder=False)\nnew_key_bob = get_shared_key(basis_alice, basis_bob, key_bob)\nnew_key_alice = get_shared_key(basis_alice, basis_bob, key_alice)\nprint(f"Alice basis: {basis_alice}")\nprint(f"Bob   basis: {basis_bob}")\nprint(f"key Bob old   {key_bob}")\nprint(f"key Alice old {key_alice}")\nprint(f"key Bob new  {new_key_bob}")\nprint(f"key Alice new {new_key_alice}")\n\nbin_message = message_to_bin("qiskit")\nprint(bin_message)\nmessage_encoded = encode_message("qiskit", new_key_alice)\nprint(message_encoded)\nmessage_decoded = decode_message(message_encoded, new_key_bob)\nprint(message_decoded)\ncheck_intruder(new_key_alice[:6], new_key_bob[:6])\n\n\n\nimport smtplib\n\ngmail_user = \'EMAIL HERE\'\ngmail_password = \'PASSWORD HERE\'\n\nsent_from = gmail_user\nto = [\'programmer3.7@outlook.com\']\nsubject = \'Hi Bob\'\nbody = \'Hi bob, this is alice. Heres the info you need: \\n\', "My Basis:" + str(basis_alice) +"\\n Your Basis (Auto-generated):" + str(basis_bob) + "\\n Your Key: " + str(key_bob) + "\\n See you on the other end (Hopefully without eve this time)!"\n\nemail_text = """\\\nFrom: %s\nTo: %s\nSubject: %s\n\n%s\n""" % (sent_from, ", ".join(to), subject, body)\n\ntry:\n    smtp_server = smtplib.SMTP_SSL(\'smtp.gmail.com\', 465)\n    smtp_server.ehlo()\n    smtp_server.login(gmail_user, gmail_password)\n    smtp_server.sendmail(sent_from, to, email_text)\n    smtp_server.close()\n    print ("Email sent successfully!")\nexcept Exception as ex:\n    print ("Something went wrong….",ex)\n\n'
    a = execute_code(source_code)
    print(a)
    return a 






