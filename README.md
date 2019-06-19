Purpose
===
A simple trading equity trading model on Interactive Brokers' API dealing with (pseudo) high-frequency data studies.

![alt text](https://github.com/jamesmawm/High-Frequency-Trading-Model-with-IB/blob/master/output/run_02_screenshot.png?raw=true "Chart output")

Requirements
===

- Python 3.7
- IB Trader Workstation Build 973.2
- IB paper or live trading account
- (Optional) Docker and docker-compose

What's New
===

*19 Jun 2019*

- Version 3.0 released
- `ibpy` library is dropped in favour of the newer `ib_insync` library.
- The same code logic is ported over to use the features of `ib_insync`, compatible with Python 3.7. Includes various code cleanup.
- Dropped `matplotlib` charting in favour of headless running inside Docker.


*14 Jun 2019*

- Version 2.0 released
- Merged pull request from: https://github.com/chicago-joe/IB_PairsTrading_Algo
    
    Thanks to chicago-joe for updating to work with Python 3.
    
    As this is only a compatibility update, there are many outdated components and the trading model is quite unlikely to be working as intended.
    

*8 Jun 2015*
- Version 1.0 released
- Refactor and conform to PEP8 standards
- New chart display with 4 subplots


Setting up
===

## Running on a local Python console 

Steps to run the trading model on your command line:

- Within a Python 3.7 environment, install the requirements:
    
        pip install -r requirements.txt

- In IB Trader Workstation (TWS), go to **Configuration** > **Api** > **Settings** and:

    - enable ActiveX and Socket Clients
    - check the port number you will be using
    - If using Docker, uncheck **Allow connections from localhost only** and enter the machine IP running TWS to **Trusted IPs**.

- Update `main.py` with the required parameters and run the model with the command:

        python main.py
    
## Running from a Docker container

A Docker container helps to automatically build your running environment and isolate changes, all in just a few simple commands!
You can run this trading model in headless model remotely with the following steps:

- Ensure your machine has docker and docker-compose installed. Build a running image:

        docker-compose build
        
- Update the parameters in `docker-compose.yml`. I've set the `TWS_HOST` value in my environment variables. This is the IP address of my remote machine running TWS. Or, you can just manually enter the IP address value directly there. Then, run the image as a container:

        docker-compose up
        
    To run  in headless mode, simple add the detached command `-d`, like this:
    
        docker-compose up -d
        
    In headless model, you would have to start and stop the containers manually.

Key Concepts
===
At the present moment, this model utilizes statistical arbitrage incorporating these methodologies:
- Bootstrapping the model with historical data to derive usable strategy parameters
- Resampling inhomogeneous time series to homogeneous time series
- Selection of highly-correlated tradable pair
- The ability to short one instrument and long the other.
- Using volatility ratio to detect up or down trend.
- Fair valuation of security using beta, or the mean over some past interval.
- One pandas DataFrame to store historical prices

Other functionas:
- Generate trade signals and place buy/sell market orders based on every incoming tick data.
- Re-evaluating beta every some interval in seconds.

And greatly inspired by these papers:
- MIT - Developing high-frequency equities trading model 
  @ http://dspace.mit.edu/handle/1721.1/59122
- SMU - Profiting from mean-reverting yield-curve trading strategies
  @ http://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=3488&context=lkcsb_research

And book:
- Introduction to High-Frequency Finance
  @ http://www.amazon.com/Introduction-High-Frequency-Finance-Ramazan-Gen%C3%A7ay/dp/0122796713

Step-by-step guide to more trading models
===

<a href="https://www.packtpub.com/big-data-and-business-intelligence/mastering-python-finance-second-edition?utm_source=github&utm_medium=repository&utm_campaign=9781789346466"><img src="https://www.packtpub.com/media/catalog/product/cache/e4d64343b1bc593f1c5348fe05efa4a6/b/1/b11165.png" alt="Mastering Python for Finance - Second Edition" height="256px" align="right"></a>

I published a book titled 'Mastering Python for Finance - Second Edition', discussing additional algorithmic trading ideas, statistical analysis, machine learning and deep learning, which you might find it useful.
It is available on major sales channels including Amazon, Safari Online and Barnes & Noble,
in paperback, Kindle and ebook.
Get it from:
- https://www.amazon.com/dp/1789346460

Source codes and table of contents on GitHub:
- https://github.com/jamesmawm/mastering-python-for-finance-second-edition




Future Enhancements
===
I would love to extend this model in the unforeseeable future:
- Extending to more than 2 securities and trade on optimum prices
- Generate trade signals based on correlation and co-integration
- Using PCA for next-period evaluation. In my book I've described the use of PCA to reconstruct the DOW index. Source codes <a href="https://github.com/jamesmawm/mastering-python-for-finance-second-edition/blob/master/Chapter%2006%20-%20Statistical%20Analysis%20of%20Time%20Series%20Data.ipynb">here</a>,
- Include vector auto-regressions
- Account for regime shifts (trending or mean-reverting states)
- Account for structural breaks
- Using EMA kernels instead of a rectangular one
- Add in alphas(P/E, B/P ratios) and Kalman filter prediction

Disclaimer
===
- Any securities listed is not a solicitation to trade
- This model has not been proven to be profitable in a live account,
and I will not be responsible for any outcome of your trades.
Should you be profitable, thank you notes are welcomed.

Is this HFT?
===
Sure, I had some questions "how is this high-frequency" or "not for UHFT" or "this is not front-running". Let's take a closer look at these definitions:
- High-frequency finance: the studying of incoming tick data arriving at high frequencies,
say hundreds of ticks per second. High frequency finance aims to derive stylized facts from high frequency signals.
- High-frequency trading: the turnover of positions at high frequencies;
positions are typically held at most in seconds, which amounts to hundreds of trades per second.

This models aims to incorporate the above two functions and present a simplistic view to traders who wish to automate their trades, get started in Python trading or use a free trading platform.

Other software of interest
===
What about trading futures? *Psst* I've got you covered.

Simply called 'The Gateway', it is a C# application that exposes a socket and
public API method calls for interfacing Python with futures markets including CME,
CBOT, NYSE, Eurex and ICE.

More information on GitHub: https://github.com/hftstrat/The-Gateway-code-samples or view on the <a href="https://github.com/hftstrat/The-Gateway-code-samples">website</a>


Final Notes
========================
- I haven't come across any complete high-frequency trading model lying around, so here's one to get started off the ground and running.
- This model has never been used with a real account. All testing was done in demo account only.
- The included strategy parameters are theoretical ideal conditions, which have not been adjusted for back-tested results.
- This project is still a work in progress. A good model could take months or even years!

Email stuff here: jamesmawm@gmail.com
