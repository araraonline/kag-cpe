MA_SIMPLIFIED_SHAPEFILE = 'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_25_tract_500k.zip'
TX_SHAPEFILE = 'https://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_48_tract.zip'

all: data/flags/raw \
		data/flags/pre \
		data/flags/process \
		data/flags/output

data/flags/raw: \
			src/util/download.py
	kaggle datasets download -d center-for-policing-equity/data-science-for-good -p data/raw
	unzip -n data/raw/data-science-for-good.zip -d data/raw/cpe-data

	python -m src.util.download $(MA_SIMPLIFIED_SHAPEFILE) 'data/raw/ma_simplified.zip'
	unzip -n data/raw/ma_simplified.zip -d data/raw/ma_simplified

	python -m src.util.download $(TX_SHAPEFILE) 'data/raw/census_tx.zip'
	unzip -n data/raw/census_tx.zip -d data/raw/census_tx

	touch data/flags/raw

data/flags/pre: data/flags/raw
	touch data/flags/pre

data/flags/process: data/flags/pre
	touch data/flags/process

data/flags/output: data/flags/process
	touch data/flags/output
