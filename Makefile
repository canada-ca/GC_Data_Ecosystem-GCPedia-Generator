.PHONY: view build

view: build
	open data_depot_out.html

build:
	./gen_data_depot.py
