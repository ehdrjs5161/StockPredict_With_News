import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from collections import OrderedDict
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from server.pythonCode import DB_Handler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

mongo = DB_Handler.DBHandler()
kospi = mongo.find_items(db_name="stockPredict", collection_name="code")
kospi = pd.DataFrame(kospi)[['code', 'name']]
options = []

for code, name in zip(kospi['code'], kospi['name']):
    temp=OrderedDict()
    temp['label'] = name
    temp['value'] = code
    options.append(temp)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Stock Predict With News"),
    dcc.Dropdown(id="dropdown",
                 options=options,
                 value=options[0]['value'],
                 clearable=False,
                 ),
    dcc.Graph(id="Stock_Graph"),
])

@app.callback(
    Output("Stock_Graph", "figure"),
    [Input("dropdown", "value")])
def show_graph(dropdown):
    result = mongo.find_item(condition={"code": "{}".format(dropdown)}, db_name="stockPredict", collection_name="testResult")
    result = pd.DataFrame(result['result'])[['Date', 'Price', 'Predict']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result['Date'], y=result['Predict'],
                             mode='lines', name='Predict'))
    fig.add_trace(go.Scatter(x=result['Date'], y=result['Price'],
                             mode='lines', name='Price'))
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
        )
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)