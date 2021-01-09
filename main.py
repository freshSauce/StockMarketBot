import requests as r
import threading
import logging
from flask import Flask, request, Response
from re import match

logging.basicConfig(format='[%(asctime)s - %(levelname)s] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='debug.log', level=logging.INFO)

class StockBot:
    def __init__(self, BOT_API_KEY, STOCK_API_KEY, chat_id):
        self.STOC_API_KEY = STOCK_API_KEY
        self.BOT_API_KEY = BOT_API_KEY
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.stock_watchlist = []
        self.querystring = {"region":"US","symbols":', '.join(stock_watchlist)}
        self.stock_url = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes'
        self.headers = {
                        'x-rapidapi-key': STOCK_API_KEY,
                        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
                        }          
        self.alerts = {'higherThan':[], 'lowerThan':[]}
        self.watchlist_prices = {}
        self.chat_id = chat_id
        self.data = {
                    'text':'',
                    'chat_id':self.chat_id
                    }
        self.sendMessageUrl = f'https://api.telegram.org/bot{BOT_API_KEY}/sendMessage'
    
    def start_message(self):
        self.data['text'] = '''
                <strong>Welcome to the Stock Bot! V.PRE-BETA</strong>
            
    The bot uses the <a href="https://rapidapi.com/apidojo/api/yahoo-finance1">Yahoo Finance API provided by ApiDojo @ RapidApi</a>

    Commands:

        - /setalert &lt;higherThan/lowerThan&gt; &lt;symbol&gt; &lt;price&gt; - Add an alert to your alert's list
            - Example: /setalert higherThan AAPL 150.72 - will add an alert for Apple (AAPL) that will tell you when its price goes over 150.72 USD

        - /removealert &lt;higherThan/lowerThan&gt; &lt;ID&gt; - Remove an alert from your alert's list
            - Example: /removealert higherThan 2 - will remove the alert with ID 2 on higherThan

        - /watchlistadd &lt;market&gt; &lt;symbol&gt; - Add a symbol (such as AAPL, AMD, IBM) to your watchlist.
            - Example: /watchlistadd US AAPL

        - /watchlistremove &lt;symbol&gt; - Remove a symbol from your watchlist.
            - Example: /watchlistremove AAPL 

        - /alertlist - Will return your alert list

If something went wrong while you were using the bot, please send a message to <a href="tg://user?id=560110547">bot's creator</a>
Github: <a href="https://github.com/freshSauce">@freshSauce</a>

            
            '''
        datastart = self.data.copy()
        datastart['parse_mode'] = 'HTML'
        datastart['disable_web_page_preview'] = 'true'
        return
    def alert_list(self):
        all_high_alerts = []
        all_low_alerts = []
        try:
            for alert in alerts['higherThan']:
                high_alert = f'Symbol: {alert.split("-")[1]} ID: {alert.split("-")[0]} Price: {alerts["higherThan"][alert]}'
                all_high_alerts.append(high_alert)
            data_full = "\n".join(all_high_alerts)
            self.data['text'] = f'Higher Than - Alerts:\n\n{data_full}'
            r.post(url=sendMessageUrl, data=self.data)
        except:
            self.data['text'] = f'Higher Than - Alerts:\n\nYou have no alerts on Higher Than'
            r.post(url=sendMessageUrl, data=self.data)
        try:
            for alert in alerts['lowerThan']:
                low_alert = f'Symbol: {alert.split("-")[1]} ID: {alert.split("-")[0]} Price: {alerts["lowerThan"][alert]}'
                all_low_alerts.append(low_alert)
            data_full = "\n".join(all_low_alerts)
            self.data['text'] = f'Lower Than - Alerts:\n\n{data_full}'
            r.post(url=sendMessageUrl, data=self.data)
        except:
            self.data['text'] = f'Lower Than - Alerts:\n\nYou have no alerts on Lower Than'
            r.post(url=sendMessageUrl, data=self.data)

        return
    
    def stock_updates(self):
        """
        Start polling the data from the API
        """
        while True:
            try:
                stock = r.get(url=self.stock_url, params=self.querystring, headers=self.headers)

                result = stock.json()['quoteResponse']['result']

                for symbol_data in result:
                    price = symbol_data['regularMarketPrice']
                    symbol = symbol_data['symbol']
                    self.watchlist_prices[symbol] = price
            except Exception as e:
                logging.error('Something went wrong while polling the data from the API - ' + str(e))


    
    def stock_alert(self):
        """
        Check if a price match with an alert
        """
        while True:
            try:
                for watchlist_price in watchlist_prices:
                    price = float(watchlist_prices[watchlist_price])
                    for alert in self.alerts:
                        for price in self.alerts[alert]:
                            if watchlist_price in list(price.keys())[0]:
                                priceAlert = float(list(price.values())[0])
                                if alert == 'higherThan' and price > priceAlert:
                                    text = f'Price of {watchlist_price} over {priceAlert}'
                                    r.post(url=self.sendMessageUrl, data={'chat_id':self.chat_id, 'text':text})

                                elif alert == 'lowerThan' and price < priceAlert:
                                    text = f'Price of {watchlist_price} below {priceAlert}'
                                    r.post(url=self.sendMessageUrl, data={'chat_id':self.chat_id, 'text':text})
                                else:
                                    pass
            except Exception as e:
                logging.error('Something went wrong while checking the alerts - ' + str(e))


                
    def stock_set_alert(self, alert):
        """
        Set an alert
        Available keys: higherThan, lowerThan (only two at the moment)
        :param alert: Defines the alert data
        """

        alertType = alert[0]
        symbol = alert[1]
        if symbol not in self.stock_watchlist:
            self.data['text'] = 'Sorry, you can only set alerts on your watchlist\'s symbols.'
            r.post(url=sendMessageUrl, data=self.data)
            return
        else:
            pass
        try:
            price = float(alert[2])
            if 'higherThan' in alertType:
                if bool(self.alerts['higherThan']) == False:
                    self.alerts['higherThan'].append({f'1-{symbol}':price})
                else:
                    IDs = [int(list(i.keys())[-1].split('-')[0]) for i in alerts['higherThan']]
                    UID = [i for i in range(1, IDs[-1]+2) if i not in IDs][0]
                    self.alerts['higherThan'].append({f'{UID}-{symbol}':price})
            elif 'lowerThan' in alertType:
                if bool(self.alerts['lowerThan']) == False:
                    self.alerts['lowerThan'].append({f'1-{symbol}':price})
                else:
                    IDs = [int(list(i.keys())[-1].split('-')[0]) for i in alerts['lowerThan']]
                    UID = [i for i in range(1, IDs[-1]+2) if i not in IDs][0]
                    self.alerts['lowerThan'].append({f'{UID}-{symbol}':price})
            else:
                return
            self.data['text'] = f'Alert added succesfully with ID: {UID}.'
            r.post(url=sendMessageUrl, data=self.data)
            return
        except ValueError:
            self.data['text'] = 'Use: /setalert [higherThan/lowerThan] [symbol] [price]'
            r.post(url=sendMessageUrl, data=self.data)
            return

    def stock_remove_alert(self, alertType, ID):
        """
        Remove an alert
        :param alertType: Type of alert that will be removed
        :param ID: Defines the ID of the alert's that will be removed

        """
        try:
            ID = int(ID)
            if alertType == 'higherThan':
                changes = len(self.alerts['higherThan'])
                self.alerts['higherThan'] = [i for i in self.alerts['higherThan'] if ID not in list(i.keys())[0]]
                if len(self.alerts['higherThan']) != changes:
                    self.data['text'] = f'Alert with ID {ID} in {alertType} removed succesfully'
                    r.post(url=sendMessageUrl, data=self.data)
                else:
                    self.data['text'] = f'Did you type a valid ID?'
                    r.post(url=sendMessageUrl, data=self.data)
            elif alertType == 'lowerThan':
                changes = len(self.alerts['lowerThan'])
                self.alerts['lowerThan'] = [i for i in self.alerts['lowerThan'] if ID not in list(i.keys())[0]]
                if len(self.alerts['lowerThan']) != changes:
                    self.data['text'] = f'Alert with ID {ID} in {alertType} removed succesfully'
                    r.post(url=sendMessageUrl, data=self.data)
                else:
                    self.data['text'] = f'Did you type a valid ID?'
                    r.post(url=sendMessageUrl, data=self.data)
            else:
                return
            return
        except ValueError:
            self.data['text'] = 'Please, make sure yo type a valid ID'
            r.post(url=sendMessageUrl, data=self.data)
            return
            

    def add_to_watchlist(self, symbol, market):
        """
        Add a symbol to watchlist
        Markets supported: Crypto, US and MX
        :params symbol: Symbol that will be added to the watchlist
        :params market: Sets the market of the symbol
        """
        market = market.upper()

        symbol = f'{symbol}.MX' if 'MX' in market else symbol

        markets = ['CRYPTO', 'US', 'MX']

        if market in markets and symbol not in self.stock_watchlist:
            try:
                if '-USD' not in symbol and market == 'CRYPTO':
                    self.data['text'] = f'Please double check your input. For cryptocurrency: (Crypto)-USD'
                    r.post(url=sendMessageUrl, data=self.data)
                else:
                    pass
                verify = {"region":"US","symbols":symbol}
                data = r.get(url=self.stock_url, params=verify, headers=self.headers).json()
                data['result'][0]['symbol']
                self.stock_watchlist.append(symbol)
                self.data['text'] = 'Symbol added to watchlist succesfully.'
                r.post(url=sendMessageUrl, data=self.data)
            except:
                self.data['text'] = 'Couldn\'t add your symbol to watchlist, please, make sure to type it correctly.'
                r.post(url=sendMessageUrl, data=self.data)
        elif symbol in self.stock_watchlist:
            self.data['text'] = f'You already added {symbol} to your watchlist.'
            r.post(url=sendMessageUrl, data=self.data)
        else:
            self.data['text'] = f'We currently support the following markets: {", ".join(markets)}.'
            r.post(url=sendMessageUrl, data=self.data)
        return

    def remove_from_watchlist(self, symbol):
        """
        Remove a symbol from watchlist
        :params symbol: Symbol that will be removed from watchlist
        """

        if symbol in self.stock_watchlist:
            self.stock_watchlist.remove(symbol)
            self.alerts['higherThan'] = [i for i in self.alerts['higherThan'] if symbol not in list(i.keys())[0]]
            self.data['text'] = f'{symbol} succesfully removed from your watchlist.'
            r.post(url=sendMessageUrl, data=self.data)
        else:
            self.data['text'] = f'Sorry, but symbol {symbol} isn\'t in your watchlist.'
            r.post(url=sendMessageUrl, data=self.data)
        return
            

app = Flask(__name__)


def getlastMsg(msg):
    chat_id = msg['message']['chat']['id']
    text = msg['message']['text']
    return text,chat_id

@app.route('/', methods=['POST', 'GET'])
def index():
    API_KEY = '2eaf1f6336msh30851f4ab48043cp1b5dedjsn24ff7dcff0a0'
    BOT_KEY = '1588291748:AAG5qv3fB8LevoK42JkqlSKR7L-KpzLmHu8'
    if request.method == 'POST':
        msg = request.get_json()
        
        lastmsg, chat_id = getlastMsg(msg)
        if lastmsg.split()[0] == '/start':
            StockBot(BOT_KEY, API_KEY, chat_id).start_message()

        if bool(match(r'[!/]addtowatchlist [\w\W]+', lastmsg)):
            try:
                symbol = lastmsg.split()[2]
                market = lastmsg.split()[1]
            except:
                r.post(f'https://api.telegramcom/bot{BOT_KEY}/sendMessage?chat_id={chat_id}&text=Incorrect use: /addtowatchlist <market> <symbol>')
            StockBot(BOT_KEY, API_KEY, chat_id).add_to_watchlist(market, symbol)
                
        return Response('Ok', status=200)


    else:
        return '<h1>MÉTODO: GET</h1>' 
if __name__ == '__main__':
    app.run(debug=True)


        

                    

            
            




        



