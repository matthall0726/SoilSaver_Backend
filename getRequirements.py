import os
import subprocess


# GitHub repository URL
repo_url = "https://github.com/matthall0726/SoilSaver_Backend"

# Directory to clone the repository into
project_directory = "SoilSaver_Backend"

# Clone the GitHub repository
subprocess.run(["git", "pull", repo_url])

# # Change to the project directory
# os.chdir(project_directory)
# print(subprocess.run(["pwd"]))

# Install requirements from requirements.txt
subprocess.run(["pip3", "install", "--upgrade", "-r", "requirements.txt"])

# Make main.py executable
subprocess.run(["python3", "main.py"])




