import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
import dash_bootstrap_components as dbc 
import numpy as np

external_stylesheets = [
    dbc.themes.BOOTSTRAP  # 公式テーマ（テーマを変えたければここを変更）
]

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
    if (row['var_name'] != 'DHS04')
       and (row['var_name'] != 'FAO_22013')
       and (row['var_name'] in df_dhs.columns)
]
varname_to_label = dict(zip(df_labels['var_name'], df_labels['var_label']))
# print(select_options)

# Dashアプリを作成
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "stunting and key factors"  # ブラウザのタブなどに表示される
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("「5歳未満児の成長阻害」と各種要因の散布図／テーブル"), width=12)
    ], className="mb-4 mt-4"),
    dbc.Row([
        dbc.Col([
            dbc.Label("表示タイプ"),
            dbc.RadioItems(
                id='view-type',
                options=[
                    {'label': '散布図', 'value': 'scatter'},
                    {'label': 'テーブル', 'value': 'table'}
                ],
                value='scatter',
                inline=True,
            ),
            dbc.Label("横軸変数", className="mt-3"),
            dcc.Dropdown(
                id='x-col',
                options=select_options,
                value=select_options[0]['value'],
                clearable=False,
            )
        ], md=8),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='output-area'), width=12)
    ], className="mt-4")
], fluid=True)

@app.callback(
    Output('output-area', 'children'),
    [Input('x-col', 'value'), Input('view-type', 'value')]
)
# 固定効果を加えた相関・回帰分析
def update_output(x_col, view_type):
    y_col = 'DHS04'
    x_label = varname_to_label.get(x_col, x_col) + ' (%)'
    y_label = 'stunted children under 5 (%)'

    # country, Yearはdf_dhsの列名に合わせてください
    fe_cols = ['Country_code', 'Year']

    # 必要な列のみ
    needed_cols = [x_col, y_col] + fe_cols
    data = df_dhs[needed_cols].replace([np.inf, -np.inf], np.nan).dropna()

    if view_type == 'scatter':
        # 基本モデル：y ~ C(Country_code) + C(Year)
        base_formula = f"{y_col} ~ C(Country_code) + C(Year)"
        base_model = sm.OLS.from_formula(base_formula, data=data).fit()
        r2_base = base_model.rsquared

        # 選択変数追加モデル：y ~ x_col + C(Country_code) + C(Year)
        full_formula = f"{y_col} ~ {x_col} + C(Country_code) + C(Year)"
        full_model = sm.OLS.from_formula(full_formula, data=data).fit()
        r2_full = full_model.rsquared

        # 寄与R²：選択変数の説明力
        r2_contrib = np.round(r2_full - r2_base, 3)
        
        # 固定効果なしモデル
        naive_formula_no_fe = f"{y_col} ~ {x_col}"
        naive_model_no_fe = sm.OLS.from_formula(naive_formula_no_fe, data=data).fit()
        r2_naive = naive_model_no_fe.rsquared
        r2_naive = np.round(r2_naive, 3)
        r_naive_dis = np.corrcoef(data[x_col], data[y_col])[0, 1]
        r_naive_dis = np.round(r_naive_dis, 2)

        # 残差相関係数（xとyから固定効果を差し引いた部分の相関）
        # 1. x, yそれぞれ国・年固定効果付き回帰の残差を得る
        x_resid = sm.OLS.from_formula(f"{x_col} ~ C(Country_code) + C(Year)", data=data).fit().resid
        y_resid = sm.OLS.from_formula(f"{y_col} ~ C(Country_code) + C(Year)", data=data).fit().resid
        r = np.corrcoef(x_resid, y_resid)[0, 1]
        r_disp = np.round(r, 2)

        annotation_text = f"固定効果付き相関 r = {r_disp}, R² = {r2_contrib}<br>"
        annotation_text += f"固定効果なし相関 r = {r_naive_dis}, R² = {r2_naive}"

        fig = px.scatter(
            data, x=x_col, y=y_col,
            labels={x_col: x_label, y_col: y_label},
            title=f"{x_label}と{y_label}の散布図（国・年固定効果付き）",
            trendline="ols",
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
    app.run(debug=True)
