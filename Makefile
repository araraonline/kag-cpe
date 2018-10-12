MA_SIMPLIFIED_SHAPEFILE = 'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_25_tract_500k.zip'
TX_SHAPEFILE = 'https://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_48_tract.zip'
AUSTIN_CRIMES = 'https://data.austintexas.gov/api/views/g3bw-w7hh/rows.csv?accessType=DOWNLOAD'
AUSTIN_OIS = 'https://data.austintexas.gov/api/views/u2k2-n8ez/rows.csv?accessType=DOWNLOAD'

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

	python -m src.util.download $(AUSTIN_CRIMES) 'data/raw/crime_reports_austin.csv'
	python -m src.util.download $(AUSTIN_OIS) 'data/raw/ois_austin.csv'

	touch data/flags/raw

data/flags/pre: data/flags/raw
	touch data/flags/pre

data/flags/process: data/flags/pre
	touch data/flags/process

data/flags/output: data/flags/process
	touch data/flags/output
