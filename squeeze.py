import os, pandas
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

dataframes = {}

# overwrite output file
file1 = open("output/index.html", "a")
file1.close()

for filename in os.listdir('datasets'):
    #print(filename)
    symbol = filename.split(".")[0]
    #print(symbol)
    df = pandas.read_csv('datasets/{}'.format(filename))
    if df.empty:
        continue

    df['20sma'] = df['Close'].rolling(window=20).mean()
    df['stddev'] = df['Close'].rolling(window=20).std()
    df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    df['upper_band'] = df['20sma'] + (2 * df['stddev'])

    df['TR'] = abs(df['High'] - df['Low'])
    df['ATR'] = df['TR'].rolling(window=20).mean()

    df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

    def in_squeeze(df):
        return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

    df['squeeze_on'] = df.apply(in_squeeze, axis=1)

    if df.iloc[-3]['squeeze_on'] and not df.iloc[-1]['squeeze_on']:
        print("{} is coming out the squeeze".format(symbol))

        dataframes[symbol] = df


        def chart(df):

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), secondary_y=True)
            fig.add_trace(go.Scatter(x=df['Date'], y=df['upper_band'], name='Upper Bollinger Band', line={'color': 'red'}), secondary_y=True)
            fig.add_trace(go.Scatter(x=df['Date'], y=df['lower_band'], name='Lower Bollinger Band', line={'color': 'red'}), secondary_y=True)
            fig.add_trace(go.Scatter(x=df['Date'], y=df['upper_keltner'], name='Upper Keltner Channel', line={'color': 'blue'}), secondary_y=True)
            fig.add_trace(go.Scatter(x=df['Date'], y=df['lower_keltner'], name='Lower Keltner Channel', line={'color': 'blue'}), secondary_y=True)
            fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], showlegend=False), secondary_y=False)
            fig.layout.xaxis.type = 'category'
            fig.layout.xaxis.rangeslider.visible = False
            fig.layout.title = symbol
            #fig.show()
            fig.write_html("output/" + symbol + ".html")
            file1 = open("output/index.html", "a")
            file1.write('<iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="' + symbol + '.html" height="525" width="100%"></iframe>\n')
            file1.close()

        df = dataframes[symbol]
        chart(df)
