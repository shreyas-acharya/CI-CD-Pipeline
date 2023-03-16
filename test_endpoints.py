import requests
from contextlib import contextmanager
import socket
import time
import pytest
import sys

BASE_URL = "http://0.0.0.0:8000"
timeout = 3


@pytest.fixture
def check_if_port_up():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for _ in range(10):
        result = sock.connect_ex(("0.0.0.0", 8000))
        if result == 0:
            return
        else:
            print(".", end="")
            time.sleep(timeout)
    sys.exit(1)


@contextmanager
def test_session():
    try:
        add_user(
            {
                "username": "testa",
                "password": "testa",
                "fullname": "Test A",
                "email": "testa@example.com",
                "age": 10,
            }
        )
        add_user(
            {
                "username": "testb",
                "password": "testb",
                "fullname": "Test B",
                "email": "testb@example.com",
                "age": 15,
            }
        )
        yield None
    finally:
        requests.delete(f"{BASE_URL}/deleteAll")


def check_validity(response, expected):
    if "status_code" in response.json():
        assert response.json()["detail"] == expected
    else:
        assert response.json() == expected


def get_users():
    return requests.get(f"{BASE_URL}/getUsers")


def add_user(data):
    return requests.post(
        f"{BASE_URL}/addUser",
        json=data,
    )


def login(username, password):
    return requests.post(
        f"{BASE_URL}/login", json={"username": username, "password": password}
    )


def logout():
    return requests.post(f"{BASE_URL}/logout")


def get_details():
    return requests.get(f"{BASE_URL}/getDetails")


def update_user(new_data):
    return requests.patch(f"{BASE_URL}/updateUser", json=new_data)


def delete_user():
    return requests.delete(f"{BASE_URL}/deleteUser")


def test_endpoint_getUsers(check_if_port_up):
    check_validity(get_users(), [])
    with test_session() as _:
        check_validity(get_users(), [{"username": "testa"}, {"username": "testb"}])


def test_endpoint_addUser(check_if_port_up):
    with test_session() as _:
        data = {
            "username": "testc",
            "password": "testc",
            "fullname": "Test C",
            "email": "testc@example.com",
            "age": 20,
        }
        check_validity(add_user(data), data)
        check_validity(add_user(data), "Username already exists!!!")


def test_endpoint_login(check_if_port_up):
    with test_session() as _:
        check_validity(login("testx", "testx"), "User doesn't exists")
        check_validity(login("testa", "testx"), "Incorrect password")
        check_validity(login("testa", "testa"), "Login Successful : testa")
        check_validity(
            login("testb", "testb"), "Logout : testa   Login Successful : testb"
        )
        check_validity(login("testb", "testb"), "Already logged in")


def test_endpoint_logout(check_if_port_up):
    with test_session() as _:
        check_validity(login("testa", "testa"), "Login Successful : testa")
        check_validity(logout(), "Logout Successful : testa")
        check_validity(logout(), "No user logged in!!!")


def test_endpoint_getDetails(check_if_port_up):
    with test_session() as _:
        check_validity(get_details(), "No user logged in!!!")
        check_validity(login("testa", "testa"), "Login Successful : testa")
        check_validity(
            get_details(),
            {
                "username": "testa",
                "password": "testa",
                "fullname": "Test A",
                "email": "testa@example.com",
                "age": 10,
            },
        )


def test_endpoint_updateUser(check_if_port_up):
    with test_session() as _:
        check_validity(update_user({}), "No user logged in!!!")
        check_validity(login("testa", "testa"), "Login Successful : testa")
        check_validity(
            update_user(
                {
                    "username": "testa",
                    "password": "testa",
                    "fullname": "Test A",
                    "email": "testa@example.com",
                    "age": 30,
                }
            ),
            "User Information Updated",
        )
        check_validity(
            get_details(),
            {
                "username": "testa",
                "password": "testa",
                "fullname": "Test A",
                "email": "testa@example.com",
                "age": 30,
            },
        )


def test_endpoint_deleteUser(check_if_port_up):
    with test_session() as _:
        check_validity(delete_user(), "No user logged in!!!")
        check_validity(login("testa", "testa"), "Login Successful : testa")
        check_validity(delete_user(), "User Deleted")
        check_validity(get_users(), [{"username": "testb"}])
