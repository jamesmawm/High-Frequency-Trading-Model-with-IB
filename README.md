Purpose
====================================
This project is intended for recruiters, headhunters and hiring managers in evaluating my proficiency in Python and looking to fill entry-level roles in automated trading strategies development, quantitative trading or developer or analyst or researcher, high-frequency trading systems, data analyst or visualization, or model validation.

Requirements
====================================
- An Interactive Brokers account with TWS or API gateway (tested with demo account)
- IbPy at https://github.com/blampe/IbPy
- Pandas
- NumPy

Key Concepts
====================================
At the present moment, this model trades on statistical arbitrage based on these methodologies:
- Transforming inhomogenous to homogeneous time series of 1 second intervals
- Mean-reversion of highly-correlated stock pairs
- Using Volatility ratio to detect trending or Brownian motion
- Fair valuation by using beta of average 5 minutes look-back price window
- Fair valuation against more than 1 security is possible

Other functionalities:
- Generate trade signals and place buy/sell orders on every incoming tick
- Re-evaluating beta every 30 seconds to account for small regime shifts

And greatly inspired by these papers:
- MIT: Developing high-frequency equities trading model 
  @ http://dspace.mit.edu/handle/1721.1/59122
- SMU: Profiting from mean-reverting yield-curve trading strategies
  @ http://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=3488&context=lkcsb_research

Future Enhancements
====================================
I would love to extend this model given sufficient time:
- Extending to more than 2 securities and trade on optimum prices
- Generate more trade signals based on corrleation and co-integration
- Using PCA for next-period evaluation
- Back-testing with zipline
- Maybe include vector auto-regressions
