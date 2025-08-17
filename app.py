# app.py

import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
import numpy as np

# 実行中ファイルのディレクトリを取得
base_dir = os.path.dirname(__file__)

# プロジェクト内の data フォルダ直下の dat_dhs.xlsx を指定
file_path = os.path.join(base_dir, 'data', 'dat_dhs.xlsx')

# ExcelファイルをDataFrameに読み込む
df_labels = pd.read_excel(file_path, sheet_name='labels', engine='openpyxl')
df_dhs = pd.read_excel(file_path, sheet_name='dat_all', engine='openpyxl')

# print(df_labels.head())
# print(df_dhs.head())

# optionsリストを作成
select_options = [
    {'label': row['var_label'], 'value': row['var_name']}
    for idx, row in df_labels.iterrows()
    if row['var_name'] != 'DHS04'  # この条件でスキップ
]
varname_to_label = dict(zip(df_labels['var_name'], df_labels['var_label']))


# Dashアプリを作成
app = dash.Dash(__name__)
server = app.server  # 追加 ← これがないとgunicornが動かない

app.layout = html.Div([
    html.H2("「5歳未満児の成長阻害」と各種要因の散布図"),
    dcc.Dropdown(
        id='x-col',
        options=select_options,
        value='DHS01',
        clearable=False
    ),
    dcc.Graph(id='scatter-plot')
])

# コールバック


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-col', 'value')]
)
def update_graph(x_col):
    y_col = 'DHS04'
    # 変数ラベルを取得
    x_label = varname_to_label.get(x_col, x_col) + ' (%)'
    y_label = 'stunted children under 5 (%)'

    # NaNやinfを除いたデータを用意
    data = df_dhs[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()

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
    # 幅=800ピクセル、高さ=600ピクセルに固定
    fig.update_layout(width=600, height=800)

    # 注釈（グラフ右上、上部余白に配置する例）
    fig.add_annotation(
        text=annotation_text,
        xref='paper', yref='paper',
        x=0.99, y=0.99,        # 右上：x=1, y=1（0~1）
        showarrow=False,
        font=dict(size=14, color="black"),
        align="right",
        bordercolor="black",
        borderwidth=1,
        bgcolor="rgba(255,255,255,0.7)",
        opacity=0.8
    )

    return fig


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Cloud Runが自動で指定する
    app.run(host="0.0.0.0", port=port, debug=True)
