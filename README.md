# pcap_web_analyzer

Web interface to analyze pcap files looking for malicious indicators

## Install

* Install redis, see https://redis.io/topics/quickstart
* Install `shred`

## Run the app in development

* Launch django : `python manage.py runserver`
* Lanch the vuejs vue, in `frontend` : `npm run serve`
* Launch Celery : `celery -A pcap_web_analyzer  worker -l info` (You need to have Redis running)

Visit http://localhost:8080/ or http://localhost:8000/admin/

## TODO

* Work on the view
    * Keep history of the files uploaded
    * Try with large files
* Delete the CORS plugin
* Track MISP errors
* Add an object to log analysis -> time + success

# LICENSE

MIT
