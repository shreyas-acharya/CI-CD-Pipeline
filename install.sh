#!/bin/bash

RED="\e[31m"
YELLOW="\e[33m"
GREEN="\e[32m"
END="\e[0m"
BOLD="\e[1m"

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

clone_repository() {
  if [[ -d CI-CD-Pipeline ]]; then
    rm -fr CI-CD-Pipeline
  fi
  local repo_link="git@github.com:shreyas-acharya/CI-CD-Pipeline.git"
  git clone $repo_link &&
  cd CI-CD-Pipeline &&
  git submodule update --init --recursive
}

run_sast() {
  semgrep --config=auto --output scan_results.json --json UserApplication &&
  python ./sast_analysis.py
  if [[ $? -eq 1 ]]; then
    echo
    press_any_key_to_continue "${YELLOW}Warnings found!!! press any key to continue${END}"
  fi
}

api_testing() {
  cd UserApplication
  if [[ -e .env ]]; then
    rm .env
  fi
  touch .env
  echo "USERNAME=test" >> .env
  echo "PASSWORD=test" >> .env
  echo "DATABASE=test" >> .env
  
  docker compose up &&
  python3 api_testing.py &&
  docker compose down &&
  cd ..
}

create_env_file() {
  cd UserApplication
  if [[ -e .env ]]; then
    rm .env
  fi
  touch .env  
  echo -n "Enter a username (Default: root) : "
  read username
  echo "USERNAME=${username:-root}" >> .env
  echo -n "Enter a password (Default: root) : "
  read password
  echo "PASSWORD=${password:-root}" >> .env
  echo -n "Enter database name (Default: user) : "
  read database
  echo "DATABASE=${database:-user}" >> .env
}

run_container() {
  sudo docker compose up
  sudo docker compose down
}

FUNCTIONS=(clone_repository run_sast api_testing create_env_file run_container)
HEADINGS=("Clone git repository" "Run SAST" "API Testing" "Create .env file" "Create and run container")
SUCCESS_MESSAGES=("Successfully cloned repository" "Scanning completed" "Testing completed" "Created .env file" "Containers removed")
FAILURE_MESSAGES=("" "" "" "" "")


for ((INDEX=0;INDEX<${#FUNCTIONS[@]}; INDEX++))
do
  echo
  echo -e "${BOLD}Step $INDEX: ${HEADINGS[$INDEX]}${END}"
  ${FUNCTIONS[$INDEX]}
  check_if_done "${SUCCESS_MESSAGES[$INDEX]}" "${FAILURE_MESSAGES[$INDEX]}"
  seq -s- $COLUMNS|tr -d '[:digit:]'
done

