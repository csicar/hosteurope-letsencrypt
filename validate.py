# coding=utf-8
import ftplib
import json
import logging
import os
import uuid

from shared import config

# zu validierende Domain, Dateinamen and Token Inhalt werden von certbot per Umgebungsvariable übergeben
domain = os.environ['CERTBOT_DOMAIN']
filename = os.environ['CERTBOT_TOKEN']
content = os.environ['CERTBOT_VALIDATION']

logging.info(f"Validating Domain {domain}")
logging.debug('Inhalt: ' + content)
logging.debug('Dateiname: ' + filename)

domain_settings = None
ftp_cfg = None

for website in config['websites']:
    if domain in website['domains']:
        domain_settings = website
        print(domain_settings)
        print(config['ftp'])
        ftp_cfg = config['ftp'][website['ftp']]

if domain_settings is None:
    logging.debug('Kein Mapping für Domain gefunden. Breche ab!')
    exit(1)

if ftp_cfg is None:
    logging.debug('Kein Mapping für FTP gefunden. Breche ab!')
    exit(1)

# mit FTP verbinden
ftp = ftplib.FTP_TLS(ftp_cfg['server'], ftp_cfg['login'], ftp_cfg['passwort'])
root_dir = ftp.pwd()

# zum Pfad navigieren, in dem Challenge angelegt werden muss
ftp.cwd(root_dir + domain_settings['ftp-path'])
try:
    ftp.cwd('.well-known/acme-challenge')
except:
    logging.debug('Creating missing .well-known/acme-challenge directory.')
    ftp.mkd('.well-known')
    ftp.cwd('.well-known')
    ftp.mkd('acme-challenge')
    ftp.cwd('acme-challenge')

# temporäre Datei mit Token Inhalt anlegen
temp_filename = str(uuid.uuid4())
logging.debug('Lege temporäre Datei {} mit Token Inhalt an.'.format(temp_filename))
with open(temp_filename, 'wb') as temp:
    temp.write(str.encode(content))

# temporäre Datei unter von certbot vorgegebenen Namen auf FTP hochladen
with open(temp_filename, 'rb') as temp:
    ftp.storbinary('STOR %s' % filename, temp)
ftp.close()

# temporäre Datei löschen
os.remove(temp_filename)
