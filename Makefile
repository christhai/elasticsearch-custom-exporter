.PHONY : build run-local

# Provide environment variables to tasks
.EXPORT_ALL_VARIABLES:

clean:
	rm -rf ./.eggs ./build/ ./dist/ *.egg-info AUTHORS ChangeLog

requirements:
	pip install -r requirements.txt

build:
	docker build -t prometheus-elastic-custom-exporter .

run-local:
	docker run -it --rm \
	-p 9210:9210 \
	prometheus-elastic-custom-exporter \
	$(extra_args)
