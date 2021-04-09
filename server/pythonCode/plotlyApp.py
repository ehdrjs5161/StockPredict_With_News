import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from collections import OrderedDict
import plotly_express as px
from dash.dependencies import Output, Input
from server.pythonCode import DB_Handler

def get_price(code, name):
    temp = mongo.find_item(condition={"code":"{}".format(code)}, db_name="stockPredict", collection_name="price")
    result = pd.DataFrame(temp['price'])[['Date', 'Close']]
    result = result.rename({"Date": "Date", 'Close': '{}'.format(name)}, axis="columns")
    return result

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
#
#     result = mongo.find_item(condition={"code": "{}".format(code)}, db_name="stockPredict", collection_name="price")
#     result = pd.DataFrame(result['price'])[['Date', 'Close']]
#     result = result.rename({"Date": "Date", 'Close': '{}'.format(name)}, axis="columns")

# def generate_table(dataframe, max_rows=100):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H1("StockPredict"),
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
    result = mongo.find_item(condition={"code": "{}".format(dropdown)}, db_name="stockPredict", collection_name="price")
    result = pd.DataFrame(result['price'])[['Date', 'Close']]
    result = result.rename({"Date": "Date", 'Close': '{}'.format(dropdown)}, axis="columns")
    fig = px.line(result, x='Date', y=dropdown)
    fig.update_layout(
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
            type="date"
        )
    )
    return fig
# def update_graph(dropdwon_properties):
#     selected_value = dropdwon_properties['value']
#     temp = mongo.find_item(condition={"code": "{}".format(selected_value)}, db_name="stockPredict", collection_name="price")
#     result = pd.DataFrame(temp['price'])[['Date', 'Close']]
#
#     return {
#         'figure': go.Figure(
#             data=[
#                 go.Scatter(x=result.index,
#                         y=result.Close,
#                         name=selected_value)
#             ]
#         )
#     }

if __name__ == "__main__":
    app.run_server(debug=True)