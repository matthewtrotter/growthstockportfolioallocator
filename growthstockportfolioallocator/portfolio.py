from .stock import *
import numpy as np
import pandas as pd
from typing import Dict


class Portfolio:
    """Form a portfolio of growth stocks
    """

    def __init__(self, stocks:Dict[str, Stock]) -> None:
        self.stocks = stocks
        self.mean_allocations = None

    def _allocate_once(self) -> Dict[str, float]:
        """Allocate portfolio weights once

        Returns
        -------
        Dict[str, float]
            stock: portfolio weight
        """
        allocations = {}
        ratios = {}
        for stock in self.stocks.keys():
            growth, value, ratio = self.stocks[stock].roll_once()
            ratios[stock] = ratio
        
        sum_ratios = np.sum(list(ratios.values()))
        for stock in self.stocks.keys():
            allocations[stock] = ratios[stock]/sum_ratios

        return allocations

    
    def allocate(self, iterations:int = 10000) -> None:
        self.allocation_trials = pd.DataFrame(
            data=np.zeros((iterations, len(self.stocks))),
            columns=list(self.stocks.keys())
        )

        for i in range(iterations):
            self.allocation_trials.iloc[i, :] = self._allocate_once()
        
        self.mean_allocations = self.allocation_trials.mean()
    
    
    def plot_histograms(self) -> None:
        """Plot histograms of allocation percentages.
        """
        fig = go.Figure()
        for stock in self.stocks.keys():
            fig.add_trace(go.Histogram(
                x=self.allocation_trials[stock].to_numpy(), 
                histnorm='probability density',
                name=stock
                ))

        # Overlay both histograms
        fig.update_layout(barmode='overlay')
        # Reduce opacity to see both histograms
        fig.update_traces(opacity=0.6)
        fig.show()


    
    def __repr__(self) -> str:
        if isinstance(self.mean_allocations, pd.Series):
            return str(self.mean_allocations)
        return 'Portfolio'
    
