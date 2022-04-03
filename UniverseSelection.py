class ParticleDynamicFlange(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 5, 11)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        # self.AddEquity("SPY", Resolution.Minute)
        # tickers = 
        
        
        self.AddUniverseSelection(
           FineFundamentalUniverseSelectionModel(self.SelectCoarse, self.SelectFine)
        )

    def SelectCoarse(self, coarse):
        tickers = ['FB', 'AMZN', 'NFLX', 'GOOG']
        return [Symbol.Create(x, SecurityType.Equity, Market.USA) for x in tickers]
    
    def SelectFine(self, fine):
        return [f.Symbol for f in fine]
        #print(f.Symbol for in fine)


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''

        # if not self.Portfolio.Invested:
        #    self.SetHoldings("SPY", 1)
