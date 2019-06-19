import pandas as pd
from dateutil import tz

UTC_TIMEZONE = tz.tzutc()
LOCAL_TIMEZONE = tz.tzlocal()


def convert_utc_datetime(datetime):
	utc = datetime.replace(tzinfo=UTC_TIMEZONE)
	local_time = utc.astimezone(LOCAL_TIMEZONE)
	return pd.to_datetime(local_time)


def convert_local_datetime(datetime):
	local_time = datetime.replace(tzinfo=LOCAL_TIMEZONE)
	return pd.to_datetime(local_time)
