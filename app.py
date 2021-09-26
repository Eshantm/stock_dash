import dash 
from dash import dcc
from dash import html
from datetime import datetime as dt 
import yfinance as yf
import pandas as pd 
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from model import prediction
from sklearn.svm import SVR

app=dash.Dash(__name__)
server = app.server

def get_stock_price_fig(df):

    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")

    return fig
  
def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

app.layout = html.Div([
          html.Div(
          [
            html.P("Welcome to the Stock Dash App!", className="start"),
            html.Div([
                    html.P("Input stock code: "),
                    html.Div([
                        dcc.Input(id="stock_input", type="text"),
                        html.Button("Submit", id='submit'),
                    ],
                             className="form")
                ],
                         className="stock_code"),
            html.Div([
                dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=dt.now(),
                initial_visible_month=dt.now(),
                end_date=dt.now().date()),
                       
                
              # Date range picker input
            ],className="date_range"),
            html.Div([
              # Stock price button
              html.Button('Stock Price', id='stock_price'),
              # Indicators button
              html.Button('Indicators', id='indicators'),
              # Number of days of forecast input
              dcc.Input(
                id="input_days",
                type="text",  
                placeholder="   Number of days"),
              # Forecast button
              html.Button('Forecast', id='forecast'),
            ],className="buttons"),
          ],
        className="nav"),

html.Div(
          [
            html.Div(
                  [  # Logo
                     html.Img(id="logo"),
                     html.P(id="ticker")
                    # Company Name
                  ],
                className="header"),
            html.Div( #Description
              id="description", className="decription_ticker"),
            html.Div([
                # Stock price plot
            ], id="graphs-content"),
            html.Div([
                # Indicator plot
            ], id="indicator-content"),
            html.Div([
                # Forecast plot
            ], id="forecast-content")
          ],
        className="content")
],className="container")


@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock_price", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
],
[Input("submit", "n_clicks")],
[State("stock_input", "value")])
def update_data(n,val): 
  if n == None:
        return "Hey there! Please enter a legitimate stock code to get the analysis.", "assets/stock1.jpg", None, None, None, None
        # raise PreventUpdate
  else:
      if val == None:
          raise PreventUpdate
      else:
        ticker = yf.Ticker(val)
        inf = ticker.info
        df = pd.DataFrame().from_dict(inf, orient="index").T
        df[['logo_url', 'shortName', 'longBusinessSummary']]
        return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0],None ,None, None
  

@app.callback([
    Output("graphs-content", "children"),
],
[Input("stock_price", "n_clicks"),
Input('my-date-picker-range', 'start_date'),
Input("my-date-picker-range", 'end_date')], [State("stock_input", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]

@app.callback([Output("indicator-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("stock_input", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]

@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("input_days", "value"),
               State("stock_input", "value")])
def forecast(n, input_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig= prediction(val, int(input_days) + 1)
    return [dcc.Graph(figure=fig)]




if __name__ == '__main__':
    app.run_server(debug=True)