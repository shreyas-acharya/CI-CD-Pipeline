# Continuous Integration and Continous Deployment Pipeline

## What is CI/CD pipeline?
A pipeline is a process that drives software development through a path of building, testing, and deploying code, also known as CI/CD. By automating the process, the objective is to minimize human error and maintain a consistent process for how software is released. Tools that are included in the pipeline could include compiling code, unit tests, code analysis, security, and binaries creation. For containerized environments, this pipeline would also include packaging the code into a container image to be deployed across a hybrid cloud.    

![CI CD Pipeline](https://javamaster.it/wp-content/uploads/2021/04/cicd.png) 

## Installation Steps:
### Step 1:
Create a .env file with the following fields:   
```
JIRA_EMAIL=<jira_email>
JIRA_TOKEN=<jira_API_token>
JIRA_SERVER=<jira_server_url>
```
### Step 2:
Run the following command:   
```bash
 if command -v curl >/dev/null 2>&1; then     bash -c "$(curl -fsSL https://raw.githubusercontent.com/shreyas-acharya/CI-CD-Pipeline/HEAD/install.sh)"; else     bash -c "$(wget -O- https://raw.githubusercontent.com/shreyas-acharya/CI-CD-Pipeline/HEAD/install.sh)"; fi
```

## Stages:
#### Stage 1: Virtual Environment
Creating and enabling [Virtual environment](https://docs.python.org/3/library/venv.html).   
List of modules installed:    
- [Semgrep](https://semgrep.dev/) : a static application security testing tool
- [Requests](https://pypi.org/project/requests/) : HTTP library for python
- [Jira](https://pypi.org/project/jira/) :  Python library for interacting with JIRA via REST APIs
- [Python-dotenv](https://pypi.org/project/python-dotenv/) :  Python library to read key-value pairs from a .env file and set then as environment variables

#### Stage 2: Cloning Repository
Cloning the repository and updating the [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), User Application.   

#### Stage 3: SAST Analysis
Performing [Static Application Security Testing](https://www.synopsys.com/glossary/what-is-sast.html). SAST or static analysis, is a testing methodology that analyzes source code to find security vulnerabilities that make your organization’s applications susceptible to attack. It scans an application before the code is compiled. It’s also known as white box testing. The python library used for SAST testing was [Semgrep](https://semgrep.dev/).    

#### Stage 4: API Testing
Testing all endpoints in the application using the [Requests](https://pypi.org/projct/requests/) library. 

#### Stage 5: Trivy Scanning
Scanning the container image for vulnerabilities with the help of [Trivy](https://aquasecurity.github.io/trivy/v0.17.2). Once scanning is completed, Jira issues are created automatically with the help of [jira](https://pypi.org/project/jira/), a python library to interact with JIRA.

#### Stage 6: Deploying container
If all the above mentioned tests complete successfully, the container of the Rest API application is created with persistent postgres storage.
