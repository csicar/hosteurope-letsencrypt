#!/usr/bin/env python3
# coding=utf-8
import json
import os
import asyncio
from playwright.async_api import async_playwright
from shared import config, letsencrypt_folder
import sys
import re

async def submit_form(page, url, cert_file, key_file, domain_name):
    # page = await browser.new_page()
    # Open SSL page
    print(f"Opening SSL-Form for {domain_name}: {url}")
    await page.goto(url, wait_until = 'networkidle')
    await page.set_viewport_size({'width': 1366, 'height': 1000})
    await asyncio.sleep(1)

    # Fill in form
    print(f"Uploading cert files: {cert_file} and {key_file}")

    await page.set_input_files("input[name=certfile]", cert_file)
    await page.set_input_files("input[name=keyfile]", key_file)

    # Submit form
    print(f"Submit form")
    await page.focus("input[name=keypass]")
    await page.keyboard.press("Enter")
    await asyncio.sleep(1)
    await page.wait_for_load_state('networkidle')

    # Log result
    print(f"Done! Logging output")
    await asyncio.sleep(5)
    await page.pdf(path=f"{domain_name}.log.pdf", print_background=True, format='A4')
    await page.screenshot(path = f"{domain_name}.log.jpeg")
    
async def login(page, retry=4):
    for i in range(0, retry):
        print(f"Login Attempt {i+1}/{retry}")
        try:
            await login_inner(page)
            return True
        except Exception as e:
            print(f"Login failed ({e}) -> Retry")
    input("Automatic Login Failed. Please try it manually and press enter")
    
    return False

async def login_inner(page):
    await asyncio.sleep(3)
    await page.goto('https://kis.hosteurope.de', wait_until = 'networkidle')
    await page.focus("input[autocomplete=email]")
    await page.keyboard.type(config["kis-username"])
    await page.focus("input[type=password]")
    await page.keyboard.type(config["kis-password"])
    await page.keyboard.press("Enter")
    await asyncio.sleep(1)
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(1)
    #2FA
    if (config["kis-2fa"]):
        await page.focus("input[id=1]")
        await page.keyboard.type(input("Enter the 2FA you got via SMS here: "))
        await page.keyboard.press("Enter")
        await asyncio.sleep(10)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(10)

    await page.wait_for_url("https://kis.hosteurope.de/**")

    print("Login completed successfully")


async def with_playwright(f):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo= 1, devtools= True)
        page = await browser.new_page()
        await f(browser, page)


def get_cert_path_for(domains):
    existing_certificate_folders = os.listdir(os.path.join(letsencrypt_folder, "live"))
    matching_path = None
    for folder in existing_certificate_folders:
        if folder in domains:
            matching_path =  folder
        else: 
            match = re.search(r"^(.+)-(\d+)$", folder)
            if match is not None:
                domain = match.group(1)
                if domain in domains:
                    matching_path = folder
    return os.path.join(letsencrypt_folder, "live", matching_path)

async def set_certificate_for(page, website):
    url = website['cert-url']
    cert_path = get_cert_path_for(website['domains'])
    cert_file = os.path.join(cert_path, 'fullchain.pem')
    key_file = os.path.join(cert_path, 'privkey.pem')
    
    await submit_form(page, url, cert_file, key_file, website['domains'][0])

    await asyncio.sleep(10)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(set_certificate())
    except KeyboardInterrupt:
        pass
