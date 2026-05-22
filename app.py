from flask import Flask
import pandas as pd
import re as r

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Grade-3 English Result Dashboard</h1><p>Welcome!</p>"

df = pd.read_excel(r'data\English_Boys_Pink.xlsx', sheet_name='Sheet1')
print(df.head())
print(df.columns.tolist)

if __name__ == '__main__':
    app.run(debug=True)