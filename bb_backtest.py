import pandas as pd
import pandas_ta as ta
import numpy as np

#This strategy is a BollingerBands Arbitrage Strategy. It does not set StopLosses because the exit is price-adjusted. Therefore the Winrate is high – nevertheless you have a extreme high drawdown/return ratio. Moreover arbitrage strategies extremely rely on comission, spread and swap fees which are not modeled within this backtest.

class Backtest:
    def __init__(self,file,rtr=10000):
        self.exec = self._load_data(file)
        self.rtr = rtr #capital used per trade
        self.trades = pd.DataFrame(columns=['time','type','entry','exit','pnl','dd'])

    def _load_data(self,file):
        try:
            self.df = pd.read_csv(file,index_col=0,parse_dates=True).head(500000)
        except FileNotFoundError:
            return False
        
        self.df = self.df.between_time('07:00','15:59') #highest Volume, biggest deviations: NY premarket - NY close
        return True
    
    def trade(self,time,type,entry,exit,dd):
        idx = len(self.trades) if not self.trades.empty else 0
        self.trades.loc[idx,'time'] = time
        self.trades.loc[idx,'type'] = type
        self.trades.loc[idx,'entry'] = entry
        self.trades.loc[idx,'exit'] = exit
        self.trades.loc[idx,'dd'] = dd*self.rtr
        
        if type == 'long':
            self.trades.loc[idx,'pnl'] = (exit-entry)* (self.rtr/entry)
        elif type == 'short':
            self.trades.loc[idx,'pnl'] = (entry-exit)* (self.rtr/entry)
    
    def backtest(self,bb_length=26,bb_std=2.2):
        bb_length = int(bb_length)
        bb_std = float(bb_std)
        
        for day, ddf in self.df.groupby(self.df.index.date):
            if len(ddf.dropna()) < 539: #9h
                continue
            # bollinger bands
            bband = ta.bbands(close=ddf['Close'],length=bb_length,std=bb_std)
            bb_high = bband[f'BBU_{bb_length}_{bb_std}']
            bb_low = bband[f'BBL_{bb_length}_{bb_std}']
            bb_mid = bband[f'BBM_{bb_length}_{bb_std}']
            
            d = pd.concat([ddf,bb_high.rename('bb_high'),bb_low.rename('bb_low'),bb_mid.rename('bb_mid')],join='inner',axis=1).dropna(axis=0) 
            # defaults
            in_trade = False
            direction = None
            dd = {'price':np.NaN,'pct':np.NaN}
            
#entry on the mean, when price is squeezed and is likely to deviate
#underlying thesis: price is moving like a sine-wave around the mean >> Brownian Motion
            
            for time,line in d.iterrows():
            
                if in_trade == False: #entry
                    if line.loc['Close'] > line.loc['bb_mid']: 
                        entry = line.loc['Close']
                        direction = 'long'
                        in_trade = True
                    elif line.loc['Close'] < line.loc['bb_mid']:
                        entry = line.loc['Close']
                        direction = 'short'
                        in_trade = True
                        
                else: #check weather to exit
                    if direction == 'long': #long exit
                        if line.loc['High'] >= line.loc['bb_high']:
                            exit = line.loc['High']
                            self.trade(time,direction,entry,exit,dd['pct']) #save trade
                            #back to default
                            in_trade = False
                            direction = None
                            dd['price'] = np.NaN
                            dd['pct'] = np.NaN
                        else: #check for new max drawdown
                            if not np.isnan(dd['price']): #if previous drawdown
                                if line.loc['Low'] < dd['price']: #current < old?
                                    dd['price'] = line.loc['Low']
                                    dd['pct'] = line.loc['Low']/entry-1
                            else:
                                dd['price'] = line.loc['Low']
                                dd['pct'] = line.loc['Low']/entry-1
                                
                    elif direction == 'short': #short exit
                        if line.loc['Low'] <= line.loc['bb_low']:
                            exit = line.loc['Low']
                            self.trade(time,direction,entry,exit,dd['pct']) #save trade
                            #back to default
                            in_trade = False
                            direction = None
                            dd['price'] = np.NaN
                            dd['pct'] = np.NaN
                        else: #check for new max drawdown
                            if not np.isnan(dd['price']): #if previous drawdown
                                if line.loc['High'] > dd['price']: #current > old?
                                    dd['price'] = line.loc['High']
                                    dd['pct']= entry/line.loc['High']-1
                            else:
                                dd['price'] = line.loc['High']
                                dd['pct'] = entry/line.loc['High']-1
                            
    def evaluate(self):
        pnl = self.trades['pnl'].sum()
        ntrades = len(self.trades)
        avg_dd = self.trades['dd'].dropna().mean()
        avg_pnl = self.trades['pnl'].mean()
        print(f'PnL({ntrades}): {round(pnl,0)}$')
        print(f'Risk(1): {self.rtr}$')
        print(f'PnL(1): {round(avg_pnl,2)}$')
        print(f'DD(1): {round(avg_dd,2)}$')
        
    def __call__(self):
        if self.exec:
            self.backtest()
            self.evaluate()
            
if __name__ == '__main__':
    bt = Backtest('NQ_OHLC_1m.csv')
    bt()