import growthstockportfolioallocator as gspa

# Load stocks from file
stocks = gspa.import_xlsx('./stocks.xlsx')

# Plot probability distributions of individual stocks
# stocks['NVO'].plot_metric_histograms()
# stocks['DE'].plot_metric_histograms()

# Form a portfolio and allocate the stock investments
portfolio = gspa.Portfolio(stocks=stocks)
portfolio.allocate(iterations=10000)
print(portfolio)
portfolio.plot_histograms()