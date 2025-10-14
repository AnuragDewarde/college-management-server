import requests

baseUrl = "http://127.0.0.1:5000/"

student = {
    "name" : "Anurag",
    "branch": "CSE",
    "year" : "TY",
    "div" : "B",
    "rollno" : 7,
    "email":"anuragdewarde@gmail.com",
    "phone":"9130395475"
}

teacher = {
    "name" : "Code with Harry",
    "subject" : "Coding Master",
    "department" : "Computer Science",
    "email" : "codewithharry45@gmail.com",
    "phone" : "9922804545",
    "password" : "Code@4545"
}

checkTeacher = {
    'teacher_id': '6764',
    'email': 'codewithharry45@gmail.com'
}

response = requests.get(baseUrl+"getData/0/all")
print(response.json())

# data = {
#     'mode': '0',  # 0 for Announcement, 1 for Achievement
#     'title': 'Image Demo',
#     'discription': 'dashboard ui design and working'
# }

# files = {
#     "image":open("D:/Python_AI/FlaskOneShot/Dashboard.png",'rb')
# }

# response = requests.get(baseUrl + "student/14/anuragdewarde@gmail.com")
# print(response)