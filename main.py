import requests
import json
import pandas as pd
from datetime import datetime
from rocketry import Rocketry
from rocketry.conds import every

scheduler = Rocketry(execution="async")

def resultado_do_tse():
    try:
        data = requests.get(
            'https://resultados.tse.jus.br/oficial/ele2022/544/dados-simplificados/br/br-c0001-e000544-r.json'
        )
    except:
        return pd.DataFrame(columns=[
            'Candidato', 'Nº de Votos', 'Porcentagem'
        ])
    json_data = json.loads(data.content)

    candidato = []
    votos = []
    porcentagem = []

    for informacoes in json_data['cand']:
        
        candidato.append(informacoes['nm'])
        votos.append(informacoes['vap'])
        porcentagem.append(informacoes['pvap'])
            
    df_eleicao = pd.DataFrame(list(zip(candidato, votos, porcentagem)), columns = [
        'Candidato', 'Nº de Votos', 'Porcentagem'
    ])
    return df_eleicao

@scheduler.task(every('30 seconds'), execution="async")
def mostrar_resultado_no_terminal():
    df_eleicao = resultado_do_tse()
    print(f"\nResultado às: {datetime.now().strftime('%H:%M:%S')}\n", "*"*50)
    print(df_eleicao)

if __name__ == '__main__':
    scheduler.run()