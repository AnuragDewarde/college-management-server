from flask import Flask, request,jsonify,send_from_directory
from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Anurag%405475@127.0.0.1:3306/college'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'ImageData')
app.config['ALLOWED_EXTENTIONS'] = set(['jpg', 'png', 'jpeg', 'gif'])

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
    subject = db.Column(db.String(100),nullable = False)
    department = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False)
    phone = db.Column(db.String(100),nullable = False)
    password = db.Column(db.String(20),nullable = False)


class Announcements(db.Model):
    id = db.Column(db.Integer,primary_key = True, autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Achievements(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Events(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

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

announce_put_args = reqparse.RequestParser()
announce_put_args.add_argument("image", type=str, required=True)
announce_put_args.add_argument("title", type=str)
announce_put_args.add_argument("description", type=str, required=True)

achievement_put_args = reqparse.RequestParser()
achievement_put_args.add_argument("image", type=str, required=True)
achievement_put_args.add_argument("title", type=str, required=True)
achievement_put_args.add_argument("description", type=str, required=True)

event_put_args = reqparse.RequestParser()
event_put_args.add_argument("image", type=str, required=True)
event_put_args.add_argument("title", type=str, required=True)
event_put_args.add_argument("description", type=str, required=True)

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
    'password' : fields.String
}

announce_achieve_fields = {
    'id' : fields.Integer,
    'image': fields.String,
    'title': fields.String,
    'description': fields.String,
    'created_at' : fields.DateTime
}


# GET IMAGE FROM THE SERVER AND DISPLAY IT TO THE USER
@app.route('/ImageData/<category>/<filename>')
def uploaded_file(category, filename):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], category)
    filepath = os.path.join(directory, filename)

    # Optional: Add debug if file doesn't exist
    if not os.path.isfile(filepath):
        return jsonify({"error": f"File not found: {filepath}"}), 404

    return send_from_directory(directory, filename)

@app.route('/upload_post',methods=['POST','DELETE'])
def upload_post():
    if request.method == 'POST':
        try:
            # get the umage,title and description from android multipart
            image = request.files['image']
            title = request.form['title']
            description = request.form['description']
            category = request.form['category'].lower()
            print("Category Recieved => ",category)

            # This makes sure the file name is safe and does not contain dangerous characters (e.g., ../ or \).
            filename = secure_filename(image.filename)

            # Create a unique filename to avoid overwritting problem
            ext = os.path.splitext(filename)[1] # to get the extention of file eg. jpg, png
            unique_filename = f"{uuid.uuid4().hex}{ext}"

            # select the folder in which the image will save
            save_dir = os.path.join(app.config['UPLOAD_FOLDER'], category)
            os.makedirs(save_dir, exist_ok=True)

            # save file on server
            filepath = os.path.join(save_dir,unique_filename)
            image.save(filepath)

            # create a image url to access it later for image display and db store
            image_url = f"http://192.168.119.195:5000/ImageData/{category}/{unique_filename}"

            if (category == "announcement"):
                announcement = Announcements(image= image_url,title=title,description=description)
                db.session.add(announcement)
                db.session.commit()
                print(">> Commit Session Successfully")

            elif category == "achievement":
                achievement = Achievements(image=image_url, title=title, description=description)
                db.session.add(achievement)
                db.session.commit()
                print(">> Commit Session Successfully")

            elif category == "event":
                event = Events(image=image_url, title=title, description=description)
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
        result = Students.query.filter_by(prn=stu_prn, email=email).first()
        if not result:
            abort(404, message="Student not found")
            return result
        return result
    
#Check Teacher Function
class checkTeacher(Resource):
    @marshal_with(teacher_fields)
    def get(self):

        teacher_id = request.args.get("teacherId")
        email = request.args.get("email")

        result = Teachers.query.filter_by(teacherId=teacher_id, email=email).first()
        if not result:
            abort(404, message="Teacher not found")
            return result
        return result
    print("outside")


class GetData(Resource):
    @marshal_with(announce_achieve_fields)
    def get(self, mode):
        if mode == 0:
            result = Announcements.query.all()
        elif mode == 1:
            result = Achievements.query.all()
        elif mode == 2:
            result = Events.query.all()
        else:
            abort(400, message="Invalid mode")

        if not result:
            abort(404, message="No data found")
        return result


api.add_resource(StudentByPRN, "/student/<string:stu_prn>")
api.add_resource(StudentByDetails, "/student/<string:branch>/<string:year>/<string:div>/<int:rollno>")
api.add_resource(checkStudent, "/student/<string:stu_prn>/<string:email>")
api.add_resource(TeacherDetails,"/teacher/<int:teacherId>")
api.add_resource(checkTeacher,"/checkTeacher")
api.add_resource(GetData, "/getData/<int:mode>/all")

if __name__ == '__main__':
    app.run()
