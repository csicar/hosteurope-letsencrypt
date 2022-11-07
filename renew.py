#!/usr/bin/env python3
# coding=utf-8
import json
import os
from shared import config
import set_certificate
import asyncio
import argparse

parser = argparse.ArgumentParser(description="Create, Verify and Upload Let's Encrypt Certificates to HostEurope")
parser.add_argument('-y', '--yes', help="Skip prompts", action='store_true')
parser.add_argument("--only", help="Run script for single website", default=None)

args = parser.parse_args()

# certbot tries to write to /var/log/letsencrypt by default; because of this, running as root is required.
# certbot Error Message:
# Either run as root, or set --config-dir, --work-dir, and --logs-dir to writeable paths.
is_root = os.geteuid() == 0
home_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt')
certbot_config_dir = home_dir
certbot_work_dir = home_dir
certbot_logs_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt/logs')
if not is_root and not os.path.exists(certbot_logs_dir):
    os.makedirs(certbot_logs_dir)

email = config['email']
staging = config['staging']

challenge = config['preferred-challenge']

async def renew_single(page, website):
  print(f"\n\n(Re)newing Domain {website['domains']}")
  domain_list = "".join([f" -d {domain}" for domain in website["domains"]])
  print(domain_list)
  # certbot Kommando zusammenbauen
  cmd = 'certbot certonly --manual --agree-tos --manual-public-ip-logging-ok'
  cmd += ' -m ' + email
  cmd += ' --preferred-challenge=' + challenge
  if 'http' == challenge:
      cmd += ' --manual-auth-hook "python3 validate.py"'
  if staging:
      cmd += ' --staging'
  if args.yes:
      cmd += ' -n '
  if not is_root:
      cmd += ' --logs-dir ' + certbot_logs_dir
      cmd += ' --work-dir ' + certbot_work_dir
      cmd += ' --config-dir ' + certbot_config_dir

  cmd += domain_list

  # Sicherheitsabfrage
  print(cmd)
  if not args.yes and input('Für diese Domains ein neues Zertifikat erstellen? (y/n): ') != 'y':
      print('Abbruch, es wurde kein Zertifikat erstellt.')
      exit(0)

  # neues Zertifikat erstellen
  os.system(cmd)

  # Sicherheitsabfrage
  print('Verification Done')
  if not args.yes and input('Upload the certificates to kis.hosteurope.de (y/n):') != 'y':
      print('Abort: No certificates uploaded')
      exit(0)
  await set_certificate.set_certificate_for(page, website)

async def renew_all(page, only_filter):
  for website in config['websites']:
    if only_filter is None or only_filter in website['domains']:
      await renew_single(page, website)

async def renew_main():
  async def inner(browser, page):
    login_task = set_certificate.login(page)
    await login_task
    renew_task = renew_all(page, args.only)
    await renew_task
    # await asyncio.gather(login_task, renew_task)

    await browser.close()
  await set_certificate.with_playwright(inner)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(renew_main())
    except KeyboardInterrupt:
        pass