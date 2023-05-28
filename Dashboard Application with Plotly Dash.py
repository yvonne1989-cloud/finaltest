import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# 加载数据
spacex_df = pd.read_csv("spacex_launch_dash.csv").rename(columns={"Payload Mass (kg)": "Payload_Mass_Kg"})
max_payload = spacex_df['Payload_Mass_Kg'].max()
min_payload = spacex_df['Payload_Mass_Kg'].min()

# 创建 Dash 应用
app = dash.Dash(__name__)

# 定义样式
styles = {
    'container': {'margin': 'auto', 'width': '80%'},
    'header': {'margin-top': '30px', 'text-align': 'center'},
    'dropdown': {'margin-right': '20px', 'display': 'inline-block'},
    'slider': {'width': '60%', 'margin': '30px 0 50px'},
    'scatter-chart': {'height': '600px'}
}

# 定义应用布局
app.layout = html.Div([
    html.Div([
        html.H1("Payload and Launch Outcome", style=styles['header']),
        html.Div([
            html.Label("Select a site:", style={'margin-right': '10px'}),
            dcc.Dropdown(id="site-dropdown", options=[
                {"label": "All Sites", "value": "ALL"},
                {"label": "CCAFS LC-40", "value": "CCAFS LC-40"},
                {"label": "VAFB SLC-4E", "value": "VAFB SLC-4E"},
                {"label": "KSC LC-39A", "value": "KSC LC-39A"},
                {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"}
            ], value="ALL", placeholder="Select a Launch Site here", searchable=True),
            dcc.RangeSlider(id="payload-slider", min=0, max=10000, step=1000,
                            marks={0: '0', 100: '100'},
                            value=[min_payload, max_payload],
                            )
        ], style={'margin': '30px 0', 'text-align': 'center'}),

        dcc.Graph(id="success-pie-chart"),
        dcc.Graph(id="success-payload-scatter-chart")

    ], style=styles['container'])
])


@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value')])
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title=f"Success/Failure Counts for {entered_site.upper()}")
        return fig
    else:
        # return the outcomes piechart for a selected site
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(site_data,
                     names='class',
                     title=f"Success/Failure Counts for {entered_site.upper()}")
        return fig


# 创建回调函数
@app.callback(Output("success-payload-scatter-chart", "figure"),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def update_chart(site, payload_range):
    if site == "ALL":
        # 如果选择了所有站点，绘制所有值的散点图
        fig = px.scatter(data_frame=spacex_df, x="Payload_Mass_Kg", y="class", color="Booster Version Category",
                         )
    else:
        # 如果选择了特定站点，过滤数据并绘制散点图
        data = spacex_df[(spacex_df.Payload_Mass_Kg >= payload_range[0]) &
                         (spacex_df.Payload_Mass_Kg <= payload_range[1]) &
                         (spacex_df["Launch Site"] == site)]
        fig = px.scatter(data_frame=data, x="Payload_Mass_Kg", y="class", color="Booster Version Category",
                         )

    # 设置图表属性
    fig.update_layout(title=f"Payload and Launch Outcome for {site}",
                      xaxis_title="Payload Mass (kg)", yaxis_title="Launch Outcome")

    return fig


# 启动应用
if __name__ == '__main__':
    app.run_server(debug=True)