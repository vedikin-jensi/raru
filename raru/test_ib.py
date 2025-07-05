from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=999)
print("Connected!")
contracts = ib.reqContractDetails(Future(symbol='CL', exchange='NYMEX'))
print("Contracts:", contracts)
ib.disconnect()