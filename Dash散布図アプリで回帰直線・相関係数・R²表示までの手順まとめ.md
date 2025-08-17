<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Dash散布図アプリで回帰直線・相関係数・R²表示までの手順まとめ


***

### 1. 変数ラベル辞書の準備

ラベル用に、`df_labels` から変数名→ラベルの辞書を作成します。

```python
varname_to_label = dict(zip(df_labels['var_name'], df_labels['var_label']))
```


***

### 2. コールバック関数でのグラフ生成と統計量計算

- x軸（選択変数）と y軸（DHS04）で、**NaN・infを除外したデータ**を作成
- 相関係数（r）と回帰分析（R²）を計算
- 散布図（回帰直線付き）、アノテーション（統計量表示）を生成

```python
import numpy as np
import statsmodels.api as sm

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-col', 'value')]
)
def update_graph(x_col):
    y_col = 'DHS04'
    x_label = varname_to_label.get(x_col, x_col)
    y_label = varname_to_label.get(y_col, y_col)

    # NaNやinfを除外
    data = df_dhs[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()

    # 相関係数
    r = data.corr(method='pearson').iloc[0,1]

    # 回帰分析（R²）
    X = sm.add_constant(data[x_col])
    model = sm.OLS(data[y_col], X).fit()
    r2 = model.rsquared

    # 表示用
    r_disp = np.round(r, 2)
    r2_disp = np.round(r2, 2)
    annotation_text = f"相関係数 r = {r_disp}, R² = {r2_disp}"

    fig = px.scatter(
        df_dhs, x=x_col, y=y_col,
        labels={x_col: x_label, y_col: y_label},
        title=f"各国の{x_label}と{y_label}の散布図",
        trendline="ols"
    )
    fig.update_layout(width=800, height=600)
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
    return fig
```


***

### 3. 散布図点の値表示のON/OFF

点の上に値ラベルを**表示しない**なら、`px.scatter`の`text`引数を省略します。

***

### 4. グラフのサイズ固定

```python
fig.update_layout(width=800, height=600)
```


***

### 5. メインアプリ構成

`dcc.Dropdown`で変数切替が可能なシンプルなDashレイアウト。

```python
app.layout = html.Div([
    html.H2("各国の人口と経済指標の散布図"),
    dcc.Dropdown(
        id='x-col',
        options=select_options,
        value='DHS01',
        clearable=False
    ),
    dcc.Graph(id='scatter-plot')
])
```


***

## 補足

- 必要なパッケージ：`dash`, `pandas`, `plotly`, `statsmodels`, `openpyxl`
- `trendline="ols"`で回帰直線自体も自動描画されます
- ラベルの割り当てやレイアウトも柔軟に調整可能です

***

分かりやすいまとめや他のTipsが必要ならまたご相談ください！

