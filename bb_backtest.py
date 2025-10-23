import pandas as pd
import pandas_ta as ta
import numpy as np

#This strategy is a BollingerBands Arbitrage Strategy. It does not set StopLosses because the exit is price-adjusted. Therefore the Winrate is high – nevertheless you there is an extreme high drawdown/return ratio. Moreover arbitrage strategies extremely rely on comission, spread and swap fees which have huge impact on the outcome.

class Backtest:
    def __init__(self,file,rtr=10000):
        self.exec = self._load_data(file)
        self.rtr = rtr #capital used per trade
        self.trades = pd.DataFrame(columns=['entrytime','exittime','duration','type','entry','exit','pnl','dd'])

    def _load_data(self,file):
        try:
            self.df = pd.read_csv(file,index_col=0,parse_dates=True).head(500000)
        except FileNotFoundError:
            return False
        
        self.df = self.df.between_time('08:00','15:59') #highest Volume, biggest deviations: NY premarket - NY close
        return True
    
    def trade(self,entrytime,exittime,type,entry,exit,dd,fees=0.0003): # 0.03% loss through comissions/slippage
        idx = len(self.trades) if not self.trades.empty else 0
        self.trades.loc[idx,'entrytime'] = entrytime.time()
        self.trades.loc[idx,'exittime'] = exittime.time()
        self.trades.loc[idx,'duration'] = (exittime.time().hour*60+exittime.time().minute)-(entrytime.time().hour*60+entrytime.time().minute)
        self.trades.loc[idx,'type'] = type
        self.trades.loc[idx,'entry'] = entry
        self.trades.loc[idx,'exit'] = exit
        self.trades.loc[idx,'dd'] = dd*self.rtr+self.rtr*fees
        
        if type == 'long':
            self.trades.loc[idx,'pnl'] = (exit-entry)* (self.rtr/entry)-self.rtr*fees
        elif type == 'short':
            self.trades.loc[idx,'pnl'] = (entry-exit)* (self.rtr/entry)-self.rtr*fees
    
    def backtest(self,bb_length=20,bb_std=2,atr_length=9):
        bb_length = int(bb_length)
        bb_std = float(bb_std)
        
        for day, ddf in self.df.groupby(self.df.index.date):
            if len(ddf.dropna()) < 479: #8h
                continue
            # bollinger bands
            bband = ta.bbands(close=ddf['Close'],length=bb_length,std=bb_std)
            bb_high = bband[f'BBU_{bb_length}_{bb_std}']
            bb_low = bband[f'BBL_{bb_length}_{bb_std}']
            bb_mid = bband[f'BBM_{bb_length}_{bb_std}']
            # average true range
            atr = ta.atr(high=ddf['High'],low=ddf['Low'],close=ddf['Close'],length=int(atr_length))
            
            d = pd.concat([ddf,bb_high.rename('bb_high'),bb_low.rename('bb_low'),bb_mid.rename('bb_mid'),atr.rename('atr')],join='inner',axis=1).dropna(axis=0) 
            # defaults
            in_trade = False
            direction = None
            dd = {'price':np.NaN,'pct':np.NaN}
            atr_d_thres = d['atr'].rolling(14).mean() #atr threshold for avoiding low volatility ranges

#entry on the mean, when price is squeezed and is likely to deviate
#underlying thesis: price is moving like a sine-wave around the mean >> Brownian Motion
            
            for time,line in d.iterrows():
            
                if in_trade == False: #entry
                    if line.loc['atr'] > atr_d_thres.loc[time] and not np.isnan(atr_d_thres[time]):
                        if line.loc['Close'] > line.loc['bb_mid']: 
                            entry = line.loc['Close']
                            direction = 'long'
                            in_trade = True
                            entry_time = time
                        elif line.loc['Close'] < line.loc['bb_mid']:
                            entry = line.loc['Close']
                            entry_time = time
                            direction = 'short'
                            in_trade = True
                        
                else: #check wether to exit
                    if direction == 'long': #long exit
                        if line.loc['High'] >= line.loc['bb_high']:
                            exit = line.loc['High']
                            self.trade(entry_time,time,direction,entry,exit,dd['pct']) #save trade
                            #back to default
                            in_trade = False
                            direction = None
                            dd['price'] = np.NaN
                            dd['pct'] = np.NaN
                        else: #check for new max drawdown
                            if not np.isnan(dd['price']): #if previous drawdown
                                if line.loc['Low'] < dd['price']: #current < old?
                                    dd['price'] = line.loc['Low']
                                    dd['pct'] = abs(entry/line.loc['Low']-1)
                            else:
                                dd['price'] = line.loc['Low']
                                dd['pct'] = abs(entry/line.loc['Low']-1)
                                
                    elif direction == 'short': #short exit
                        if line.loc['Low'] <= line.loc['bb_low']:
                            exit = line.loc['Low']
                            self.trade(entry_time,time,direction,entry,exit,dd['pct']) #save trade
                            #back to default
                            in_trade = False
                            direction = None
                            dd['price'] = np.NaN
                            dd['pct'] = np.NaN
                        else: #check for new max drawdown
                            if not np.isnan(dd['price']): #if previous drawdown
                                if line.loc['High'] > dd['price']: #current > old?
                                    dd['price'] = line.loc['High']
                                    dd['pct']= abs(line.loc['High']/entry-1)
                            else:
                                dd['price'] = line.loc['High']
                                dd['pct'] = abs(line.loc['High']/entry)-1
                            
    def evaluate(self):
        pnl = self.trades['pnl'].sum()
        ntrades = len(self.trades)
        avg_dd = self.trades['dd'].dropna().mean()
        avg_pnl = self.trades['pnl'].mean()
        print(f'PnL({ntrades}): {round(pnl,0)}$')
        print(f'Risk(1): {self.rtr}$')
        print(f'PnL(1): {round(avg_pnl,2)}$')
        print(f'DD(1): {round(avg_dd,2)}$')
        print(f'Duration(1):',round(self.trades['duration'].mean(),2),'min')
        
    def __call__(self):
        if self.exec:
            self.backtest()
            self.evaluate()
            
if __name__ == '__main__':
    bt = Backtest('NQ_OHLC_1m.csv')
    bt()
