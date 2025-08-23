import os
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np

# 実行中ファイルのディレクトリを取得
base_dir = os.path.dirname(__file__)

# プロジェクト内の data フォルダ直下の dat_dhs.xlsx を指定
file_path = os.path.join(base_dir, 'data', 'dat_dhs.xlsx')

# ExcelファイルをDataFrameに読み込み
df_labels = pd.read_excel(file_path, sheet_name='labels', engine='openpyxl')
df_dhs = pd.read_excel(file_path, sheet_name='dat_all', engine='openpyxl')
print(df_dhs.isnull().sum())
with open(os.path.join(base_dir, 'data', 'describe.txt'), 'w') as f:
    f.write(df_dhs.describe().to_string())

# カテゴリ変数化
df_dhs['Country_code'] = df_dhs['Country_code'].astype('category')
df_dhs['Year'] = df_dhs['Year'].astype('category')
df_dhs.isnull().sum()  # 欠損値の確認

# フォーミュラ作成と適合
formula = "DHS04 ~ FAO_21013 + DHS01 + DHS03 + DHS10 + DHS11 + DHS12 + C(Country_code) + C(Year)"
result = smf.ols(formula, data=df_dhs).fit()

# 結果表示
print(result.summary())
