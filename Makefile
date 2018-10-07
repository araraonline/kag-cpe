MA_SIMPLIFIED_SHAPEFILE = 'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_25_tract_500k.zip'

all: data/flags/raw \
		data/flags/pre \
		data/flags/process \
		data/flags/output

data/flags/raw: \
			src/util/download.py
	kaggle datasets download -d center-for-policing-equity/data-science-for-good -p data/raw
	unzip data/raw/data-science-for-good.zip -d data/raw/cpe-data

	python -m src.util.download $(MA_SIMPLIFIED_SHAPEFILE) 'data/raw/ma_simplified.zip'
	unzip data/raw/ma_simplified.zip -d data/raw/ma_simplified

	touch data/flags/raw

data/flags/pre: data/flags/raw
	touch data/flags/pre

data/flags/process: data/flags/pre
	touch data/flags/process

data/flags/output: data/flags/process
	touch data/flags/output
