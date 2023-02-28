#!/bin/bash -e

RED="\e[31m"
YELLOW="\e[33m"
GREEN="\e[32m"
END="\e[0m"
BOLD="\e[1m"

clean_up() {
  echo "Running clean up function"
  delete_venv
  sudo docker compose -f ./UserApplication/docker-compose.yml down
  sudo docker compose -f ./UserApplication/docker-compose.yml -f ./UserApplication/docker-compose-production.yml down
}

check_if_done() {
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}$1${END}"
  else
    echo -e "${RED}Aborted : $2${END}"
    exit 1
  fi  
}

press_any_key_to_continue() {
  echo -e "$1"
  read -r -n 1 -s answer
}

create_venv() {
  python3 -m venv venv
  source venv/bin/activate
  pip3 install semgrep
  pip3 install requests
  pip3 install jira
  pip3 install python-dotenv
}

delete_venv() {
  deactivate
  rm -r ../venv/
}

clone_repository() {
  if [[ -d CI-CD-Pipeline ]]; then
    rm -fr CI-CD-Pipeline
  fi
  local repo_link="git@github.com:shreyas-acharya/CI-CD-Pipeline.git"
  git clone $repo_link &&
  cd CI-CD-Pipeline &&
  sleep 3 &&
  git submodule update --init --recursive
}

run_sast() {
  if [[ ! -d "output" ]]; then
    mkdir output
  fi 
  semgrep --config=auto --output ./output/semgrep_scan_results.json --json UserApplication &&
  python ./sast_analysis.py
  if [[ $? -eq 1 ]]; then
    echo
    press_any_key_to_continue "${YELLOW}Warnings found!!! press any key to continue${END}"
  fi
}

api_testing() {
  if [[ -e UserApplication/.env ]]; then
    rm UserApplication/.env
  fi
  touch UserApplication/.env
  echo "USERNAME=test" >> UserApplication/.env
  echo "PASSWORD=test" >> UserApplication/.env
  echo "DATABASE=test" >> UserApplication/.env
  
  sudo docker compose -f ./UserApplication/docker-compose.yml up --detach &&
  sleep 3 &&
  python3 ./api_testing.py &&
  sudo docker compose -f ./UserApplication/docker-compose.yml down
}

trivy_scanning() {
  which trivy > /dev/null 2>&1
  if [ ! $? -eq 0 ]; then
    wget https://github.com/aquasecurity/trivy/releases/download/v0.37.3/trivy_0.37.3_Linux-64bit.deb
    sudo dpkg -i trivy_0.37.3_Linux-64bit.deb
    rm -r trivy_0.37.3_Linux-64bit.deb
  fi
  sudo trivy --format json --output ./output/trivy_scan_results.json image userapplication-fastapi
  python3 ./trivy_scanning.py
}

create_env_file() {
  if [[ -e ./UserApplication/.env ]]; then
    rm ./UserApplication/.env
  fi
  touch ./UserApplication/.env  
  echo -n "Enter a username (Default: root) : "
  read username
  echo "USERNAME=${username:-root}" >> ./UserApplication/.env
  echo -n "Enter a password (Default: root) : "
  read password
  echo "PASSWORD=${password:-root}" >> ./UserApplication/.env
  echo -n "Enter database name (Default: user) : "
  read database
  echo "DATABASE=${database:-user}" >> ./UserApplication/.env
}

run_container() {
  sudo docker compose -f ./UserApplication/docker-compose.yml -f ./UserApplication/docker-compose-production.yml up
  sudo docker compose -f ./UserApplication/docker-compose.yml -f ./UserApplication/docker-compose-production.yml down
}

FUNCTIONS=(create_venv clone_repository run_sast api_testing trivy_scanning create_env_file run_container)
HEADINGS=("Create a virtual Environment" "Clone git repository" "Run SAST" "API Testing" "Trivy Scanning" "Create .env file" "Create and run container" "Clean up")
SUCCESS_MESSAGES=("Successfully created and enabled virtual env" "Successfully cloned repository" "SAST Scanning completed" "Testing completed" "Trivy Scanning completed" "Created .env file" "Containers removed" "Clean Up Successful")
FAILURE_MESSAGES=("" "" "" "" "" "" "" "")


trap clean_up EXIT
for ((INDEX=0;INDEX<${#FUNCTIONS[@]}; INDEX++))
do
  echo
  echo -e "${BOLD}Step $INDEX: ${HEADINGS[$INDEX]}${END}"
  ${FUNCTIONS[$INDEX]}
  check_if_done "${SUCCESS_MESSAGES[$INDEX]}" "${FAILURE_MESSAGES[$INDEX]}"
  seq -s- $COLUMNS|tr -d '[:digit:]'
done

