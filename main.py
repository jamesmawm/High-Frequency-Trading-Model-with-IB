from .models.hft_model import HFTModel

if __name__ == '__main__':
	model = HFTModel(
		host='localhost',
		port=7497,
		client_id=101,
		is_use_gateway=False,
		evaluation_time_secs=15,
		resample_interval_secs='30s'
	)

	# model.start(["RDS A", "BP"], 250)
	# model.start(["JPM", "BAC"], 100)
	model.start(["SPY", "QQQ"], 100)
