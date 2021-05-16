import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd
from collections import OrderedDict
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from pythonCode import DB_Handler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

mongo = DB_Handler.DBHandler()
kospi = mongo.client.get_database("stockpredict").code
kospi = pd.DataFrame(kospi.find())[['code', 'name']]

options = []
result = result = mongo.client.get_database("stockpredict").predictResult
result = pd.DataFrame(result.find())[['code', 'name', 'predict', 'rate']]
result.columns = ['종목코드', '기업명', '예측 종가(KRW)', '전일 대비(%)']

for code, name in zip(kospi['code'], kospi['name']):
    temp = OrderedDict()
    temp['label'] = name
    temp['value'] = code
    options.append(temp)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_table(frame):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in frame.columns])),
        html.Tbody([
            html.Tr([
                html.Td(frame.iloc[i][col]) for col in frame.columns
            ], style={"width": "10%"}) for i in range(min(len(frame), len(frame)))
        ])
    ],
    )

app.layout = html.Div(
    style={
        "margin-top": "20px",
        "margin-left": "50px",
        "gap": "20px",
        "display": "flex"},
    children=[
        html.Div(style={"width": "500px"},
                 children=[
                     html.H1('Stock Predict'),
                     html.P("딥러닝을 이용한 뉴스 데이터 기반 주가 예측 프로그램"),
                     dcc.Dropdown(id="dropdown",
                                  options=options,
                                  value=options[0]['value'],
                                  clearable=False, style={"margin-bottom": "30px"}),

                     html.Div(dash_table.DataTable(id='current',
                                                   columns=[{"name": i, "id": i} for i in result.columns],
                                                   data=None,
                                                   style_as_list_view=True,
                                                   style_cell={'textAlign': 'left'},
                                                   style_header={"fontWeight": 'bold'}), style={"margin-bottom": "30px"}),
                     html.Div(dash_table.DataTable(id='datatable-paging',
                                                   columns=[{"name": i, "id": i} for i in result.columns],
                                                   data=result.to_dict('records'),
                                                   page_size=20,
                                                   style_as_list_view=True,
                                                   style_cell={'textAlign': 'left'},
                                                   style_header={"fontWeight": 'bold'},
                                                   ))
                 ]),
        html.Div(style={"width": "1500px"},
                 children=[
                     html.H1("TEST Accuracy",
                             style={"textAlign": "center",
                                    "margin-top": "20px",
                                    "font-size": "25px"}),
                     dcc.Graph(id="Stock_Graph",
                               style={"margin-top": "-20px",
                                      "height": "930px"})
                 ])
    ])

@app.callback(
    Output("Stock_Graph", "figure"),
    [Input("dropdown", "value")])
def show_graph(dropdown):
    result = mongo.find_item(condition={"code": "{}".format(dropdown)}, db_name="stockpredict",
                             collection_name="testResult")
    result = pd.DataFrame(result['price'])[['Date', 'Actual_Price', 'Predict_Price']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result['Date'], y=result['Predict_Price'],
                             mode='lines', name='Predict'))
    fig.add_trace(go.Scatter(x=result['Date'], y=result['Actual_Price'],
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


@app.callback(
    Output("current", "data"),
    [Input("dropdown", "value")])
def price_info(dropdown):
    isdropdown = result['종목코드'] == dropdown
    return result[isdropdown].to_dict("records")

# @app.callback(
#     Output('datatable-paging', 'data'),
#     Input('datatable-paging', "page_current"),
#     Input('datatable-paging', "page_size"))
# def update_table(page_current, page_size):
#     return result.iloc[
#         page_current*page_size:(page_current+ 1)*page_size
#     ].to_dict('records')
# @app.callback(
#     Output("predict_result", "figure"),
#     [Input("dropdown", "value")])
# def predict_result(dropdown):
#     isnotdropdown = result['종목코드'] != dropdown
#     fig = ff.create_table(result[isnotdropdown])
#     return fig

if __name__ == "__main__":
    app.run_server(debug=True)
