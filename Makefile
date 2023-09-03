all:
	APP_BROKER_URI: "pyamqp://guest@rabitmq:5672"
	APP_BACKEND: "redis://redis:6379/0"
	CELERY_RESULT_BACKEND: "redis://redis:6379/0"
	FLASK_ENV: "development"

copy-model:
	mkdir -p artifacts
	cp model/{input.json,kzg.srs,network.onnx,network.ezkl,pk.key,settings.json} ./artifacts


run-standalone:
	gunicorn app_alone:app -w3 -b 0.0.0.0:8000 --timeout 120