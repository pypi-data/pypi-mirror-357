import requests
import os
import subprocess
import shutil


def download_with_requests(gists, headers):
    for gist in gists:
        gist_name = name_gist(gist)
        if not os.path.exists(gist_name):
            os.mkdir(gist_name)
            print(f"Downloading the gist '{gist_name}'...")
        else:
            print(f"Updating the gist '{gist_name}'...")
            shutil.rmtree(gist_name)
        files = gist["files"]
        for filename in files:
            gist_url = files[filename]["raw_url"]
            response = requests.get(gist_url, headers=headers)
            with open(f"{gist_name}/{filename}", "wb") as file:
                file.write(response.content)


def download_with_git(gists):
    for gist in gists:
        gist_name = name_gist(gist)
        gist_pull_url = f"git@gist.github.com:{gist['id']}.git"
        if not os.path.exists(gist_name):
            subprocess.call(["git", "clone", "--recursive", gist_pull_url, gist_name])
        else:
            print(f"Pulling '{gist_name}'...")
            subprocess.call(["git", "-C", gist_name, "pull", "--recurse-submodules"])


def name_gist(gist):
    return gist["description"] if gist["description"] != "" else gist["id"]


def get_all_gists(username, headers):
    gists = []
    page = 1

    while True:
        page_query = f"?per_page=100&page={page}"
        API_ENDPOINT = f"https://api.github.com/users/{username}/gists{page_query}"

        response = requests.get(API_ENDPOINT, headers=headers)

        if response.status_code != 200:
            print(response.status_code, response.text)
            break

        page_gists = response.json()

        if not page_gists:
            break

        gists.extend(page_gists)
        page += 1

    return gists


def download_gists(username, token, git_check):
    headers = {"Authorization": f"token {token}"} if token else None
    gists = get_all_gists(username, headers)

    if git_check:
        download_with_git(gists)
    else:
        download_with_requests(gists)
