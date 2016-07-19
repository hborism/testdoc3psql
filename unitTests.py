import requests

print("-------------------UNIT TESTS-----------------------")

print("Getting user info")







response=None
response=requests.get("http://localhost/bacon")

print(response.json())
