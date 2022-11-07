# coding=utf-8
import tomli
import os



config_file = os.path.expanduser('~/.config/hosteurope-letsencrypt/config.toml')
if os.path.isfile("config.toml") or not os.path.isfile(config_file):
  config_file = os.path.abspath('config.toml')

letsencrypt_folder = os.path.expanduser('~/.config/hosteurope-letsencrypt/')

with open(config_file, 'rb') as f:
    config = tomli.load(f)