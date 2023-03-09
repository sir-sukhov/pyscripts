#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2022 sir-sukhov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
import requests
import json
import urllib
import shutil
import os
import logging
from datetime import datetime
from argparse import ArgumentParser

# REPO = "rabbitmq/rabbitmq-delayed-message-exchange"
# repo = REPO


def getReleases(repo: str) -> list:
    result = None
    url = f"https://api.github.com/repos/{repo}/releases"
    try:
        r = requests.get(url, headers={"accept": "application/json"})
        if r.status_code == 200:
            result = json.loads(r.content)
    except Exception as e:
        print(e)
    return result


parser = ArgumentParser()
parser.add_argument(
    "-r", "--repo", dest="repo", required=True,
    help="name of github repository"
)
args = parser.parse_args()
repo = args.repo

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S%z')

releases = getReleases(repo)
if releases:
    local_repo_path = os.path.join(os.getcwd(), repo)
    try:
        os.makedirs(local_repo_path)
        logging.info(f"Created directory {repo}")
    except FileExistsError:
        logging.info(f"Directory {repo} already exists")
        pass
    for r in releases:
        for a in r['assets']:
            if a['content_type'] == "application/octet-stream":
                logging.info(f"Downloading {a['name']}")
                browser_download_url = a['browser_download_url']
                file_path = os.path.join(local_repo_path, a['name'])
                with urllib.request.urlopen(browser_download_url) as response, open(file_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                file_path_json = file_path + '.json'
                with open(file_path_json, 'w') as out_file_json:
                    json.dump(a, out_file_json)
                atime = datetime.now()
                mtime = datetime.strptime(a['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                os.utime(file_path, (atime.timestamp(), mtime.timestamp()))
                os.utime(file_path_json, (atime.timestamp(), mtime.timestamp()))
