unitMap = {
    'wei':          1,
    'mwei':         1e6,
    'gwei':         1e9,
    'szabo':        1e12,
    'finney':       1e15,
    'ETH':          1e18,
    'CMT':          1e18
}

def toWei(x, units):
    return x * unitMap[units]

def fromWei(x, units):
    return x / unitMap[units]

class UsdEthConverter:
    def __init__(self, usdPerEth, roundDigits=None):
        self.usdPerEth = usdPerEth
        self.roundDigits = roundDigits

    def round(self, x):
        if (self.roundDigits != None):
            return round(x, self.roundDigits)
        return x

    def toEth(self, usd):
        return self.round(usd/self.usdPerEth)

    def fromEth(self, eth):
        return self.round(eth*self.usdPerEth)

class Market:
    # pass params as dictionary
    def __init__(self, params):
        for key, value in params.items():
            setattr(self, key, value)
        self.reserve = 0 # total Ether in wei
        self.market_total = 0 # total CMT in wei
        self.reserve_payment = 100 - self.maker_payment - self.backend_payment

    # Note units returned is ETH-wei per billion CMT-wei
    def get_support_price(self):
        return self.price_floor + ((self.spread * self.reserve * 1e9) // (100 * self.market_total))

    # Human readable support price in ETH per CMT
    def get_human_support_price(self):
        return self.get_support_price() / 1e9

    # ETH per CMT
    def get_withdraw_price(self):
        return self.reserve / self.market_total

    # Units is ETH!
    def support(self, offer_eth):
        offer = toWei(offer_eth, 'ETH')
        support_price = self.get_support_price()
        minted = (offer // support_price) * 1e9 # note GWEI multiplier

        self.market_total += minted
        self.reserve += offer
    
    # differs from contracts in allowing a specified withdraw amount in
    # whole CMT units. This is to simplify simulation so that we don't
    # have to keep track of a coin table.
    def withdraw(self, amount_cmt):
        amount = toWei(amount_cmt, 'CMT')
        withdraw_proceeds = (amount * self.reserve) // self.market_total
        
        self.market_total -= amount
        self.reserve -= withdraw_proceeds

    # simulate some data being listed
    def list(self):
        self.market_total += self.list_reward

    def buy(self, megabytes):
        _bytes = megabytes * 1e6
        cost = self.cost_per_byte * _bytes
        reserve_share = cost * (self.reserve_payment/100)
        self.reserve += reserve_share
        
    def log(self):
        support_price = round(self.get_human_support_price(), 4)
        withdraw_price = round(self.get_withdraw_price(), 4)
              
        print(f"{round(fromWei(self.market_total, 'CMT'), 1)} CMT")
        print(f"{round(fromWei(self.reserve, 'ETH'), 1)} ETH")
        print(f"Support at {support_price} ETH per CMT")
        print(f"Withdraw at {withdraw_price} ETH per CMT")
        print("")