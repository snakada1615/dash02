import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
import numpy as np

# 実行中ファイルのディレクトリを取得
base_dir = os.path.dirname(__file__)

# プロジェクト内の data フォルダ直下の dat_dhs.xlsx を指定
file_path = os.path.join(base_dir, 'data', 'dat_dhs.xlsx')

# ExcelファイルをDataFrameに読み込み
df_labels = pd.read_excel(file_path, sheet_name='labels', engine='openpyxl')
df_dhs = pd.read_excel(file_path, sheet_name='dat_all', engine='openpyxl')

# optionsリストを作成
select_options = [
    {'label': row['var_label'], 'value': row['var_name']}
    for idx, row in df_labels.iterrows()
    if row['var_name'] != 'DHS04'
]
varname_to_label = dict(zip(df_labels['var_name'], df_labels['var_label']))

# Dashアプリを作成
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("「5歳未満児の成長阻害」と各種要因の散布図／テーブル"),
    dcc.RadioItems(
        id='view-type',
        options=[
            {'label': '散布図', 'value': 'scatter'},
            {'label': 'テーブル', 'value': 'table'}
        ],
        value='scatter',
        labelStyle={'display': 'inline-block', 'margin-right': '20px'}
    ),
    dcc.Dropdown(
        id='x-col',
        options=select_options,
        value='DHS01',
        clearable=False
    ),
    html.Div(id='output-area', style={'margin-top': '30px'})
])


@app.callback(
    Output('output-area', 'children'),
    [Input('x-col', 'value'), Input('view-type', 'value')]
)
def update_output(x_col, view_type):
    y_col = 'DHS04'
    x_label = varname_to_label.get(x_col, x_col) + ' (%)'
    y_label = 'stunted children under 5 (%)'

    # NaNやinfを除いたデータを用意
    data = df_dhs[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()

    if view_type == 'scatter':
        # 相関係数の計算
        r = data.corr(method='pearson').iloc[0, 1]
        # 線形回帰
        X = sm.add_constant(data[x_col])
        model = sm.OLS(data[y_col], X).fit()
        r2 = model.rsquared
        # 小数点2桁で丸める
        r_disp = np.round(r, 2)
        r2_disp = np.round(r2, 2)
        annotation_text = f"相関係数 r = {r_disp}, R² = {r2_disp}"

        fig = px.scatter(
            df_dhs, x=x_col, y=y_col,
            labels={x_col: x_label, 'DHS04': y_label},
            title=f"{x_label}と{y_label}の相関図",
            trendline="ols"
        )
        fig.update_layout(width=600, height=800)
        fig.add_annotation(
            text=annotation_text,
            xref='paper', yref='paper',
            x=0.99, y=0.99,
            showarrow=False,
            font=dict(size=14, color="black"),
            align="right",
            bordercolor="black",
            borderwidth=1,
            bgcolor="rgba(255,255,255,0.7)",
            opacity=0.8
        )
        return dcc.Graph(figure=fig)
    else:
        # テーブル表示
        data_all = df_dhs
        columns_all = [
            {"name": varname_to_label.get(col, col), "id": col}
            for col in data_all.columns
        ]
        table = dash_table.DataTable(
            data=data_all.to_dict('records'),
            columns=columns_all,
            page_size=20,
            style_table={'overflowX': 'auto'}
        )
        return table


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
