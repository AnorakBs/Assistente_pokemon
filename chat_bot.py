import numpy as np
import json
import codecs
import time
import requests
import os
from IPython.display import clear_output
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

with open('pkmn_dict.json','r',encoding='utf-8') as f:
    pkmn_dict = json.load(f)

with open('tipo_pkmn.json','r',encoding='utf-8') as f:
    tipo_pkmn = json.load(f)
    
url_pokedex = ('https://pokemondb.net/pokedex/all')

def calculo_mult_tipos(tipo_pkmn,tipo_1,tipo_2):
    calc_vec_tipo_1 = np.zeros(len(tipo_pkmn),dtype =np.float32)
    calc_vec_tipo_2 = np.zeros(len(tipo_pkmn),dtype =np.float32)
    for idx, w in enumerate(tipo_pkmn):
        
        if w in pkmn_dict[tipo_1][0]:
          calc_vec_tipo_1[idx] = calc_vec_tipo_1[idx] - 1
        if w in pkmn_dict[tipo_1][2]:
          calc_vec_tipo_1[idx] = calc_vec_tipo_1[idx] + 1 
        if w in pkmn_dict[tipo_1][3]:
          calc_vec_tipo_1[idx] = calc_vec_tipo_1[idx] + 100

        if w in pkmn_dict[tipo_2][0]:
            calc_vec_tipo_2[idx] = calc_vec_tipo_2[idx] - 1
        if w in pkmn_dict[tipo_2][2]:
          calc_vec_tipo_2[idx] = calc_vec_tipo_2[idx] + 1
        if w in pkmn_dict[tipo_2][3]:
          calc_vec_tipo_2[idx] = calc_vec_tipo_2[idx] + 100

        calc_vec = np.add(calc_vec_tipo_1,calc_vec_tipo_2)
    return calc_vec

def call_api(nome_pkmn):
    resposta = requests.get(f'https://pokeapi.co/api/v2/pokemon/{nome_pkmn}')
    if resposta.status_code == 200:
        x = resposta.json()
        x = x['types']
        tipos = []
        for i in range(len(x)):
            tipos.append(x[i]['type']['name']) 
        return tipos
    else:
        return 'erro'

def norm_user_input(user_input):
    texto = user_input.lower()
    return user_input.lower()



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root(txt: str):
    
    msgArray = []
    nome_pkmn = norm_user_input(txt)
    
    tipos = call_api(nome_pkmn)

    if tipos == 'erro':
        
        url_pokedex = 'https://pokemondb.net/pokedex/all'
        msgArray.append('Não conheço esse pokemon')
        msgArray.append(f'Clique nesse link para ver a pokedex e procurar pelo nome correto do pokemon: {url_pokedex}')
        return msgArray
    if len(tipos) > 1:
        tipo_1 = tipos[0]
        tipo_2 = tipos[1]

        neg = []
        efetivo_2x = []
        efetivo_4x = []
        imunidade = []

        func = calculo_mult_tipos(tipo_pkmn,tipo_1,tipo_2)

        for idx, w in enumerate(func):
            if w < 0 or w > 90:
                neg.extend([[tipo_pkmn[idx],w]])
        for x,y in neg:
            if y == -1:
                efetivo_2x.append(x)
            if y <= -2:
                efetivo_4x.append(x)
            if y > 90:
                imunidade.append(x)

        if len(efetivo_2x) > 1:
            tipos_2x = ', '.join(efetivo_2x)
            msgArray.append(f'O pokemon toma super efetivo 2x dos tipos: {tipos_2x}')
        else:
            msgArray.append(f'O pokemon toma super efetivo 2x do tipo: {efetivo_2x[0]}')

        if len(efetivo_4x) > 1:
            tipos_4x = ', '.join(efetivo_4x)
            msgArray.append(f'O pokemon toma super efetivo 4x dos tipos: {tipos_4x}')
        elif len(efetivo_4x) == 1:

            msgArray.append(f'O pokemon toma super efetivo 4x do tipo: {efetivo_4x[0]}')

        if len(imunidade) == 1:
            msgArray.append(f'O pokemon é imune ao tipo: {imunidade[0]}')
        elif len(imunidade) > 1:
            imunidades = ', '.join(imunidade)
            msgArray.append(f'O pokemon é imune aos tipos: {imunidades}')


    if len(tipos) == 1:
        tipo = tipos[0]
        melhores_tipo = ', '.join(pkmn_dict[tipo][0])
        imunidade = ', '.join(pkmn_dict[tipo][3])

        msgArray.append(f'Tipos que dão super efetivo contra {tipo}: {melhores_tipo}')

        if imunidade != '':

            msgArray.append(f'Tipos que {tipo} tem imunidade: {imunidade}')


    return {"mensagens": msgArray}
            



