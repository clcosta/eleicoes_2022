import requests
import json
import pandas as pd
from datetime import datetime
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

app = Dash(__name__)

imgs = {
    "LULA": "https://arte.estadao.com.br/public/pages/rm/jo/x2/gz/v2/34/draft/Icone_Lula.png",
    "JAIR BOLSONARO": "https://arte.estadao.com.br/public/pages/rm/jo/x2/gz/v2/34/draft/Icone_Bolsonaro.png",
}


def resultado_do_tse():
    try:
        data = requests.get(
            "https://resultados.tse.jus.br/oficial/ele2022/545/dados-simplificados/br/br-c0001-e000545-r.json"
        )
    except:
        return pd.DataFrame(columns=["Candidato", "Nº de Votos", "Porcentagem"])
    json_data = json.loads(data.content)

    candidato = []
    votos = []
    porcentagem = []

    for informacoes in json_data["cand"]:

        candidato.append(informacoes["nm"])
        votos.append(informacoes["vap"])
        porcentagem.append(informacoes["pvap"])

    df_eleicao = pd.DataFrame(
        list(zip(candidato, votos, porcentagem)),
        columns=["Candidato", "Nº de Votos", "Porcentagem"],
    )
    return df_eleicao


def grafico():
    df = resultado_do_tse()
    if int(df["Nº de Votos"].values.any()) > 0:
        # fig = px.pie(df, names="Candidato", values="Nº de Votos")
        fig = px.bar(df[::-1],x="Candidato", y="Nº de Votos")
        return fig
    else:
        fig = px.bar(df[::-1], x="Candidato", y="Nº de Votos")
        return fig


def hora_atual():
    return datetime.now().strftime("%H:%M:%S")


def candidato_na_frente():
    df = resultado_do_tse()
    if not int(df["Nº de Votos"].values.any()) > 0:
        return html.Div(
            children=[
                html.H2("Os votos ainda não foram contabilizados."),
                html.Br(),
                html.A(
                    "Você pode se informar mais no site do TSE.",
                    href="https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/resultados",
                    target="__blank",
                ),
            ],
            style={"display": "block", "padding": "15px"},
        )
    candidato = df[0:1]["Candidato"].values.tolist()
    candidato = candidato[0] if candidato else "TSE"
    return html.Div(
        children=[
            html.Img(src=imgs[candidato], alt=candidato, width=250, height=250),
            html.H4(candidato),
        ],
        style={"display": "block", "padding": "10px"},
    )


def layout():
    return html.Div(
        children=[
            html.H1("Eleições 2022 em tempo Real"),
            html.Div(
                id="lideranca",
                children=[
                    html.H3("Candidato na liderança:"),
                    candidato_na_frente(),
                ],
            ),
            html.Div(
                children=[
                    html.Legend(
                        children=[
                            f"Última atualização às: ",
                            html.B(f"{hora_atual()}"),
                        ],
                        id="atualizacao",
                    ),
                    dcc.Graph("grafico-eleicoes", figure=grafico()),
                    html.Button("Atualizar", id="btn-update", n_clicks=0),
                ]
            ),
        ]
    )


app.layout = layout


@app.callback(
    Output(component_id="grafico-eleicoes", component_property="figure"),
    Input(component_id="btn-update", component_property="n_clicks"),
)
def atualizar_grafico(click):
    return grafico()


@app.callback(
    Output(component_id="lideranca", component_property="children"),
    Input(component_id="btn-update", component_property="n_clicks"),
)
def atualizar_lideranca(click):
    return [html.H3("Candidato na liderança:"), candidato_na_frente()]


@app.callback(Output("atualizacao", "children"), Input("btn-update", "n_clicks"))
def atualizar_legend(click):
    return [f"Última atualização às: ", html.B(f"{hora_atual()}")]


if __name__ == "__main__":
    app.run_server(debug=True)
