<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Dashで「散布図」と「全変数テーブル」を切り替え表示する方法まとめ

### 1. ユーザー選択で表示切替

- **ドロップダウン**で変数を選択。
- **ラジオボタン（RadioItems）**で「散布図」「テーブル」表示を切り替え。


### 2. コールバックの仕組み

- Dashの `@app.callback` を用いて、入力コンポーネント（ドロップダウン・ラジオボタン）の値に応じて出力を動的に変える。
- コールバック関数の返り値で、 `output-area` の表示内容（children）が変わる。


### 3. テーブル表示の注意点

- テーブル表示の際、`df_dhs[[x_col, y_col]]` などと2変数だけ抽出していると、2列しか表示されない。
- **全列表示させるには：**
`df_dhs` の全列を利用し（例：`data_all = df_dhs.replace([np.inf, -np.inf], np.nan).dropna()`）、
`columns` も自動生成してすべての項目を表示する。

```python
columns_all = [
    {"name": varname_to_label.get(col, col), "id": col}
    for col in data_all.columns
]

table = dash_table.DataTable(
    data=data_all.to_dict('records'),
    columns=columns_all,
    page_size=10,
    style_table={'overflowX': 'auto'}
)
```


### 4. 実装例

- 散布図の場合は選択変数でグラフ作成。
- テーブル表示の場合は全変数・全列をDataTable表示。
- コールバック内で分岐させてどちらかを返す。

***

**ポイント：表示用のデータ（data）を目的に応じて切り替えることで散布図・全列テーブルの切り替え表示が可能になります。**

