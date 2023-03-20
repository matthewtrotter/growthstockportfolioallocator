from os import PathLike
import numpy as np
import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots
# import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple


class Stock:
    """Holds all the input data and calculations of a stock.
    """

    def __init__(self, row:pd.Series) -> None:
        self.stock = row['Stock']
        self.industry = row['Industry']
        self.ms_moat = row['MS Moat']
        self.ms_moat_trend = row['MS Moat Trend']
        self.ms_capital_allocation = row['MS Capital Allocation']
        self.us_equities_exp_real_return_10y = row['Research Affiliates 10-year Expected Real Return of US Large Equities']/100
        self.us_treasury_note_risk_free_yield_10y = row['10-Year Treasury Note Risk-Free Yield']/100
        self.beta = row['Beta']
        self.common_shares_outstanding = row['Common Shares Outstanding (M)']*1e6
        self.tax_rate = row['Tax Rate']/100
        self.long_term_interest_payment = row['LT Interest ($M)']*1e6
        self.long_term_debt_balance = row['LT Debt ($M)']*1e6
        self.preferred_dividend = row['Pfd Div’d ($M)']*1e6
        self.preferred_stock = row['Pfd Stock ($M)']*1e6
        self.vl_cash_flow_per_share = row['VL Cash Flow Per Share']
        self.vl_earnings_predictability = row['VL Earnings Predictability']/100
        self.vl_return_on_total_capital = row['VL ROTC']/100
        self.vl_retained_earnings_plowback_ratio = row['VL Retained to Com Eq (Plowback Ratio)']/100
        self.price = row['Current Price']

        self._derive_distributions()
        self._calculate_wacc()


    def _derive_distributions(self) -> None:
        """Derive the distribution properties based on the user input.
        """
        self.vl_cash_flow_per_share_std_dev = (0.50 - 0.45*self.vl_earnings_predictability)*self.vl_cash_flow_per_share
        self.vl_return_on_total_capital_std_dev = (0.50 - 0.45*self.vl_earnings_predictability)*self.vl_return_on_total_capital
        self.vl_retained_earnings_plowback_ratio_std_dev = (0.50 - 0.45*self.vl_earnings_predictability)*self.vl_retained_earnings_plowback_ratio


    def _calculate_wacc(self) -> None:
        """Calculate the weighted average cost of capital (WACC)
        """
        # Cost of debt
        after_tax_historical_cost_of_debt = 0
        if self.long_term_debt_balance > 0:
            after_tax_historical_cost_of_debt = (self.long_term_interest_payment/self.long_term_debt_balance)*(1-self.tax_rate)

        # Cost of preferred equity
        cost_of_preferred_equity = 0
        if self.preferred_stock > 0:
            cost_of_preferred_equity = self.preferred_dividend/self.preferred_stock
        
        # Cost of equity
        cost_of_equity = self.us_treasury_note_risk_free_yield_10y + self.beta*self.us_equities_exp_real_return_10y

        # Cost of capital
        total_capital = self.long_term_debt_balance + self.preferred_stock + self.common_shares_outstanding*self.price
        self.weighted_average_cost_of_capital = (after_tax_historical_cost_of_debt*self.long_term_debt_balance + cost_of_preferred_equity*self.preferred_stock + cost_of_equity*self.common_shares_outstanding*self.price)/total_capital


    def roll_once(self) -> Tuple[float, float, float]:
        """Randomly calculate the Operating Profit Growth Rate and Price/Cash Flow from the statistics of the stock.

        Returns
        -------
        Tuple[float, float]
            Operating Profit Growth Rate, Price/Cash Flow, ratio of growth/(price/cashflow)
        """
        rotc = np.random.normal(self.vl_return_on_total_capital, self.vl_return_on_total_capital_std_dev)
        plowback_ratio = np.random.normal(self.vl_retained_earnings_plowback_ratio, self.vl_retained_earnings_plowback_ratio_std_dev)
        plowback_ratio = np.clip(plowback_ratio, 0, 1)
        excess_return_on_total_capital = rotc - self.weighted_average_cost_of_capital
        operating_profit_growth_rate = 100*excess_return_on_total_capital*plowback_ratio

        cash_flow = np.random.normal(self.vl_cash_flow_per_share, self.vl_cash_flow_per_share_std_dev)
        price_to_cash_flow = self.price/cash_flow

        ratio = operating_profit_growth_rate/price_to_cash_flow

        return (operating_profit_growth_rate, price_to_cash_flow, ratio)


    def plot_metric_histograms(self, iterations:int = 10000) -> None:
        """Plot histograms of Operating Profit Growth Rate and Price/Cash Flow
        """
        # Calculate statistics

        values_df = pd.DataFrame(data=np.zeros((iterations, 3)), columns=['Operating Profit Growth Rate', 'Price/Cash Flow', 'Value Ratio'])
        for i in range(iterations):
            values_df.loc[i, 'Operating Profit Growth Rate'], values_df.loc[i, 'Price/Cash Flow'], values_df.loc[i, 'Value Ratio'] = self.roll_once()


        fig = make_subplots(rows=1, cols=3,
                            subplot_titles=('Operating Profit Growth Rate (%)', 'Price/Cash Flow', 'Value Ratio'))

        fig.add_trace(
            # px.histogram(values_df, x="Operating Profit Growth Rate", histnorm='probability density'),
            go.Histogram(y=values_df['Operating Profit Growth Rate']),
            row=1, col=1
        )

        fig.add_trace(
            go.Histogram(y=values_df['Price/Cash Flow']),
            row=1, col=2
        )

        fig.add_trace(
            go.Histogram(y=values_df['Value Ratio']),
            row=1, col=3
        )

        fig.update_layout(title_text=self.stock)
        fig.show()



def import_xlsx(f: PathLike) -> Dict[str, Stock]:
    """Import an XLSX file and return a dictionary of Stock objects.

    Parameters
    ----------
    f : PathLike
        path to the XLSX file

    Returns
    -------
    Dict[Stock]
    """
    # Import the data
    data = pd.read_excel(f)

    # Make dictionary of stocks
    stocks = {row['Stock']: Stock(row) for _, row in data.iterrows()}

    return stocks