# Deploying in production

**Still beta, lots of things may go wrong here**

## Compile vuejs files

* Update the url in `vue.config.js` `baseUrl`
* Build the code with `npm run build`

## Prepare users

* Create local user `pcap` : `adduser pcap`
* Create logs folder : `mkdir logs`

## Deploy Django

I will use gunicorn as a local web server, and requests proxied either from Nginx or Apache as described [here](https://medium.com/@_christopher/deploying-my-django-app-to-a-real-server-part-i-de78962e95ac).

* Update `pcap_web_analyzer/settings.py`
    * Update `SECRET_KEY`
    * Update `Debug` to False
    * Update `ALLOWED_HOSTS`
    * Update `DATABASES`
    * Update `TIME_ZONE`
    * Update `MISP_SERVER` and `MISP_KEY`

### Set-up gunicorn

* Install gunicorn : `(venv) $ pip install gunicorn`
* Create a file in `/etc/systemd/system/gunicorn.service`

```
[Unit]
Description=gunicorn service
After=network.target

[Service]
User=pcap
Group=www-data
WorkingDirectory=/home/pcap/pcap_web_analyzer/pcap_web_analyzer/
ExecStart=/home/pcap/venv/bin/gunicorn --access-logfile /home/pcap/logs/gunicorn_access.log --error-logfile /home/pcap/logs/gunicorn_error.log --workers 3 --bind unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock pcap_web_analyzer.wsgi:application

[Install]
WantedBy=multi-user.target
```

Then run it

```
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
sudo systemctl status gunicorn.service
```

If something is not working, check logs in `/home/pcap/logs/`, if you update the gunicorn service, you need to reload the daemon with :

```
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```
## Configure Apache

Install Apache 2.4, here is a potential configuration file :

```
<VirtualHost *:443>
        ServerAdmin EMAIL
        ServerName DOMAIN
        DocumentRoot /home/pcap/pcap_web_analyzer/pcap_web_analyzer/public/

        Alias /.well-known/acme-challenge /etc/letsencrypt/challenges/DOMAIN
        <Directory /etc/letsencrypt/challenges/DOMAIN>
                Require all granted
        </Directory>

        SSLEngine On
        SSLCertificateFile /etc/letsencrypt/certs/DOMAIN.crt
        SSLCertificateKeyFile /etc/letsencrypt/private/DOMAIN.io.key
        SSLCertificateChainFile /etc/letsencrypt/pem/DOMAIN.io.pem

        ProxyPreserveHost On
        <Location "/analysis">
                ProxyPass "unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock|http://127.0.0.1/analysis"
                ProxyPassReverse "unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock|http://127.0.0.1/"
        </Location>
        <Location "/admin">
                ProxyPass "unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock|http://127.0.0.1/admin"
                ProxyPassReverse "unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock|http://127.0.0.1/"
        </Location>

        <Directory /home/pcap/pcap_web_analyzer/pcap_web_analyzer/public/>
                Require all granted
                DirectoryIndex index.html
                Options -Indexes
        </Directory>

        ErrorLog /var/log/apache2/pcap.local_error.log
        CustomLog /var/log/apache2/pcap.local_access.log combined
        ServerSignature Off
        Header set X-Content-Type-Options nosniff
        Header set X-Frame-Options DENY
</VirtualHost>
```


## Deploy Redis and Celeri

* Install Reddis
* Install Supervisor : `sudo apt install supervisor`
* Create a supervisor task by creating a file in `/etc/supervisor/conf.d/pcap-celery.conf` :

```
[program:pcap-celery]
command=/home/pcap/venv/bin/celery worker -A pcap_web_analyzer --loglevel=INFO
directory=/home/pcap/pcap_web_analyzer/pcap_web_analyzer/
user=pcap
numprocs=1
stdout_logfile=/home/pcap/logs/celery.log
stderr_logfile=/home/pcap/logs/celery.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600
stopasgroup=true
priority=1000
```

Reload Supervisor configuration :

```
sudo supervisorctl reread
sudo supervisorctl update
```

Start the celery process with `supervisorctl start pcap-celery` and check that it is correctly working with `supervisorctl status pcap-celery` (if it is not working, check logs in `/home/pcap/logs/celery.log`)

## Could be better

* Many people prefer to handle gunicorn with supervisor instead of another systemd service, it can be easier, check [this blog post](https://zerowithdot.com/django-celery-p3/) to see how to do that
* gunicorn recommends using nginx instead of apache as web server, if you do, you should read [this](https://medium.com/@_christopher/deploying-my-django-app-to-a-real-server-part-ii-f0c277c338f4) and [this](https://docs.gunicorn.org/en/latest/deploy.html)
