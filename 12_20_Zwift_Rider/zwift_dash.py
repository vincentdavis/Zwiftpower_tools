import pandas as pd
from loginzwift_1 import get_json_data_from_url
import numpy as np
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px



flag = False
try:
    #z_id = '2528564'
    z_id = input("\nInput ZID : ")
    df = get_json_data_from_url(z_id)
    #print(df.columns)
    if 'category' in df.columns:
        flag = True
except:
    pass

if flag == False:
    print("\n[Error] Invalid ZID, Please Rerun and input valid ZID!.")
    
else:

    df['category'].value_counts()
    sub_cols = ['pos', 'category', 'w1200', 'w300', 'w120', 'w60', 'w30', 'w15', 'w5',
                'avg_wkg', 'wkg_ftp', 'wftp', 'wkg1200', 'wkg300', 'wkg120', 'wkg60', 'wkg30', 'wkg15','wkg5']
    
    def clean_w(val):
        try:
            res = int(val[0])
        except:
            res = float(val[0])
        return res
    
    for col in sub_cols:
        if col not in  ['pos', 'category']:
            try:
                df.loc[:, col] = df[col].apply(lambda val : clean_w(val))
            except:
                pass
            
    df = df.sort_values(by='pos')
    #df.head()
    
    watts_cols = ['w1200', 'w300', 'w120', 'w60', 'w30', 'w15', 'w5']
    watts_keys = ['20min', '5min', '2min', '1min', '30sec', '15sec', '5sec']
    watts_names = {}
    for idx in range(len(watts_cols)):
        watts_names[watts_cols[idx]] = watts_keys[idx]
        
    
    wkg_cols = ['avg_wkg', 'wkg_ftp', 'wkg1200', 'wkg300', 'wkg120', 'wkg60', 'wkg30', 'wkg15', 'wkg5']
    wkg_keys = ['Average', 'FTP', '20min', '5min', '2min', '1min', '30sec', '15sec', '5sec']
    wkg_names = {}
    for idx in range(len(wkg_cols)):
        wkg_names[wkg_cols[idx]] = wkg_keys[idx]
        
    cat_cols = df['category'].unique().tolist()
    #df.head()
    
    
    
    tabs_styles = {
        'height': '44px',
        'align-items': 'center'
    }
    tab_style = {
        'borderBottom': '1px solid #d6d6d6',
        'padding': '6px',
        'fontWeight': 'bold',
        'border-radius': '15px',
        'background-color': '#F2F2F2',
        'box-shadow': '4px 4px 4px 4px lightgrey',
     
    }
     
    tab_selected_style = {
        'borderTop': '1px solid #d6d6d6',
        'borderBottom': '1px solid #d6d6d6',
        'backgroundColor': '#119DFF',
        'color': 'white',
        'padding': '6px',
        'border-radius': '15px',
    }
    
    
    
    X_0 = np.array(sorted(df['pos'].unique()))
    Y_0 = np.array(df.groupby(['pos'])[watts_cols].mean().mean(axis=1))
    m_0, b_0 = np.polyfit(X_0, Y_0, 1) 
    title_0 = "Overall Category :  m = " + str(round(m_0, 2)) + ", b = " + str(round(b_0,2))
    fig = go.Figure()
    for col in watts_cols:
        fig.add_trace(go.Line(x=df["pos"], y=df[col],name=col))
    
    fig.add_trace(go.Scatter(x=X_0, y=m_0*X_0+b_0, name="Slipe Line", mode='lines+markers',
                               textposition="top center", line=dict(color="red",width=5), marker_size=15))
    
    fig.add_annotation(x=X_0[-1]-1, y=Y_0[-1]+150, text="y = "+ str(round(m_0,2))+"*X + "+str(round(b_0,2)), showarrow=True, arrowhead=5)
    fig.update_layout(autosize=False, width=1200, height=800,margin=dict(l=50,r=50,b=100,t=100,pad=4),paper_bgcolor="LightSteelBlue",
            title=dict(text=title_0, font_color='blue', x=0.5), xaxis=dict(title="Position",color="blue"), yaxis=dict(title="Watts Values",color="blue",rangemode="tozero"))
    
    
    X_1 = np.array(sorted(df['pos'].unique()))
    Y_1 = np.array(df.groupby(['pos'])[wkg_cols].mean().mean(axis=1))
    m_1, b_1 = np.polyfit(X_1, Y_1, 1) 
    title_1 = "Overall Category :  m = " + str(round(m_1, 2)) + ", b = " + str(round(b_1,2))
    fig_wkg = go.Figure()
    for col in wkg_cols:
        fig_wkg.add_trace(go.Line(x=df["pos"], y=df[col],name=col))
    
    fig_wkg.add_trace(go.Scatter(x=X_0, y=m_1*X_1+b_1, name="Slipe Line", mode='lines+markers',
                               textposition="top center", line=dict(color="red",width=5), marker_size=15))
    
    fig_wkg.add_annotation(x=X_1[-1]-1, y=Y_1[-1]+2, text="y = "+ str(round(m_1,2))+"*X + "+str(round(b_1,2)), showarrow=True, arrowhead=5)
    fig_wkg.update_layout(autosize=False, width=1200, height=800,margin=dict(l=50,r=50,b=100,t=100,pad=4),paper_bgcolor="LightSteelBlue",
            title=dict(text=title_1, font_color='blue', x=0.5), xaxis=dict(title="Position",color="blue"), yaxis=dict(title="WKG Values",color="blue",rangemode="tozero"))
    
    
    
    app = dash.Dash()
    # Create a Dash layout
    app.layout = html.Div([
        html.Div(
            html.H1('Zwiftpower Overview', style={"color": 'blue','marginLeft': 100,"textAlign": "left"})
        ),
        dcc.Tabs(id='tabs', value='Tab1', children=[
            dcc.Tab(label='Watts',style = tab_style, selected_style = tab_selected_style,
                    id='id_tab1', value='val_tab1', 
                    
                    children =[            
                        html.H3("Select Category",style={"color": 'green','marginLeft': 100}),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="id_watts",
                                    options=[{ 'label': i,'value': i } for i in cat_cols],value='A'),
                            ],style={'width': '15%', 'display': 'inline-block','marginLeft': 100}),
                        
                    html.H2("Watts Values for each Postion",  style={"color":"red","textAlign": "left","marginTop":60,'marginLeft': 100}),
                    dcc.Graph(id="app_1"),
                    
                    html.H2("\nOverall Watt Insights",  style={"color": 'red','marginTop': 50,"textAlign": "left",'marginLeft': 100}),
                    dcc.Graph(figure=fig),
                    
            ]),
            
            dcc.Tab(label='WKG',style = tab_style, selected_style = tab_selected_style,
                     id='id_tab2', value='val_tab2', 
                     
                    children=[
                         html.H3("Select Category",style={"color": 'green','marginLeft': 100}),
                         html.Div(
                            [
                                dcc.Dropdown(
                                    id="id_wkg",
                                    options=[{'label': i, 'value': i} for i in cat_cols], value='A'),],
                                        style={'width': '15%', 'display': 'inline-block','marginLeft': 100}),
                    
                        html.H2("WKG Values for each Postion",  style={"color":"red","textAlign": "left","marginTop":60,'marginLeft': 100}),
                    dcc.Graph(id="app_2"),
                    
                    html.H2("\nOverall WKG Insights",  style={"color": 'red','marginTop': 50,"textAlign": "left",'marginLeft': 100}),
                    dcc.Graph(figure=fig_wkg)
    
            ])
            
        ], style = tabs_styles)
    ])
    
    @app.callback(
        [dash.dependencies.Output('app_1', 'figure')],
        [dash.dependencies.Input('id_watts', 'value')])
    
    def update_graph(id_watts):
        df_filter = df[df['category']==id_watts]
        df_filter = df_filter.sort_values(by='pos')
        
        X = np.array(sorted(df_filter['pos'].unique()))
        Y = np.array(df_filter.groupby(['pos'])[watts_cols].mean().mean(axis=1))
        m, b = np.polyfit(X, Y, 1) 
        
        title = "Category : " + id_watts + ", m = " + str(round(m,2)) + ", b = " + str(round(b,2))
        fig_1 = go.Figure()
        for col in watts_cols:
            fig_1.add_trace(go.Line(x=df_filter["pos"], y=df_filter[col],name=col))
            #fig_1.add_trace(dict(x=df_filter["pos"], y=df_filter[col], type='scatter', mode='lines'))
        
        fig_1.add_trace(go.Scatter(x=X, y=m*X+b, name="Slipe Line",mode='lines+markers',
                                   textposition="top center", line=dict(color="red",width=5),marker_size=15))
        
        fig_1.add_annotation(x=X[-1]-1, y=Y[-1]+50, text="y = "+ str(round(m,2))+"*X + "+str(round(b,2)), showarrow=True, arrowhead=5)
        fig_1.update_layout(autosize=False, width=1200, height=800,margin=dict(l=50,r=50,b=100,t=100,pad=4),paper_bgcolor="LightSteelBlue",
                title=dict(text=title, font_color='blue', x=0.5), xaxis=dict(title="Position",color="blue"), yaxis=dict(title="Watts Values",color="blue",rangemode="tozero"))
    
        return [fig_1]
    
    @app.callback(
        [dash.dependencies.Output('app_2', 'figure')],
        [dash.dependencies.Input('id_wkg', 'value')])
    
    def update_graph(id_wkg):   
        df_filter = df[df['category']==id_wkg]
        df_filter = df_filter.sort_values(by='pos')
        
        X = np.array(sorted(df_filter['pos'].unique()))
        Y = np.array(df_filter.groupby(['pos'])[wkg_cols].mean().mean(axis=1))
        m, b = np.polyfit(X, Y, 1) 
        
        title = "Category : " + id_wkg + ", m = " + str(round(m,2)) + ", b = " + str(round(b,2))
        fig_2 = go.Figure()
        for col in wkg_cols:
            fig_2.add_trace(go.Line(x=df_filter["pos"], y=df_filter[col],name=col))
        
        fig_2.add_trace(go.Scatter(x=X, y=m*X+b, name="Slipe Line",mode='lines+markers',
                                   textposition="top center", line=dict(color="red",width=5),marker_size=15))
        
        fig_2.add_annotation(x=X[-1]-1, y=Y[-1]+2, text="y = "+ str(round(m,2))+"*X + "+str(round(b,2)), showarrow=True, arrowhead=5)
        fig_2.update_layout(autosize=False, width=1200, height=800,margin=dict(l=50,r=50,b=100,t=100,pad=4),paper_bgcolor="LightSteelBlue",
                title=dict(text=title, font_color='blue', x=0.5), xaxis=dict(title="Position",color="blue"), yaxis=dict(title="WKG Values",color="blue",rangemode="tozero"))
    
        return [fig_2]
    
    
    
    if __name__ == '__main__':
        app.run_server(debug=False)
        

