from dash_core_components import Download
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import pandas as pd
import twitter  # pip install python-twitter
from app import app, api
import nltk


# nltk.download('stopwords') # only downlaod once
# Resource: https://python-twitter.readthedocs.io/en/latest/twitter.html

# Create stopword list for wordcloud analysis later:
stopwords = nltk.corpus.stopwords.words('english')
stopwords = set(stopwords)
stopwords.update(["https", "plotlygraphs"])

def f(row):
    return "[{0}]({0})".format(row["url"])

# layout of second (trends) tab ******************************************
trends_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Most trending topics")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='table-div', children="")
        ], width=6),
        dbc.Col([
            html.Div(id='figure-div', children="")
        ], width=6),
    ], className="mt-3",),
    dcc.Interval(id='timer', interval=1000*300, n_intervals=0)
])

Download.layout = dbc.Container(
    [
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
        ),

        dbc.Button(id='btn',
            children=[html.I(className="fa fa-download mr-1"), "Download"],
            color="info",
            className="mt-1"
        ),

        dcc.Download(id="download-component"),
    ],
    className='m-4'
)


@app.callback(
    Output("download-component", "data"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dict(content="Always remember, we're better together.", filename="hello.txt")
    # return dcc.send_data_frame(df.to_csv, "mydf_csv.csv")
    # return dcc.send_data_frame(df.to_excel, "mydf_excel.xlsx", sheet_name="Sheet_name_1")
    # return dcc.send_file("./assets/data_file.txt")
    # return dcc.send_file("./assets/bees-by-Lisa-from-Pexels.jpg")

# pull trending tweets and create the table ******************************
@app.callback(
    Output(component_id="table-div", component_property="children"),
    Input(component_id="timer", component_property="n_intervals"),
)
def display_trend(timer):
    trnd_name, trnd_vol, trnd_url = [], [], []
    trends = api.GetTrendsCurrent()
    for trend in trends:
        print(trend)
        if trend.tweet_volume:
            trnd_name.append(trend.name)
            trnd_vol.append(trend.tweet_volume)
            trnd_url.append(trend.url)
    d = {
        "trending": trnd_name,
        "url": trnd_url,
        "volume": trnd_vol,
    }
    df = pd.DataFrame(d)
    # aply function so you can insert url link inside Dash DataTable
    df["url"] = df.apply(f, axis=1)
    print(df.head())

    return dash_table.DataTable(
        id='datatable-trends',
        columns=[
            {"name": i, "id": i}
            if i == "trending" or i == "volume"
            else {"name": i, "id": i, 'type': 'text', "presentation":"markdown"}
            for i in df.columns
        ],
        data=df.to_dict('records'),
        markdown_options=dict(html=True, link_target='_blank'),
        page_action='native',
        page_size=6,
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'overflow': 'hidden',
            'minWidth': '50px', 'width': '80px', 'maxWidth': '120px',
        },
    )


# pull liked tweets by user **********************************************
@app.callback(
    Output(component_id="figure-div", component_property="children"),
    Input(component_id="timer", component_property="n_intervals"),
)
def display_trend(timer):
    liked_twt = []
    # get tweets metadata that were liked by @Plotlygraphs
    x = api.GetFavorites(screen_name='plotlygraphs', count=100, return_json=False)
    # extract the tweet text, from the metadata, into a list
    for status in x:
        liked_twt.append(status.text)

    # join all tweet text into one string
    alltweets = " ".join(tweet for tweet in liked_twt)