from flask import Flask, request,jsonify,send_from_directory
from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from datetime import timedelta
import cloudinary
import cloudinary.uploader
import os
import uuid

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cloudinary.config(
    cloud_name = "dhhtrfmg3",
    api_key = "979538325751399",
    api_secret = "BVdMZtvMfy8B1Og8DSrFf1YgB5E"
)

db = SQLAlchemy(app)

class Students(db.Model):
    prn = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    div = db.Column(db.String(10), nullable=False)
    rollno = db.Column(db.Integer, nullable=False)
    year = db.Column(db.String(10), nullable=False)
    branch = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(20),nullable = False)

class Teachers(db.Model):
    teacherId = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    subject = db.Column(db.Text,nullable = False)
    department = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False)
    phone = db.Column(db.String(100),nullable = False)
    password = db.Column(db.String(20),nullable = False)
    working_experience = db.Column(db.String(20),nullable = False)
    profile_pic = db.Column(db.String(255), nullable=False, default="Default Image")


class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    dept = db.Column(
        db.String(20),
        nullable=False,
        server_default='All Dept'
    )

class Achievements(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Competition(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Features(db.Model):
    feature_id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    feature_name = db.Column(db.String(100),nullable = False)
    image_url = db.Column(db.Text,nullable = False)
    details = db.Column(db.Text,nullable = False)

class Placement(db.Model):
    placement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.Text, nullable=False)

class Sports(db.Model):
    sport_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sport_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)

class SportAchievements(db.Model):
    achievement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.sport_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    rank = db.Column(db.String(50), nullable=False)
    achievement_year = db.Column(db.Integer, nullable=True)

class Events(db.Model):
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String(150), nullable=False)
    youtube_link = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)

class Parent(db.Model):
    __tablename__ = 'parent'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class StudentParent(db.Model):
    __tablename__ = 'student_parent'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_prn = db.Column(db.String(100), db.ForeignKey('students.prn'))
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    relation = db.Column(db.String(50))

class SemesterResult(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_prn = db.Column(db.String(100), db.ForeignKey('students.prn'), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    sgpa = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_prn', 'semester_number'),
    )


with app.app_context():
    db.create_all()

student_put_args = reqparse.RequestParser()
student_put_args.add_argument("name", type=str, required=True)
student_put_args.add_argument("branch", type=str, required=True)
student_put_args.add_argument("year", type=str, required=True)
student_put_args.add_argument("div", type=str, required=True)
student_put_args.add_argument("rollno", type=int, required=True)
student_put_args.add_argument("email", type=str, required=True)
student_put_args.add_argument("phone", type=str, required=True)

teacher_put_args = reqparse.RequestParser()
teacher_put_args.add_argument("name",type=str,required = True)
teacher_put_args.add_argument("subject",type=str,required= True)
teacher_put_args.add_argument("department",type=str,required= True)
teacher_put_args.add_argument("email",type=str,required= True)
teacher_put_args.add_argument("phone",type=str,required= True)
teacher_put_args.add_argument("password",type=str,required= True)
teacher_put_args.add_argument("working_experience", type=str, required=True)
teacher_put_args.add_argument("profile_pic", type=str, required=False)


announce_put_args = reqparse.RequestParser()
announce_put_args.add_argument("image", type=str, required=True)
announce_put_args.add_argument("title", type=str)
announce_put_args.add_argument("description", type=str, required=True)
announce_put_args.add_argument("dept", type=str, required=False, default="All Dept")

achievement_put_args = reqparse.RequestParser()
achievement_put_args.add_argument("image", type=str, required=True)
achievement_put_args.add_argument("title", type=str, required=True)
achievement_put_args.add_argument("description", type=str, required=True)

competition_put_args = reqparse.RequestParser()
competition_put_args.add_argument("image", type=str, required=True)
competition_put_args.add_argument("title", type=str, required=True)
competition_put_args.add_argument("description", type=str, required=True)

placement_put_args = reqparse.RequestParser()
placement_put_args.add_argument("student_name", type=str, required=True)
placement_put_args.add_argument("department", type=str, required=True)
placement_put_args.add_argument("job_role", type=str, required=True)
placement_put_args.add_argument("company_name", type=str, required=True)
placement_put_args.add_argument("package", type=str, required=True)
placement_put_args.add_argument("image_url", type=str, required=True)

sports_put_args = reqparse.RequestParser()
sports_put_args.add_argument("sport_name", type=str, required=True)
sports_put_args.add_argument("description", type=str, required=True)
sports_put_args.add_argument("image_url", type=str, required=True)

achievement_put_args = reqparse.RequestParser()
achievement_put_args.add_argument("sport_id", type=int, required=True)
achievement_put_args.add_argument("title", type=str, required=True)
achievement_put_args.add_argument("rank", type=str, required=True)
achievement_put_args.add_argument("achievement_year", type=int)

events_put_args = reqparse.RequestParser()
events_put_args.add_argument("event_name", type=str, required=True)
events_put_args.add_argument("youtube_link", type=str)
events_put_args.add_argument("description", type=str, required=True)
events_put_args.add_argument("image_url", type=str, required=True)

resource_fields = {
    'prn': fields.String,
    'name': fields.String,
    'branch': fields.String,
    'year': fields.String,
    'div': fields.String,
    'rollno': fields.Integer,
    'email': fields.String,
    'phone': fields.String
}

teacher_fields = {
    'name' : fields.String,
    'subject' : fields.String,
    'department' : fields.String,
    'email' : fields.String,
    'phone' : fields.String,
    'working_experience' : fields.String,
    'password' : fields.String,
    
    'profile_pic' : fields.String
}

announce_achieve_fields = {
    'id' : fields.Integer,
    'image': fields.String,
    'title': fields.String,
    'description': fields.String,
    'created_at' : fields.DateTime,
    'dept': fields.String
}

features_fields = {
    "feature_id": fields.Integer,
    "feature_name": fields.String,
    "image_url": fields.String,
    "details": fields.String
}

placement_fields = {
    'placement_id': fields.Integer,
    'student_name': fields.String,
    'department': fields.String,
    'job_role': fields.String,
    'company_name': fields.String,
    'package': fields.String,
    'image_url': fields.String,
}

sports_fields = {
    'sportId': fields.Integer,
    'teamName': fields.String,
    'achievement': fields.String,
    'year': fields.String,
    'image_url': fields.String,
}

result_fields = {
    'result_id': fields.Integer,
    'prn': fields.String,
    'sem1': fields.Float,
    'sem2': fields.Float,
    'sem3': fields.Float,
    'sem4': fields.Float,
    'sem5': fields.Float,
    'sem6': fields.Float,
    'sem7': fields.Float,
    'sem8': fields.Float,
    'total': fields.Float
}

events_fields = {
    'event_id': fields.Integer,
    'event_name': fields.String,
    'youtube_link': fields.String,
    'description': fields.String,
    'image_url': fields.String
}

# ==========================
#   API RESOURCES
# ==========================

class FeaturesAPI(Resource):
    @marshal_with(features_fields)
    def get(self):
        return Features.query.all()

class PlacementAPI(Resource):
    @marshal_with(placement_fields)
    def get(self):
        data = Placement.query.all()
        if not data:
            abort(404, message="No data found")
        return data

    def post(self):
        args = placement_put_args.parse_args()
        entry = Placement(**args)
        db.session.add(entry)
        db.session.commit()
        return {"message": "Placement added successfully"}, 201


class SportsAPI(Resource):
    @marshal_with(sports_fields)
    def get(self):
        data = Sports.query.all()
        return data

    def post(self):
        args = sports_put_args.parse_args()
        entry = Sports(**args)
        db.session.add(entry)
        db.session.commit()
        return {"message": "Sport added successfully"}, 201


class SportAchievementAPI(Resource):
    def get(self):
        data = SportAchievements.query.all()
        return 

    def post(self):
        args = achievement_put_args.parse_args()
        entry = SportAchievements(**args)
        db.session.add(entry)
        db.session.commit()
        return {"message": "Sport Achievement added successfully"}, 201


class EventsAPI(Resource):
    @marshal_with(events_fields)
    def get(self):
        data = Events.query.all()
        return data

    def post(self):
        args = events_put_args.parse_args()
        entry = Events(**args)
        db.session.add(entry)
        db.session.commit()
        return {"message": "Event added successfully"}, 201


class ResultAPI(Resource):
    def get(self, prn):
        semesters = SemesterResult.query.filter_by(student_prn=prn)\
            .order_by(SemesterResult.semester_number).all()

        if not semesters:
            return {"message": "No result found"}, 404

        total = sum([s.sgpa for s in semesters])
        count = len(semesters)
        cgpa = round(total / count, 2)

        semester_data = [
            {
                "semester": s.semester_number,
                "sgpa": s.sgpa
            } for s in semesters
        ]

        return {
            "prn": prn,
            "overall_cgpa": cgpa,
            "semesters": semester_data
        }

    def post(self):
        data = request.get_json()

        student_prn = data.get("student_prn")
        semester_number = data.get("semester_number")
        sgpa = data.get("sgpa")

        if not all([student_prn, semester_number, sgpa]):
            return {"error": "Missing required fields"}, 400

        entry = SemesterResult(
            student_prn=student_prn,
            semester_number=semester_number,
            sgpa=sgpa
        )

        try:
            db.session.add(entry)
            db.session.commit()
            return {"message": "SGPA added"}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": "Semester already exists"}, 400



@app.route("/test_db")
def test_db():
    try:
        all_students = Students.query.all()
        count = len(all_students)
        return {"message": f"Database connected successfully! Total students: {count}"}, 200
    except Exception as e:
        return {"error": str(e)}, 500



@app.route('/upload_post',methods=['POST','DELETE'])
def upload_post():
    if request.method == 'POST':
        try:
            # get the umage,title and description from android multipart
            image = request.files['image']
            title = request.form['title']
            description = request.form['description']
            category = request.form['category'].lower()
            dept = request.form.get('dept', 'All Dept')
            # print("Category Recieved => ",category)

            # This makes sure the file name is safe and does not contain dangerous characters (e.g., ../ or \)

            # upload_image = cloudinary.uploader.upload(
            #     image,
            #     public_id = category,
            #     unique_filename = True,
            #     overwrite = False
            # )

            upload_image = cloudinary.uploader.upload(
            image,
            folder=category,          # announcement / achievement / event
            resource_type="image"
            )

            image_url = upload_image['secure_url']

            if (category == "announcement"):
                announcement = Announcements(image=image_url,title=title,description=description,dept=dept)
                db.session.add(announcement)
                db.session.commit()
                print(">> Commit Session Successfully")

            elif category == "achievement":
                achievement = Achievements(image=image_url, title=title, description=description)
                db.session.add(achievement)
                db.session.commit()
                print(">> Commit Session Successfully")

            elif category == "event":

                youtube_link = request.form.get("youtube_link", "")

                event = Events(
                    event_name=title,
                    youtube_link=youtube_link,
                    description=description,
                    image_url=image_url
                )

                db.session.add(event)
                db.session.commit()

                print(">> Commit Session Successfully")

            elif(category == "attendance"):
                pass

            else:
                print("Some thing went wrong")
                return jsonify({"message":"Upload Failed"}),500

            return jsonify({
                "message" : "Upload successful",
                "title" : title,
                "description" : description,
                "image_url" : image_url
            }),200
        
        except Exception as e:
            print(str(e))
            return jsonify({
                "error" : str(e)
            }),500
        
    elif request.method == 'DELETE':
        result = Students.query.filter_by(id =id ).first()
        if not result:
            abort(404, message=f"PRN {id} not found")
        db.session.delete(result)
        db.session.commit()
        return {"message": "Student deleted successfully"}, 200

class TeacherDetails(Resource):
    @marshal_with(teacher_fields)
    def get(self,teacherId):
        try:
            teacherData = Teachers.query.filter_by(teacherId = teacherId).first()
            if not teacherData:
                abort(404,message = f"Teacher Not Found")
            
            return teacherData
        except Exception as e:
            print(str(e))
    
    @marshal_with(teacher_fields)
    def put(self,teacherId):
        try:
            teacher = Teachers.query.filter_by(teacherId = teacherId).first()
            if teacher:
                abort(409,message=f"Teacher allready Exists.")
            args = teacher_put_args.parse_args()
            teacher = Teachers(teacherId = teacherId,**args)
            db.session.add(teacher)
            db.session.commit()
            print(">>Commit Successfully")
            return teacher,201
        except Exception as e:
            print(str(e))

    def delete(self, teacherId):
        teacherCheck = Teachers.query.filter_by(teacherId = teacherId).first()
        if not teacherCheck:
            abort(404, message=f"PRN {teacherId} not found")
        db.session.delete(teacherCheck)
        db.session.commit()
        return {"message": "Student deleted successfully"}, 200

class TeachersList(Resource):

    @marshal_with(teacher_fields)
    def get(self):
        return Teachers.query.all()

class StudentByPRN(Resource):
    @marshal_with(resource_fields)
    def get(self, stu_prn):
        try:
            result = Students.query.filter_by(prn=stu_prn).first()
            if not result:
                abort(404, message=f"PRN {stu_prn} not found")
            return result
        except Exception as e:
            print(str(e))

    @marshal_with(resource_fields)
    def put(self, stu_prn):
        result = Students.query.filter_by(prn=stu_prn).first()
        if result:
            abort(409, message="Student already exists.")
        args = student_put_args.parse_args()
        student = Students(prn=stu_prn, **args)
        db.session.add(student)
        db.session.commit()
        return student, 201

    def delete(self, stu_prn):
        result = Students.query.filter_by(prn=stu_prn).first()
        if not result:
            abort(404, message=f"PRN {stu_prn} not found")
        db.session.delete(result)
        db.session.commit()
        return {"message": "Student deleted successfully"}, 200

class StudentByDetails(Resource):
    @marshal_with(resource_fields)
    def get(self, branch, year, div, rollno):
        result = Students.query.filter_by(branch=branch, year=year, div=div, rollno=rollno).first()
        if not result:
            abort(404, message="Student not found")
        return result

# Check Student Function
class checkStudent(Resource):
    @marshal_with(resource_fields)
    def get(self, stu_prn, email):
        student = Students.query.filter_by(prn=stu_prn, email=email).first()
        if not student or not student.email == email:
            return {"msg": "prn and email required"}, 400

        return student, 200
    
#Check Teacher Function
class checkTeacher(Resource):
    @marshal_with(teacher_fields)
    def get(self):

        teacher_id = request.args.get("teacherId")
        email = request.args.get("email")

        teacher = Teachers.query.filter_by(teacherId=teacher_id, email=email).first()
        if not teacher:
            return {"msg": "prn and password required"}, 400

        return teacher, 200

class ParentLogin(Resource):

    def post(self):
        data = request.get_json()

        phone = data.get("phone_number")
        password = data.get("password")

        parent = Parent.query.filter_by(
            phone_number=phone,
            password=password
        ).first()

        if not parent:
            return {"status": "error", "message": "Invalid credentials"}, 401

        return {
            "status": "success",
            "parent_id": parent.id,
            "name": parent.name
        }, 200

class ParentStudentsResource(Resource):

    def get(self, parent_id):

        data = db.session.query(Students, StudentParent.relation).join(
            StudentParent, Students.prn == StudentParent.student_prn
        ).filter(
            StudentParent.parent_id == parent_id
        ).all()

        result = []

        for student, relation in data:
            result.append({
                "name": student.name,
                "prn": student.prn,
                "branch": student.branch,
                "year": student.year,
                "relation": relation
            })

        return {"students": result}, 200


class GetData(Resource):
    @marshal_with(announce_achieve_fields)
    def get(self, mode):
        dept = request.args.get("dept", "All Dept")
        if mode == 0:
            result = Announcements.query.filter((Announcements.dept == dept) | (Announcements.dept == "All Dept")).all()
        elif mode == 1:
            result = Achievements.query.all()
        elif mode == 2:
            result = Events.query.all()
        else:
            abort(400, message="Invalid mode")
        return result


api.add_resource(StudentByPRN, "/student/<string:stu_prn>")
api.add_resource(StudentByDetails, "/student/<string:branch>/<string:year>/<string:div>/<int:rollno>")
api.add_resource(checkStudent, "/student/<string:stu_prn>/<string:email>")
api.add_resource(TeacherDetails,"/teacher/<int:teacherId>")
api.add_resource(TeachersList, "/teachers")
api.add_resource(checkTeacher,"/checkTeacher")
api.add_resource(GetData, "/getData/<int:mode>/all")
api.add_resource(ResultAPI, "/result/<string:prn>")
api.add_resource(ParentLogin, "/parent/login")
api.add_resource(ParentStudentsResource, "/parent/<int:parent_id>/students")



# ==========================
#   ROUTES REGISTRATION
# ==========================

api.add_resource(FeaturesAPI, "/features")
api.add_resource(PlacementAPI, "/placements")
api.add_resource(SportsAPI, "/sports")
api.add_resource(SportAchievementAPI, "/sportAchievements")
api.add_resource(EventsAPI, "/events")

if __name__ == '__main__':
    app.run()
