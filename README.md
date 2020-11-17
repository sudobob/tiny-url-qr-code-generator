# tiny-url-qr-code-generator
Personal URL shortener microservice to run on in your own domain. 

![enter image description here](https://github.com/sudobob/tiny-url-qr-code-generator/blob/master/images/tinyurl_demo.gif)

Intended to run on your public web server it takes URLs and produces a unique, short URL which redirects to the original URL.

In addition, a QR code is produced which also redirects to the original URL

## Installation
### Using python virtual env
```
git clone <this repo> <dest dir>
cd <dest dir>
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env #  set local variables to suit
python3 run.py
```
### Using docker

```
git clone <this repo> <dest dir> cd <dest dir>
docker build --tag tinyurl .
docker run \
 --name tinyurl_container \
 -P  -it -p 60000:60000  \
 -v `pwd`/db/:/home/tinyurl/db/\
 --rm tinyurl python3 run.py
```
### Apached vhost
We run this in an apache http vhost environment where our web server runs several different services under different subdomains

Here is our configuration file
```
#
# apache httpd vhost proxy config
#
# directs [http,https]://tu.nova-labs.org/ to a dockered python flask service which
# implements tinyurl
# copy or symlink this file to /etc/httpd/conf.d
#
<VirtualHost tu.nova-labs.org:80>
  ServerName tu.nova-labs.org
  ServerAlias tu.nova-labs.org
  Redirect / https://tu.nova-labs.org/
</VirtualHost>
<VirtualHost tu.nova-labs.org:443>
  ServerName tu.nova-labs.org
  ServerAlias tu.nova-labs.org
  ServerAdmin admins@nova-labs.org

  ErrorLog /var/log/httpd/tinyurl
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:60000/
  ProxyPassReverse / http://127.0.0.1:60000/
  RequestHeader set X-Forwarded-Proto "https"


  ErrorLog /var/log/httpd/tinyurl
  UseCanonicalName On
  SSLEngine on
  SSLProtocol all -SSLv3
  SSLProxyProtocol all -SSLv3
  SSLProxyEngine On
  SSLHonorCipherOrder on
  SSLCipherSuite PROFILE=SYSTEM
  SSLProxyCipherSuite PROFILE=SYSTEM

  SSLCertificateFile /etc/letsencrypt/live/tu.nova-labs.org/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/tu.nova-labs.org/privkey.pem
  Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
```
