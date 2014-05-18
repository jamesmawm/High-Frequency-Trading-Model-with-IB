Purpose
====================================
These files are intended for recruiters, headhunters and hiring managers in evaluating my proficiency in Python and looking to fill entry-level roles in automated trading strategy development, quantitative trading/developer/analyst/researcher, portfolio management/analyst, high-frequency trading, data analyst/visualization, and model validation.

Requirements
====================================
- An Interactive Brokers account with TWS/API gateway
- IbPy @ https://github.com/blampe/IbPy
- Pandas
- NumPy

Key Concepts
====================================
At the present moment, this model utilizes statistical arbitrage incorporating these methodologies:
- Bootstrap the model with historical data to derive usable strategy parameters
- Bootstrapping takes some time, we need to bridge historical data with recent tick data
- Transforming inhomogenous to homogeneous time series of 1 second intervals
- Selection of highly-correlated stock pairs
- Using volatility ratio to detect trending, mean-reversion or Brownian motion
- Fair valuation by using beta of average 5 minute look-back price window
- Fair valuation of stock A against more than 1 security (stock B, C...) is possible
- Make trade decisions based on mean-reversion, volatility ratio and deviation from fair prices

Other functionalities:
- Generate trade signals and place buy/sell orders based on every incoming tick data
- Re-evaluating beta every 30 seconds to account for small regime shifts

And greatly inspired by these papers:
- MIT - Developing high-frequency equities trading model 
  @ http://dspace.mit.edu/handle/1721.1/59122
- SMU - Profiting from mean-reverting yield-curve trading strategies
  @ http://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=3488&context=lkcsb_research

Future Enhancements
====================================
I would love to extend this model in the unforeseeable future:
- Extending to more than 2 securities and trade on optimum prices
- Generate trade signals based on correlation and co-integration
- Using PCA for next-period evaluation
- Back-testing with zipline
- Maybe include vector auto-regressions
- Account for regime shifts (trending or mean-reverting states)
- Account for structural breaks
- Using EMA kernels instead of a rectangular one
- Use and store rolling betas and standard deviations
- Add in alphas(P/E, B/P ratios) and Kalman filter prediction
- Storaging of tick data in MongoDb for future back-tests.

What It Can Do
=========================
- Establish connection to broker and request for tick data
- Generate trade signals on each incoming tick
- Open position with buy/sell orders, and reverse position
- Lose money

What It Cannot Do
=========================
- Make money

Final Notes
========================
- I haven't come across any complete high-frequency trading model except those I've created, so here's one to get started off the ground and running.
- Created in two weeks while dealing with final exams, job search, part-time internship and pet projects. Please forgive on sub-standard quality.
- This model has never been tested with a real account. All testing done in demo account only.
- The included strategy parameters is likely to lose money than to make money.
- If you know of anyone who might be interested to offer a job (i.e paid salary), please pass these links around with thanks.
- I do have the right to work in the United States on OPT work visa, hopefully from June 01 2014 onwards (or when I receive my EAD card). 

Email stuff here: jamesmawm@gmail.com
