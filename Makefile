all: data/flags/raw \
		data/flags/pre \
		data/flags/process \
		data/flags/output

data/flags/raw:
	kaggle datasets download -d center-for-policing-equity/data-science-for-good -p data/raw
	unzip data/raw/data-science-for-good.zip -d data/raw/cpe-data
	touch data/flags/raw

data/flags/pre: data/flags/raw
	touch data/flags/pre

data/flags/process: data/flags/pre
	touch data/flags/process

data/flags/output: data/flags/process
	touch data/flags/output
