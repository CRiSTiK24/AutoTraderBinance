from binance import Client
import config
client = Client(config.API_KEY, config.API_SECRET)
Intervalo_Kline = 15
tipo_tiempo = "m"
string_tipo_dias_mirar = "240 minute ago UTC"
Mercado = "EOSUSDT"
close_prices = []
for x in range(16):
	close_prices.append(client.get_historical_klines(Mercado, str(Intervalo_Kline)+tipo_tiempo, string_tipo_dias_mirar)[x][4])
print(close_prices)