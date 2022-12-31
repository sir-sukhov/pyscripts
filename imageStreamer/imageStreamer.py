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
import time, json, requests, urllib3, getpass, re, subprocess, logging
from base64 import b64encode
from argparse import ArgumentParser

SECONDS_TO_SLEEP=300
VERSION_PATTERN='^v[0-9a-z]+$'

urllib3.disable_warnings()

class Registry:

    def __init__(self, baseUrl: str, user: str, password: str):
        self.token=b64encode(f"{user}:{password}".encode('utf-8')).decode("ascii")
        self.baseUrl = baseUrl
        self.headers = {
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
            'Authorization': f'Basic {self.token}'
        }


    def get_latest_tag(self, repo: str) -> str:
        result=None
        url=f"{self.baseUrl}/v2/{repo}/tags/list"
        try:
            r=requests.get(url, headers=self.headers, verify=False)
            if r.status_code == 200:
                response=json.loads(r.content)
                tags=list(filter(lambda t: re.match(VERSION_PATTERN, t) != None, response['tags']))
                tags.sort()
                result=tags[-1]
        except Exception as e:
            print(e)
        return result

    def get_remote_digest(self, repo: str, tag: str) -> str:
        result=None
        url=f"{self.baseUrl}/v2/{repo}/manifests/{tag}"
        try:
            r=requests.get(url, headers=self.headers, verify=False)
            if r.status_code == 200:
                result=f"{self.baseUrl.split('//')[1]}/{repo}@{r.headers['Docker-Content-Digest']}"
        except Exception as e:
            print(e)
        return result

def update_local_latest(remote_digest, latest_remote_tag, user, password):
    repository=remote_digest.split('@')[0]
    server=repository.split('/')[0]
    subprocess.run(["docker", "login", "-p", password, "-u", user, server], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logging.info(f"Updating local latest to {repository}:{latest_remote_tag}")
    subprocess.run(["docker", "pull", remote_digest], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "tag", remote_digest, f"{repository}:{latest_remote_tag}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "tag", remote_digest, f"{repository}:latest"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "logout", server], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

arguments={
    "username":
        {"short_key": "-u", "prompt": "registry user", "help": "User to login registry"},
    "password":
        {"short_key": "-p", "prompt": "registry pass", "help": "Password to login registry"},
    "registry_url":
        {"short_key": "-r", "prompt": "registry url", "help": "Registry url in format https://registry.example.com"},
    "image_repos":
        {"short_key": "-i", "prompt": "comma-separated repos", "help": "Comma-separate image repos, for example: system/image-name for command 'docker pull registry.example.com/system/image-name:latest'"},
}

parser = ArgumentParser()
for a in arguments:
    parser.add_argument(
        arguments[a]["short_key"],dest=a,help=arguments[a]["help"]
    )
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true")
args = parser.parse_args()

if args.verbose:
    print("Setting log level to debug")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S%z')
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S%z')

for a in arguments:
    argument_value=getattr(args,a)
    if not argument_value:
        prompt=f"{arguments[a]['prompt']}: "
        if a == "password":
            arguments[a]["value"]=getpass.getpass(prompt)
        else:
            arguments[a]["value"]=input(prompt)
    else:
        arguments[a]["value"]=argument_value

url=arguments["registry_url"]["value"]
domain_name=url.split('//')[1]
user=arguments["username"]["value"]
password=arguments["password"]["value"]
repos=arguments["image_repos"]["value"]
registry = Registry(url, user, password)

while True:
    for repo in repos.split(','):
        latest_remote_tag = registry.get_latest_tag(repo)
        remote_digest = registry.get_remote_digest(repo, latest_remote_tag)

        if latest_remote_tag == None or remote_digest == None:
            raise ValueError("Failed to fetch remote digest")

        local_digest_resul=subprocess.run(
                ["docker", "inspect", "--format", "{{index .RepoDigests 0}}", f"{domain_name}/{repo}:latest"],
                capture_output=True)

        rc=local_digest_resul.returncode
        no_such_image_locally=local_digest_resul.stderr.decode().startswith('Error: No such object')
        local_digest=local_digest_resul.stdout.decode().strip()

        if (rc == 0 and local_digest != remote_digest) or (rc == 1 and no_such_image_locally):
            update_local_latest(remote_digest, latest_remote_tag, user, password)
        elif (rc == 0 and local_digest == remote_digest):
            logging.debug(f"Remote and local latest digest matches for {repo}, nothing to do")
        else:
            raise ValueError("Something went wrong with docker inspect command")
    time.sleep(SECONDS_TO_SLEEP)