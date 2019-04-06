# Deploying in production

**Beta version, this guide may need some improvements. The installation process was tested on debian stretch 9.8**

This guide is largely based on [Christopher Shoo "How to deploy django application to a production server."](https://medium.com/@_christopher/deploying-my-django-app-to-a-real-server-part-i-de78962e95ac).


## Prepare the system

* Install needed packages : `sudo apt-get install nginx mysql-server python3-pip python3-dev default-libmysqlclient-dev virtualenv git redis-server supervisor tshark`
* Install nodejs LTS version ([ref](https://github.com/nodesource/distributions/blob/master/README.md#deb)) : `curl -sL https://deb.nodesource.com/setup_10.x | bash -` and `apt-get install -y nodejs`
* Finish the MySQL installation and set-up a root password with `mysql_secure_installation`
* Create the MySQL database :

```
$ mysql -u root -p
mysql> CREATE DATABASE pcap_db CHARACTER SET 'utf8';
mysql> CREATE USER pcap_user;
mysql> GRANT ALL ON pcap_db.* TO 'pcap_user'@'localhost' IDENTIFIED BY 'secret';
mysql> quit
```
* Create local user `pcap` : `adduser pcap`
* Login as pcap : `sudo su pcap` and `cd`
* Create log folder : `mkdir logs`
* Create virtual env : `virtualenv venv -p /usr/bin/python3`
* Enable it : `source venv/bin/activate `

## Deploy Django

* Get the source code : `git clone https://github.com/Nothing2Hide/pcap_web_analyzer.git`
* Install the requirements : `cd pcap_web_analyzer` and `pip install -r requirements`
* Update `pcap_web_analyzer/settings.py`
    * Update `SECRET_KEY`
    * Update `Debug` to False
    * Update `ALLOWED_HOSTS`
    * Update `DATABASES`
    * Update `TIME_ZONE`
    * Update `MISP_SERVER` and `MISP_KEY`
* Regarding database, here is an example of code :
```
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pcap_db',
        'USER': 'pcap_user',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '3306',
```
* Go into `frontend` and run `npm install`
* Update the `baseUrl` in `vue.config.js`
* Build the javascript bundle : `npm run build`
* Go back into `pcap_web_analyzer`
* Create the database tables with `python manage.py migrate`
* Collect all the static files with `python manage.py collectstatic`
* Create a super user account with `python manage.py createsuperuser`
* In `public`, create a folder `mkdir static` and move `admin` in it with `mv admin static`

You can test if everything is working fine by running `python manage.py runserver`

### Set-up gunicorn

* Install gunicorn (still as pcap) : `pip install gunicorn`
* You can test if everything is working with `gunicorn --bind 0.0.0.0:8800 pcap_web_analyzer.wsgi:application` (the javascript and static files wouldn't work)
* Now as root, create a file in `/etc/systemd/system/gunicorn.service`

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

## Deploying Celery for Aynchronous Analysis

(This part was inspired by [this article](https://zerowithdot.com/django-celery-p3/))

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

## Installing and Configuring Nginx

* Create the following site file `/etc/nginx/sites-available/pcap` :

```
upstream gunicorn_app_server {
    server unix:/home/pcap/pcap_web_analyzer/pcap_web_analyzer/awesome.sock fail_timeout=0;
}

server {
        listen 80;
        server_name pcap.pcap;
        client_max_body_size 4G;
        keepalive_timeout 5;
        root /home/pcap/pcap_web_analyzer/pcap_web_analyzer/public;
        access_log /var/log/nginx/pcap-access.log;
        error_log  /var/log/nginx/pcap-error.log;

        location / {
                # checks for static file, if not found proxy to app
                try_files $uri @proxy_to_app;
        }

        location @proxy_to_app {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Host $http_host;
                # we don't want nginx trying to do something clever with
                # redirects, we set the Host: header above already.
                proxy_redirect off;
                proxy_pass http://gunicorn_app_server;
        }
}
```

* Add it to the enabled sites : `ln -s /etc/nginx/sites-available/pcap /etc/nginx/sites-enabled/`
* Check the syntax : `nginx -t`
* If the syntax is ok, reload the configuration : `service nginx reload`

Now connect to your server on port 80 and you should see the application running correctly.

Please note that for simplicity, we have not included here how to deploy let's encrypt certificate and use https instead of http. Needless to say that it is strongly recommanded to deploy valid certificate and enforce https connections. If you have any trouble with having nginx working with gunicorn, you should check [this](https://docs.gunicorn.org/en/latest/deploy.html).

## Additional information

###  Using Apache instead of nginx

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

### Compile static files locally

You can avoid installing the heavy nodejs on your production server by compiling the assets locally on your local system before uploading them.

In `pcap_web_analyzer/frontend`, build the javascript app :

* Update the url in `vue.config.js` `baseUrl`
* Build the code with `npm run build`

In `pcap_web_analyzer`, collect all the static files with `python manage.py collectstatic`. The static files are now in `public`. Upload this folder on the server and move it to `/home/pcap/pcap_web_analyzer/pcap_web_analyzer`

### This Could be better

* Many people prefer to handle gunicorn with supervisor instead of another systemd service, it can be easier, check [this blog post](https://zerowithdot.com/django-celery-p3/) to see how to do that
* We have not included how to configure a firewall in this guide, you should definitely have a firewall filtering incoming connections. In that case, you just need to have the ports used by nginx (likely 80 and 443) to have this app working (redis is listening locally and gunicorn is using a Unix socket)
