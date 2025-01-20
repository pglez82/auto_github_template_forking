import os
import subprocess
import shutil
import time

# Template repository details
TEMPLATE_REPO = "Arquisoft/wichat_0"
ORGANIZATION = "Arquisoft"  # Organization name

# List of new repository names
NEW_REPOS = ["wichat_es1a","wichat_es1b","wichat_es1c",
             "wichat_es2a","wichat_es2b","wichat_es2c",
             "wichat_es3a","wichat_es3b","wichat_es3c",
             "wichat_es4a","wichat_es4b","wichat_es4c",
             "wichat_es5a","wichat_es5b","wichat_es5c",
             "wichat_es6a","wichat_es6b","wichat_es6c",
             "wichat_en1a","wichat_en1b","wichat_en1c",
             "wichat_en2a","wichat_en2b","wichat_en2c",
             "wichat_en3a","wichat_en3b","wichat_en3c",]

# Files to update
FILES_TO_UPDATE = [
    "docker-compose.yml",
    "README.md",
    "docs/README.md",
    ".github/workflows/release.yml",
    "webapp/packages.json",
    "users/userservice/package.json",
    "users/authservice/package.json",
    "gatewayservice/package.json",
    "llmservice/package.json",
    "docs/index.adoc",
    "sonar-project.properties",
    "webapp/public/index.html",
]

def fork_repository(template_repo, org, fork_name):
    """Fork the repository into the organization with a custom name."""
    try:
        subprocess.run(
            [
                "gh", "repo", "fork", template_repo,
                "--clone=false",
                f"--org={org}",
                f"--fork-name={fork_name}"
            ],
            check=True,
        )
        print(f"Forked repository '{template_repo}' as '{org}/{fork_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to fork repository: {e}")
        return False
    return True

def remove_template_status(org, repo_name):
    """Remove the template status of the forked repository."""
    try:
        subprocess.run(
            [
                "gh", "api", f"/repos/{org}/{repo_name}",
                "--method", "PATCH",
                "--field", "is_template=false"
            ],
            check=True,
        )
        print(f"Removed template status from repository '{org}/{repo_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove template status for '{org}/{repo_name}': {e}")

def clone_repository(org, repo_name, local_path):
    """Clone a repository locally."""
    repo_url = f"https://github.com/{org}/{repo_name}.git"
    try:
        subprocess.run(["git", "clone", repo_url, local_path], check=True)
        print(f"Cloned repository '{org}/{repo_name}' locally.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository '{org}/{repo_name}': {e}")
        return False
    return True

def update_files(local_path, old_string, new_string):
    """Update specified files with the new repository name."""
    for root, _, files in os.walk(local_path):
        for file in files:
            # Compute the relative path of the file from the local_path
            relative_path = os.path.relpath(os.path.join(root, file), start=local_path)
            # Check if this relative path matches any in FILES_TO_UPDATE
            if relative_path in FILES_TO_UPDATE:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                updated_content = content.replace(old_string, new_string)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"Updated '{file_path}'.")

def update_repository_description(org, repo_name):
    """Update the repository description to include a custom URL."""
    description = f"https://{org}.github.io/{repo_name}/"
    try:
        subprocess.run(
            [
                "gh", "api", f"/repos/{org}/{repo_name}",
                "--method", "PATCH",
                "--field", f"description={description}"
            ],
            check=True,
        )
        print(f"Updated description for '{org}/{repo_name}' to '{description}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update description for '{org}/{repo_name}': {e}")


def push_changes(local_path, org, repo_name):
    """Push local changes to the GitHub repository."""
    os.chdir(local_path)
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Customize repository"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"Pushed changes to '{org}/{repo_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to push changes for '{org}/{repo_name}': {e}")
    finally:
        os.chdir("..")

def main():
    for repo_name in NEW_REPOS:
        print(f"Processing repository: {repo_name}")

        # Step 1: Fork the repository into the organization with a custom name
        if not fork_repository(TEMPLATE_REPO, ORGANIZATION, repo_name):
            print(f"Skipping repository '{repo_name}' due to forking error.")
            continue
        
        # Pause a little bit to let github create the fork
        time.sleep(3)

        # Step 2: Remove the template status from the forked repository
        remove_template_status(ORGANIZATION, repo_name)

        # Step 3: update the repository description
        update_repository_description(ORGANIZATION, repo_name)

        # Step 4: Clone the forked repository locally
        local_path = os.path.join(os.getcwd(), repo_name)
        if not clone_repository(ORGANIZATION, repo_name, local_path):
            print(f"Skipping repository '{repo_name}' due to cloning error.")
            continue

        # Step 5: Update files with the new repository name
        update_files(local_path, "wichat_0", repo_name)

        # Step 6: Push changes back to the forked repository
        push_changes(local_path, ORGANIZATION, repo_name)

        # Step 7: Clean up local files
        shutil.rmtree(local_path)
        print(f"Repository '{repo_name}' setup completed.\n")

if __name__ == "__main__":
    main()
