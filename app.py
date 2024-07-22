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
    # Check for changes
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True
    )
    if result.stdout.strip() == "":
        print("No changes to commit.")
        return  # Exit the function early if there are no changes

    # If there are changes, proceed with commit
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
    # Checkout back to the main branch
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_path, check=True
    )  # Adjust if your main branch has a different name

    # Push changes and create a PR
    github_token = os.getenv(
        "GITHUB_TOKEN"
    )  # Ensure you've set this environment variable
    repo_full_name = "your_github_username/your_repo_name"  # Replace with your GitHub username and repository name
    push_changes_and_create_pr(
        branch_name, repo_path, commit_message
    )


def push_changes_and_create_pr(branch_name, repo_path, commit_message):
    # Push the changes
    subprocess.run(
        ["git", "push", "--set-upstream", "origin", branch_name],
        cwd=repo_path,
        check=True,
    )

    # Create a pull request using GitHub CLI
    pr_create_command = [
        "gh",
        "pr",
        "create",
        "--title",
        commit_message,
        "--body",
        f"Automated pull request for {branch_name}",
        "--head",
        branch_name,
        "--base",
        "main",  # Adjust if your main branch has a different name
    ]
    subprocess.run(pr_create_command, cwd=repo_path, check=True)


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
            json.dump(json_obj, file, indent=4)

        # Commit the changes and checkout back to the main branch
        commit_message = f"Add {manufacturer} {name} fixture"
        git_commit_and_checkout(branch_name, root_directory, commit_message)


# The rest of the script remains unchanged


# Define the root directory for the Git repository
root_directory = "Open_fixture.lib"


with open("import.json") as file:
    json_data = json.load(file)

save_json_objects(json_data, root_directory)
