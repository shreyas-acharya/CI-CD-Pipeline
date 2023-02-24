import requests
import sys

BASE_URL = "http://0.0.0.0:8000"


def check_validity(response, expected):
    print(response.json())
    print(expected)
    if "status_code" in response.json():
        if response.json()["detail"] != expected:
            sys.exit(2)
    elif response.json() != expected:
        sys.exit(2)


def base_address_testing(expected):
    check_validity(requests.get(f"{BASE_URL}"), expected)


def get_users(expected):
    check_validity(requests.get(f"{BASE_URL}/getUsers"), expected)


def add_user(data, expected):
    check_validity(
        requests.post(
            f"{BASE_URL}/addUser",
            json=data,
        ),
        expected,
    )


def login(username, password, expected):
    check_validity(
        requests.post(
            f"{BASE_URL}/login", json={"username": username, "password": password}
        ),
        expected,
    )


def logout(expected):
    check_validity(requests.post(f"{BASE_URL}/logout"), expected)


def get_details(expected):
    check_validity(requests.get(f"{BASE_URL}/getDetails"), expected)


def update_user(expected, new_data):
    check_validity(requests.patch(f"{BASE_URL}/updateUser", json=new_data), expected)


def delete_user(expected):
    check_validity(requests.delete(f"{BASE_URL}/deleteUser"), expected)


def main():
    data = {
        "username": "testa",
        "password": "testa",
        "fullname": "Test A",
        "email": "testa@example.com",
        "age": 10,
    }
    print("-------------------------------TESTING------------------------------------")
    print("\n")
    print(f"Testing endpoint: {BASE_URL}/")
    base_address_testing(expected="User Application is running")
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/getUsers")
    get_users(expected=[])
    add_user(data=data, expected=data)
    get_users(expected=[{"username": "testa"}])
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/addUser")
    add_user(data=data, expected="Username already exists!!!")
    data = {
        "username": "testb",
        "password": "testb",
        "fullname": "Test B",
        "email": "testb@example.com",
        "age": 10,
    }
    add_user(data=data, expected=data)
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/login")
    login(username="testx", password="testx", expected="User doesn't exits")
    login(username="testa", password="testx", expected="Incorrect password")
    login(username="testa", password="testa", expected="Login Successful : testa")
    login(
        username="testb",
        password="testb",
        expected="Logout : testa   Login Successful : testb",
    )
    login(username="testb", password="testb", expected="Already logged in")
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/logout")
    logout(expected="Logout Successful : testb")
    logout(expected="No user logged in!!!")
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/getDetails")
    get_details(expected="No user logged in!!!")
    login(username="testb", password="testb", expected="Login Successful : testb")
    get_details(expected=data)
    print("Test Successful\n")

    data = {
        "username": "testb",
        "password": "testb",
        "fullname": "Test B",
        "email": "testb@example.com",
        "age": 20,
    }
    print(f"Testing endpoint: {BASE_URL}/updateUser")
    logout(expected="Logout Successful : testb")
    update_user(expected="No user logged in!!!", new_data=data)
    login(username="testb", password="testb", expected="Login Successful : testb")
    update_user(expected="User Information Updated", new_data=data)
    get_details(expected=data)
    print("Test Successful\n")

    print(f"Testing endpoint: {BASE_URL}/deleteUser")
    logout(expected="Logout Successful : testb")
    delete_user(expected="No user logged in!!!")
    login(username="testb", password="testb", expected="Login Successful : testb")
    delete_user(expected="User Deleted")
    get_users(expected=[{"username": "testa"}])
    print("Test Successful\n")

    print("-------------------------------DONE------------------------------------")


main()
