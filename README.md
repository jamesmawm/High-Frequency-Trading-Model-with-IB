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
- MIT - Developing high-frequency equities trading model 
  @ http://dspace.mit.edu/handle/1721.1/59122
- SMU - Profiting from mean-reverting yield-curve trading strategies
  @ http://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=3488&context=lkcsb_research

Future Enhancements
====================================
I would love to extend this model in the unforeseeable future:
- Extending to more than 2 securities and trade on optimum prices
- Generate more trade signals based on corrleation and co-integration
- Using PCA for next-period evaluation
- Back-testing with zipline
- Maybe include vector auto-regressions
- Account for regime shifts (trending or mean-reverting states)
- Account for structureal breaks
- Using EMA kernels instead of a rectangular one
- Use and store rolling betas and standard deviations
- Add in alphas and Kalman filter predictions

What It Can Do
=========================
- Establish connection to broker and request for tick data
- Generate trade signals on each incoming tick
- Place buy/sell orders to a demo account
- Lose money

What It Cannot Do
=========================
- Make money


Final Notes
========================
- I haven't come across any real or full high-frequency trading model except those I've created, so here's one to get started off the ground and running
- This model has never been tested with a real account. All testing done in demo account only.
- The included strategy parameters is likely to lose money than to make money
- If you know of anybody who might be interested to offer a job (i.e paid salary), pass these links around with thanks
- I do have the right to work in the United States on OPT work visa, hopefully from June 01 2014 onwards (or when I receive my EAD card). 

Email stuff here: jamesmawm@gmail.com
