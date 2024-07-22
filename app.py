import os
import sys
import json
import time
import requests
import subprocess


def create_git_branch(branch_name, repo_path):
    # Save the current working directory
    original_cwd = os.getcwd()
    try:
        # Change the working directory to the specified repo path
        os.chdir(repo_path)
        # Check if the branch exists
        branch_exists = subprocess.run(
            ["git", "rev-parse", "--verify", branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if branch_exists.returncode == 0:
            # Checkout the branch if it exists
            subprocess.run(["git", "checkout", branch_name], check=True)
        else:
            # Create and checkout the branch if it does not exist
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    finally:
        # Change back to the original working directory
        os.chdir(original_cwd)


def git_commit_and_checkout(branch_name, repo_path, commit_message):
    original_cwd = os.getcwd()
    try:
        os.chdir(repo_path)
        # Add changes to the staging area and commit
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        # Checkout back to the main branch
        subprocess.run(
            ["git", "checkout", "main"], check=True
        )  # Adjust if your main branch has a different name
    finally:
        os.chdir(original_cwd)

    # Push changes and create a PR
    github_token = os.getenv(
        "GITHUB_TOKEN"
    )  # Ensure you've set this environment variable
    repo_full_name = "your_github_username/your_repo_name"  # Replace with your GitHub username and repository name
    push_changes_and_create_pr(
        branch_name, repo_path, commit_message, github_token, repo_full_name
    )


def push_changes_and_create_pr(
    branch_name, repo_path, commit_message, github_token, repo_full_name
):
    # Push the changes
    subprocess.run(
        ["git", "push", "--set-upstream", "origin", branch_name],
        cwd=repo_path,
        check=True,
    )

    # Create a pull request
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": commit_message,
        "head": branch_name,
        "base": "main",  # or "master" if your repository uses the old naming convention
        "body": f"Automated pull request for {branch_name}",
    }
    response = requests.post(
        f"https://api.github.com/repos/{repo_full_name}/pulls",
        headers=headers,
        json=data,
    )
    if response.status_code == 201:
        print(f"Pull request created successfully: {response.json()['html_url']}")
    else:
        print(f"Failed to create pull request: {response.status_code}, {response.text}")


def save_json_objects(json_list, root_directory):
    for json_obj in json_list:
        manufacturer = json_obj["Manufacturer"]
        name = json_obj["Name"].replace(" ", "-")
        branch_name = f"{manufacturer}-{name}".lower()
        # Create a branch for each fixture
        create_git_branch(branch_name, root_directory)

        filename = f"{name}.json"
        directory = os.path.join(root_directory, f"Fixtures/{manufacturer}")
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            json.dump(json_obj, file)

        # Commit the changes and checkout back to the main branch
        commit_message = f"Add {manufacturer} {name} fixture"
        git_commit_and_checkout(branch_name, root_directory, commit_message)


# The rest of the script remains unchanged


# Define the root directory for the Git repository
root_directory = "Open_fixture.lib"


with open("import.json") as file:
    json_data = json.load(file)

save_json_objects(json_data, root_directory)
