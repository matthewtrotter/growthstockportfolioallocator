# Growth Stock Portfolio Allocator
A tool that allocates growth stocks in a portfolio

## Usage
1. Define a portfolio of stocks.
2. Run the allocator.

Example:
```python
import growthstockportfolioallocator as gspa

# Load stocks from file
stocks = gspa.import_xlsx('./stocks.xlsx')

# Plot probability distributions of individual stocks
stocks['AAPL'].plot_stats()
stocks['SBUX'].plot_stats()

# Form a portfolio and allocate the stock investments
portfolio = gspa.portfolio(stocks=stocks)
portfolio.allocate_by_confidence(iterations=10000)
print(portfolio)
portfolio.plot_by_confidence()
```

