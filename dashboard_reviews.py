import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta

# Configuration
API_URL = "http://localhost:8000/api/reviews/"

app = dash.Dash(__name__)

def fetch_reviews():
    """Récupère les reviews depuis l'API"""
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
           
            df = pd.DataFrame(data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            df['date_only'] = df['created_at'].dt.date
            print(df)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Erreur: {e}")
        return pd.DataFrame()

# Layout principal
app.layout = html.Div([
    # En-tête avec style moderne
    html.Div([
        html.Div([
            html.H1("📊 Dashboard d'Analyse des Reviews", 
                    style={'margin': '0', 'color': 'white', 'fontSize': '32px'}),
            html.P("Analyse de sentiment en temps réel avec intelligence artificielle", 
                   style={'margin': '5px 0 0 0', 'color': '#ecf0f1', 'fontSize': '16px'})
        ]),
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '30px',
        'borderRadius': '15px',
        'marginBottom': '30px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.2)'
    }),
    
    # Barre d'actions
    html.Div([
        html.Button('🔄 Rafraîchir', id='refresh-button', n_clicks=0,
                   style={
                       'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                       'color': 'white',
                       'border': 'none',
                       'padding': '12px 30px',
                       'borderRadius': '25px',
                       'cursor': 'pointer',
                       'fontSize': '16px',
                       'fontWeight': 'bold',
                       'marginRight': '15px',
                       'boxShadow': '0 4px 15px rgba(102, 126, 234, 0.4)',
                       'transition': 'all 0.3s'
                   }),
        
        dcc.Dropdown(
            id='filter-dropdown',
            options=[
                {'label': '📊 Toutes les reviews', 'value': 'ALL'},
                {'label': '😊 Positives uniquement', 'value': 'POSITIVE'},
                {'label': '😞 Négatives uniquement', 'value': 'NEGATIVE'}
            ],
            value='ALL',
            style={
                'width': '250px',
                'display': 'inline-block',
                'marginRight': '15px'
            }
        ),
        
        dcc.DatePickerRange(
            id='date-range',
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            display_format='DD/MM/YYYY',
            style={'display': 'inline-block'}
        )
    ], style={
        'textAlign': 'center',
        'marginBottom': '30px',
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '10px'
    }),
    
    # Indicateur de chargement
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            # Métriques
            html.Div(id='metrics-cards', style={'marginBottom': '30px'}),
            
            # Graphiques principaux
            html.Div([
                html.Div([
                    dcc.Graph(id='sentiment-pie')
                ], style={
                    'width': '32%',
                    'display': 'inline-block',
                    'padding': '10px',
                    'verticalAlign': 'top'
                }),
                
                html.Div([
                    dcc.Graph(id='polarity-box')
                ], style={
                    'width': '32%',
                    'display': 'inline-block',
                    'padding': '10px',
                    'verticalAlign': 'top'
                }),
                
                html.Div([
                    dcc.Graph(id='top-words')
                ], style={
                    'width': '32%',
                    'display': 'inline-block',
                    'padding': '10px',
                    'verticalAlign': 'top'
                })
            ], style={'marginBottom': '20px'}),
            
            # Graphique temporel
            html.Div([
                dcc.Graph(id='timeline-chart')
            ], style={'marginBottom': '30px'}),
            
            # Statistiques détaillées
            html.Div(id='detailed-stats', style={'marginBottom': '30px'}),
            
            # Tableau des reviews
            html.Div([
                html.H2("📝 Liste Complète des Reviews", 
                       style={'color': '#2c3e50', 'marginBottom': '20px'}),
                html.Div(id='reviews-table')
            ], style={
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'boxShadow': '0 5px 20px rgba(0,0,0,0.1)'
            })
        ]
    )
    
], style={
    'padding': '30px',
    'backgroundColor': '#f0f2f5',
    'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    'minHeight': '100vh'
})

@app.callback(
    [Output('metrics-cards', 'children'),
     Output('sentiment-pie', 'figure'),
     Output('polarity-box', 'figure'),
     Output('top-words', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('detailed-stats', 'children'),
     Output('reviews-table', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('filter-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(n_clicks, filter_value, start_date, end_date):
    df = fetch_reviews()
    
    if df.empty:
        empty_msg = html.Div("⚠️ Aucune donnée disponible", 
                            style={'color': '#e74c3c', 'textAlign': 'center', 'fontSize': '20px'})
        return empty_msg, {}, {}, {}, {}, html.Div(), html.Div()
    
    # Filtrage par sentiment
    if filter_value != 'ALL':
        df = df[df['sentiment'] == filter_value]
    
    # Filtrage par date
    if start_date and end_date:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df['created_at'] >= start) & (df['created_at'] <= end)]
    
    # Calcul des métriques
    total = len(df)
    positive = len(df[df['sentiment'] == 'POSITIVE'])
    negative = len(df[df['sentiment'] == 'NEGATIVE'])
    avg_polarity = df['polarity'].mean()
    positive_rate = (positive / total * 100) if total > 0 else 0
    
    # Cartes de métriques avec design moderne
    metrics = html.Div([
        create_metric_card(str(total), "Total Reviews", "#667eea", "📊"),
        create_metric_card(str(positive), "Positives", "#10b981", "😊"),
        create_metric_card(str(negative), "Négatives", "#ef4444", "😞"),
        create_metric_card(f"{positive_rate:.1f}%", "Taux de Satisfaction", "#f59e0b", "⭐"),
        create_metric_card(f"{avg_polarity:.3f}", "Polarité Moyenne", "#8b5cf6", "🎯")
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '15px', 'flexWrap': 'wrap'})
    
    # Graphique en camembert 3D
    sentiment_counts = df['sentiment'].value_counts()
    pie_fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.5,
        marker=dict(colors=['#10b981', '#ef4444']),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        pull=[0.1, 0.1]
    )])
    pie_fig.update_layout(
        title="Distribution des Sentiments",
        title_font=dict(size=18, color='#2c3e50'),
        height=350,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Box plot de polarité par sentiment
    box_fig = go.Figure()
    for sentiment in ['POSITIVE', 'NEGATIVE']:
        data = df[df['sentiment'] == sentiment]['polarity']
        color = '#10b981' if sentiment == 'POSITIVE' else '#ef4444'
        box_fig.add_trace(go.Box(
            y=data,
            name=sentiment,
            marker_color=color,
            boxmean='sd'
        ))
    box_fig.update_layout(
        title="Distribution de la Polarité",
        title_font=dict(size=18, color='#2c3e50'),
        yaxis_title="Score de Polarité",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    # Analyse des mots dans les titres
    from collections import Counter
    import re
    
    all_words = []
    for title in df['title']:
        words = re.findall(r'\b\w+\b', title.lower())
        all_words.extend([w for w in words if len(w) > 3])
    
    word_counts = Counter(all_words).most_common(10)
    if word_counts:
        words, counts = zip(*word_counts)
        words_fig = go.Figure(data=[go.Bar(
            x=list(counts),
            y=list(words),
            orientation='h',
            marker=dict(
                color=list(counts),
                colorscale='Viridis',
                showscale=True
            ),
            text=list(counts),
            textposition='auto'
        )])
        words_fig.update_layout(
            title="Top 10 Mots Fréquents",
            title_font=dict(size=18, color='#2c3e50'),
            xaxis_title="Fréquence",
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    else:
        words_fig = {}
    
    # Timeline avec moyenne mobile
    timeline_df = df.groupby([df['created_at'].dt.date, 'sentiment']).size().reset_index(name='count')
    timeline_fig = px.line(
        timeline_df,
        x='created_at',
        y='count',
        color='sentiment',
        title="Évolution Temporelle des Reviews",
        color_discrete_map={'POSITIVE': '#10b981', 'NEGATIVE': '#ef4444'},
        markers=True
    )
    timeline_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Nombre de Reviews",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    # Statistiques détaillées
    stats = html.Div([
        html.H3("📈 Statistiques Détaillées", style={'color': '#2c3e50', 'marginBottom': '20px'}),
        html.Div([
            html.Div([
                html.P("Polarité Maximale", style={'fontWeight': 'bold', 'color': '#7f8c8d'}),
                html.P(f"{df['polarity'].max():.3f}", style={'fontSize': '24px', 'color': '#10b981', 'margin': '5px 0'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '0 10px'}),
            
            html.Div([
                html.P("Polarité Minimale", style={'fontWeight': 'bold', 'color': '#7f8c8d'}),
                html.P(f"{df['polarity'].min():.3f}", style={'fontSize': '24px', 'color': '#ef4444', 'margin': '5px 0'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '0 10px'}),
            
            html.Div([
                html.P("Écart-Type", style={'fontWeight': 'bold', 'color': '#7f8c8d'}),
                html.P(f"{df['polarity'].std():.3f}", style={'fontSize': '24px', 'color': '#667eea', 'margin': '5px 0'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '0 10px'}),
            
            html.Div([
                html.P("Médiane", style={'fontWeight': 'bold', 'color': '#7f8c8d'}),
                html.P(f"{df['polarity'].median():.3f}", style={'fontSize': '24px', 'color': '#f59e0b', 'margin': '5px 0'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '0 10px'})
        ], style={'display': 'flex', 'gap': '20px'})
    ], style={'padding': '30px', 'backgroundColor': '#f8f9fa', 'borderRadius': '15px'})
    
    # Tableau stylisé
    table_df = df[['id', 'title', 'sentiment', 'polarity', 'date']].copy()
    table_df = table_df.sort_values('created_at', ascending=False) if 'created_at' in df.columns else table_df
    
    table = dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Sentiment', 'id': 'sentiment'},
            {'name': 'Polarité', 'id': 'polarity', 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {'name': 'Date', 'id': 'date'}
        ],
        style_table={'overflowX': 'auto'},
        style_header={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'padding': '15px',
            'fontSize': '14px'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '15px',
            'fontFamily': "'Segoe UI', sans-serif",
            'fontSize': '13px',
            'border': '1px solid #e0e0e0'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{sentiment} = "POSITIVE"', 'column_id': 'sentiment'},
                'backgroundColor': '#d1fae5',
                'color': '#065f46',
                'fontWeight': 'bold'
            },
            {
                'if': {'filter_query': '{sentiment} = "NEGATIVE"', 'column_id': 'sentiment'},
                'backgroundColor': '#fee2e2',
                'color': '#991b1b',
                'fontWeight': 'bold'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9fafb'
            }
        ],
        page_size=15,
        sort_action='native',
        filter_action='native',
        style_filter={
            'backgroundColor': '#f0f2f5'
        }
    )
    
    return metrics, pie_fig, box_fig, words_fig, timeline_fig, stats, table

def create_metric_card(value, label, color, icon):
    """Crée une carte de métrique avec design moderne"""
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize': '40px', 'marginBottom': '10px'}),
            html.H2(value, style={'margin': '10px 0', 'color': color, 'fontSize': '32px', 'fontWeight': 'bold'}),
            html.P(label, style={'margin': '0', 'color': '#6b7280', 'fontSize': '14px'})
        ], style={
            'backgroundColor': 'white',
            'padding': '25px',
            'borderRadius': '15px',
            'textAlign': 'center',
            'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
            'border': f'3px solid {color}',
            'transition': 'transform 0.3s',
            'flex': '1',
            'minWidth': '180px'
        })
    ], style={'flex': '1', 'minWidth': '180px'})

if __name__ == '__main__':
    app.run(debug=True, port=8050)