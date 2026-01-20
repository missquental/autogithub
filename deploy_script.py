#!/usr/bin/env python3
import requests
import os
import base64
import argparse

def get_templates():
    return sorted([
        f for f in os.listdir(".")
        if f.startswith("template-app") and f.endswith(".py")
    ])

class Deployer:
    def __init__(self, token):
        self.h = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_repo(self, name, desc, private):
        r = requests.post(
            "https://api.github.com/user/repos",
            headers=self.h,
            json={
                "name": name,
                "description": desc,
                "private": private,
                "auto_init": True
            }
        )
        if r.status_code != 201:
            raise Exception(r.json())
        return r.json()

    def upload(self, owner, repo, path, content):
        requests.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            headers=self.h,
            json={
                "message": f"Add {path}",
                "content": base64.b64encode(content.encode()).decode()
            }
        )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--token", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--template")
    p.add_argument("--private", action="store_true")
    p.add_argument("--description", default="Auto deployed Streamlit app")
    args = p.parse_args()

    templates = get_templates()
    if not templates:
        raise Exception("No template-app*.py found")

    template = args.template or (
        "template-app4.py" if "template-app4.py" in templates else templates[0]
    )

    with open(template, "r", encoding="utf-8") as f:
        app_code = f.read()

    with open("requirements.txt", "r", encoding="utf-8") as f:
        req = f.read()

    deployer = Deployer(args.token)
    repo = deployer.create_repo(args.repo, args.description, args.private)

    owner = repo["owner"]["login"]

    deployer.upload(owner, args.repo, "app.py", app_code)
    deployer.upload(owner, args.repo, "requirements.txt", req)

    print("✅ DONE")
    print(repo["html_url"])

if __name__ == "__main__":
    main()
