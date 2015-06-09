"""
Author: James Ma
Email stuff here: jamesmawm@gmail.com
"""
from models.hft_model import HFTModel

if __name__ == "__main__":
    model = HFTModel(host='localhost',
                     port=7496,
                     client_id=101,
                     is_use_gateway=False,
                     evaluation_time_secs=20,
                     resample_interval_secs='30s')
    model.start(["JPM", "C"], 100)