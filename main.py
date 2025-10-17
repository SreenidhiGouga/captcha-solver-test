from fastapi import FastAPI, Request
import json, requests, subprocess, os

app = FastAPI()
SECRET = "TDS_PROJECT_1"
GITHUB_USERNAME = "SreenidhiGouga"

@app.post("/api-endpoint")
async def build_app(req: Request):
    data = await req.json()
    if data.get("secret") != SECRET:
        return {"error": "Invalid secret"}, 400

    task = data["task"]
    repo_name = task.replace(" ", "-")  # unique repo name
    pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"

    # Create repo using GitHub CLI
    subprocess.run(f"gh repo create {repo_name} --public --confirm", shell=True)

    # Write minimal HTML
    os.makedirs("app", exist_ok=True)
    with open("app/index.html", "w") as f:
        f.write(f"<h1>{data['brief']}</h1>")

    # Git push
    subprocess.run(f"git init", shell=True, cwd="app")
    subprocess.run(f"git add .", shell=True, cwd="app")
    subprocess.run(f"git commit -m 'init'", shell=True, cwd="app")
    subprocess.run(f"git branch -M main", shell=True, cwd="app")
    subprocess.run(f"git remote add origin https://github.com/{GITHUB_USERNAME}/{repo_name}.git", shell=True, cwd="app")
    subprocess.run(f"git push -u origin main", shell=True, cwd="app")

    # Create basic README
    with open("README.md", "w") as f:
        f.write("# Captcha Solver Demo\n- MIT License\n- Minimal App Demo\n")

    # POST to evaluation_url
    payload = {
        "email": data["email"],
        "task": data["task"],
        "round": data["round"],
        "nonce": data["nonce"],
        "repo_url": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
        "commit_sha": "latest_commit_sha_here",
        "pages_url": pages_url
    }
    try:
        r = requests.post(data["evaluation_url"], json=payload)
        return {"status": "success" if r.status_code==200 else "failed"}
    except Exception as e:
        return {"error": str(e)}
