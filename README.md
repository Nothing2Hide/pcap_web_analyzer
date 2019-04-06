# pcap_web_analyzer

Web interface to analyze pcap files looking for malicious indicators from a MISP instance.

This web application allows to upload pcap and pcap-ng files and :
* Extract indicators using `pcap_ioc`
* Search for these indicators in a MISP instance using `pymisp`
* Delete securely the pcap file
* Return a result (Nothing found, or malicious)

## Development

Installation:

* Install redis, see https://redis.io/topics/quickstart
* Install `shred`
* Install requirements : `pip install -r requirements.txt`
* Locally install the npm packages with `npm install` in `pcap_web_analyzer/frontend`

Run the app :

* Launch django : `python manage.py runserver`
* Lanch the vuejs vue, in `frontend` : `npm run serve`
* Launch Celery : `celery -A pcap_web_analyzer  worker -l info` (You need to have Redis running)

Visit http://localhost:8080/ or http://localhost:8000/admin/

## Run the application in production

See [the production instructions](PROD.md).

## Limitatiions

This application is just looking for know malicious indicators in the PCAP files and won't find any unknown malicious acitivity. The detection is just as good as the indicators in the MISP instance.

## LICENSE

This software is released under the MIT license.
