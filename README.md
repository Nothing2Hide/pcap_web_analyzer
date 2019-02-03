# pcap_web_analyzer
Web interface to analyze pcap files looking for malicious indicators

## Install

* Install redis, see https://redis.io/topics/quickstart
* Install `shred`

## Run the app

* Launch Celery : `celery -A pcap_web_analyzer  worker -l info` (You need to have Redis running)

## TODO

* Add a step for indicator analysis to have a better tracking in the view
* Work on the view
* Track MISP errors
* Add an object to log analysis -> time + success

# LICENSE

MIT
