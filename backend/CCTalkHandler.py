from cctalk.coin_messenger import CoinMessenger
from cctalk.tools import make_serial_object
from helpers.Config import Config
import time

class CCTalkHandler:
    def __init__(self):
        self.connected = False

    def listenThrowIn(self, callback):
        while self.connected:
            coinType = self.getCoinType()
            if(coinType != None):
                callback(coinType)
            time.sleep(0.1)
    
    def connect(self):
        serial = Config.get('/CCTalk/serial')
        self.connection = make_serial_object(serial)
        self.connected = self.connection.isOpen()
        self.messenger = CoinMessenger(self.connection)
        self.resetDevice()

    def disconnect(self):
        self.connected = False
        self.blockCoins()
        self.connection.close()

    def resetDevice(self):
        self.messenger.request('reset_device', verbose=False)

    def acceptCoins(self):
        self.messenger.accept_coins(True, verbose=False)

    def blockCoins(self):
        self.messenger.accept_coins(False, verbose=False)

    def getCoinType(self):
        self.acceptCoins()
        coins = {
            1: 0.05, 
            2: 0.1, 
            3: 0.2, 
            4: 0.5, 
            5: 1, 
            6: 2
        }
        buffer = self.messenger.read_buffer(verbose=False)
        
        data = buffer[1]
        error = buffer[2]
        if error != 0:
            return None
        else:
            if(data != 0):
                coinType = coins[data]
                self.resetDevice()
                return coinType
            else:
                return None