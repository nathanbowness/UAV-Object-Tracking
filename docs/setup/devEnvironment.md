# Development Requirements 
The development requirements for this project are as follows:
1. Python 3.10
2. Pip
3. (Optional) The Nvidia toolkit installed so a GPU can be used and accessed.

## Running Using Local Python Environment
- Install the required python version
- Install pip if you don't already have it
- Setup a virtual environemtn for this project
- Install all dependencies using `pip install -r requirements.txt`

## Using Development Containers (A bit more setup, but easier long term)
- Install VSCode or your favorite IDE with [development container](https://containers.dev/) support. These instructions will assume VSCode is used.

### VSCode
- Ensure you have docker installed on your computer.
- Install the VSCode "Dev Containers" containers extension.
- Now you should be able to enter "CTRL+SHIFT+P", type in "Dev Containers: Build and Open in Container" 
  - This will use the existing .devcontainer.json to automatically setup the environment on your PC.