#IMPORTS
from binance import Client
import numpy as np
import config
import time
#GLOBAL VARIABLES
client = Client(config.API_KEY, config.API_SECRET)
close_prices = []
num_Moneda1 = 0
num_Moneda2 = 0
in_position = False
tiempo_dormir = 0
string_tipo_dias_mirar = ""
#FUNCTIONS
def get_asset_balances(Moneda):
    #PRE:--
    #POST:return num moneda
    return client.get_asset_balance(Moneda).get('free')
def get_klines(string_tipo_dias_mirar,Intervalo_Kline,tipo_tiempo,Mercado):
    #PRE:--
    #POST: return list of close price
    close_prices = []
    data = float(client.get_historical_klines(Mercado, str(Intervalo_Kline)+tipo_tiempo, string_tipo_dias_mirar))
    for x in range(len(data)):
      close_prices.append(float(data[x][4])) #append the price of vec
    return close_prices
def order(side, quantity, symbol,order_type=Client.ORDER_TYPE_MARKET):
    #PRE:side is "SIDE_SELL" or "SIDE_BUY", quantity is bigger or equal than 0 and smaller than number of currency in the account and symbol is valid
    #POST:Sends the order of BUY or SELL 
    try:
        print("Enviando orden")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("ERROR - {}".format(e))
        return False
    return True
def mooving_avarage(close_prices):
    #PRE: --
    #POST: return mooving avarage of close_prices
    x = np.array(close_prices)
    w = len(close_prices);
    return np.convolve(x, np.ones(w), 'valid') / w
def calcular_tiempo_dormir(tipo_tiempo,Intervalo_Kline):
    #PRE: tipo tiempo = 'm' or 'h' or 'd' or 'w' or 'M' i intervalo >0
    #POST: return tiempo dormir
    if tipo_tiempo == 'm':
        return Intervalo_Kline*60
    elif tipo_tiempo == 'h':
        return Intervalo_Kline*3600
    elif tipo_tiempo == 'd':
        return Intervalo_Kline*3600*24
    elif tipo_tiempo == 'w':
        return Intervalo_Kline*3600*24*7
    elif tipo_tiempo == 'M':
        return Intervalo_Kline*3600*24*30
def calcular_dias_mirar(tipo_tiempo_mirar,tiempo_mirar):
	#PRE:tipo tiempo mirar = 'm' or 'd' i tiempo_mirar>0
	#POST: return string UTC FORMAT
	if tipo_tiempo_mirar == 'm':
			return str(tiempo_mirar)+" day ago UTC"
	elif tipo_tiempo_mirar == 'd':
			return str(tiempo_mirar)+" minute ago UTC"
#MAIN
print("*************************************************************")
Moneda1 = input("Introducir criptomoneda: ")
Moneda2 = input("Introducir moneda base: ")
num_Moneda1 = get_asset_balances(Moneda1)
num_Moneda2 = get_asset_balances(Moneda2)
print("Tienes "+str(num_Moneda1)+" de "+ Moneda1+" y "+str(num_Moneda2) +" de "+ Moneda2)
Venta = float(input("Introduir cuanto tanto por 1 de monedas vender (ex: 20%= 0.2): "))
Compra = float(input("Introducir cuanto tanto por 1 de monedas comprar (ex: 20%=0.2): "))
Porcentage_venta = float(input("Introducir el tanto por 1 de diferencia entre MA y precio para vender(ex: 20% = 0.2): "))
Porcentage_compra = float(input("Introducir el tanto por 1 de diferencia entre MA y precio para comprar(ex: 20% = 0.2): "))            
Mercado = Moneda1+Moneda2
tipo_tiempo = input("Introducir letra segun el tipo de tiempo del candlebar: 'm'= minutos, 'h'=hora,'d'=dia,'w'=semana,'M'=mes: ")
Intervalo_Kline = int(input("Introducir la cantidad de tipo de la letra anterior quieres que sean los candlebars: "))
tipo_tiempo_mirar = input("Introducir 'd' si quieres que mirar dias, 'm' si quieres mirar minutos: ")
tiempo_mirar = int(input("Introducir la cantidad de tiempo de la letra anterior que se quiere mirar: "))
print("*************************************************************")
while True:
    num_Moneda1 = get_asset_balances(Moneda1)
    num_Moneda2 = get_asset_balances(Moneda2)
    print("Tienes "+str(num_Moneda1)+" de "+ Moneda1+" y "+str(num_Moneda2) +" de "+ Moneda2)
    tiempo_dormir = calcular_tiempo_dormir(tipo_tiempo,Intervalo_Kline)
    string_tipo_dias_mirar = calcular_dias_mirar(tipo_tiempo_mirar,tiempo_mirar)
    close_prices = get_klines(string_tipo_dias_mirar,Intervalo_Kline,tipo_tiempo,Mercado)
    MA = mooving_avarage(close_prices)[0]
    price_Moneda1 = float(client.get_avg_price(symbol=Mercado)['price'])
    if price_Moneda1 > Porcentage_venta*MA+MA:
        if num_Moneda1 == "0":
            print("No hay "+Moneda1+" en la wallet para vender")
        else:
            order(Client.SIDE_SELL, num_Moneda1 * Venta, Mercado)
            print("Vendiendo "+Moneda1+" A {}".format(price_Moneda1))
    elif price_Moneda1*Porcentage_compra+price_Moneda1 < MA:
        if num_Moneda2 == "0":
            print("No hay "+Moneda2+" en la wallet para comprar")
        order(Client.SIDE_BUY, Compra*Moneda2/price_Moneda1,Mercado)
        print("Comprando "+Moneda1+" A {}".format(price_Moneda1))
    else:
        print("NI COMPRA NI VENTA")
        print("La moneda 1 vale {}".format(price_Moneda1))
        print("El MA vale {}".format(MA))
    #time.sleep(tiempo_dormir)

