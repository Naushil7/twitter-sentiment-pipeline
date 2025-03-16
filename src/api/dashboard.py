import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, title="Twitter Sentiment Dashboard")

# Define the layout
app.layout = html.Div(style={'backgroundColor': '#f8f9fa', 'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1("Twitter Sentiment Analysis Dashboard", style={'textAlign': 'center', 'color': '#343a40', 'marginBottom': '20px'}),

    # Refresh Button & Last Update Time
    html.Div(style={'textAlign': 'center', 'marginBottom': '20px'}, children=[
        html.Button('🔄 Refresh Data', id='refresh-button', n_clicks=0, 
                    style={'padding': '10px 20px', 'fontSize': '16px', 'borderRadius': '5px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none'}),
        html.Div(id='last-update-time', style={'marginTop': '10px', 'color': '#6c757d'})
    ]),

    # Charts Section
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div([
            html.H3("Sentiment Distribution", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='sentiment-pie', style={'boxShadow': '0px 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '10px'})
        ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3("Topic Distribution", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='topic-pie', style={'boxShadow': '0px 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '10px'})
        ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
    ]),

    # Recent Tweets Table
    html.Div([
        html.H3("Recent Tweets", style={'color': '#343a40'}),
        html.Div(id='tweets-table', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 
                                           'boxShadow': '0px 4px 8px rgba(0,0,0,0.1)'})
    ], style={'marginTop': '20px'}),

    # Store the data
    dcc.Store(id='tweets-data'),
    dcc.Store(id='summary-data'),

    # Auto Refresh
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

# Callback to fetch data
@app.callback(
    [Output('tweets-data', 'data'),
     Output('summary-data', 'data'),
     Output('last-update-time', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_data(n_intervals, n_clicks):
    try:
        tweets_response = requests.get('http://api:8000/tweets', params={'limit': 50})
        # tweets_response = requests.get('http://localhost:8000/tweets', params={'limit': 50})
        tweets_data = tweets_response.json()
        
        summary_response = requests.get('http://api:8000/summary')
        # summary_response = requests.get('http://localhost:8000/summary')
        summary_data = summary_response.json()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return tweets_data, summary_data, f"Last updated: {current_time}"
    except:
        return {}, {}, "⚠️ Data fetch failed. API may not be running."

# Sentiment Pie Chart
@app.callback(
    Output('sentiment-pie', 'figure'),
    [Input('summary-data', 'data')]
)
def update_sentiment_pie(summary_data):
    if not summary_data or 'sentiment_distribution' not in summary_data:
        return go.Figure()
    
    sentiments = summary_data['sentiment_distribution']
    labels = list(sentiments.keys())
    values = list(sentiments.values())

    colors = {'positive': '#28a745', 'neutral': '#6c757d', 'negative': '#dc3545'}
    
    fig = px.pie(
        names=labels, values=values, title="Sentiment Distribution",
        color=labels, color_discrete_map=colors
    )
    
    fig.update_traces(textinfo='percent+label', pull=[0.05, 0, 0])
    return fig

# Topic Pie Chart
@app.callback(
    Output('topic-pie', 'figure'),
    [Input('summary-data', 'data')]
)
def update_topic_pie(summary_data):
    if not summary_data or 'topic_distribution' not in summary_data:
        return go.Figure()
    
    topics = summary_data['topic_distribution']
    labels = list(topics.keys())
    values = list(topics.values())

    fig = px.pie(names=labels, values=values, title="Topic Distribution")
    fig.update_traces(textinfo='percent+label')
    
    return fig

# Tweets Table
@app.callback(
    Output('tweets-table', 'children'),
    [Input('tweets-data', 'data')]
)
def update_tweets_table(tweets_data):
    if not tweets_data or 'tweets' not in tweets_data or not tweets_data['tweets']:
        return html.Div("No tweets available", style={'textAlign': 'center', 'color': '#dc3545'})
    
    tweets = tweets_data['tweets']

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Tweet Text"), html.Th("Sentiment"), html.Th("Topic"), html.Th("Polarity"), html.Th("Created At")
        ], style={'backgroundColor': '#007bff', 'color': 'white'})),
        
        html.Tbody([
            html.Tr([
                html.Td(tweet.get('text', '')),
                html.Td(tweet.get('sentiment', ''), style={
                    'color': '#28a745' if tweet.get('sentiment') == 'positive' 
                             else '#dc3545' if tweet.get('sentiment') == 'negative'
                             else '#6c757d'
                }),
                html.Td(tweet.get('topic', '')),
                html.Td(f"{tweet.get('polarity', 0):.2f}"),
                html.Td(tweet.get('created_at', '').split('T')[0] if 'created_at' in tweet else '')
            ], style={'borderBottom': '1px solid #ddd'}) for tweet in tweets[:10]
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '10px'})

    return table

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
