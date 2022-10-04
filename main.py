import requests
import json
import pandas as pd
from datetime import datetime
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

app = Dash(__name__)

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

def grafico_pizza():
    df = resultado_do_tse()
    fig = px.pie(df,names='Candidato', values='Nº de Votos')
    return fig

def hora_atual():
    return datetime.now().strftime('%H:%M:%S')

def layout():
    return html.Div(
        children=[
            html.H1("Eleições 2022 em tempo Real"),
            html.Legend(children=[f"Última atualização às: ",html.B(f"{hora_atual()}")], id="atualizacao"),
            dcc.Graph('grafico-eleicoes', figure=grafico_pizza()),
            html.Button('Atualizar', id="btn-update", n_clicks=0)
        ]
    )

app.layout = layout

@app.callback(
    Output("grafico-eleicoes", 'figure'),
    Input('btn-update', 'n_clicks')
)
def atualizar_grafico(click):
    "Atualizado às: "
    return grafico_pizza()

@app.callback(
    Output("atualizacao", 'children'),
    Input('btn-update', 'n_clicks')
)
def atualizar_legend(click):
    return [f"Última atualização às: ",html.B(f"{hora_atual()}")]

if __name__ == '__main__':
    app.run_server(debug=True)