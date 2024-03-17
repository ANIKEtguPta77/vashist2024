from flask import render_template,url_for,redirect,flash,request,send_from_directory
from agrihub import app,db,bcrypt
from agrihub.forms import RegistrationFormBuyer,RegistrationFormFarmer,LoginFormBuyer,LoginFormFarmer,CropForm,ItemForm
from flask_login import login_required,logout_user
from agrihub.models import Farmer,Buyer,Crop,Item
from flask_login import login_user,current_user,logout_user,login_required
import pickle 
import random

# model=pickle.load(open("./agrihub/model.pkl","rb"))

input_dict={
    "farmernews":["Farmer_Protest.mp4","Farmer_Protest1.mp4","1.mp4","2.mp4"],
    "learnenglish":["1.mp4","2.mp4","Fast_English_.mp4","native_english.mp4"],
    "lesswaterfarming":["Drought_Resistant.mp4","Dryland_Agriculture.mp4","HydroPonic_a.mp4","next_gen.mp4"],
}


@app.route("/")
@app.route("/home")
def home():
    print("home")
    return render_template('home.html')


@app.route('/predictor', methods=["GET","POST"])
def predictor():
    if(request.method=="POST"):
        nitrogen=request.form["Nitrogen"]
        phosphorus=request.form["phosphorus"]
        potassium=request.form["potassium"]
        temper=request.form["temperature"]
        hum=request.form["humidity"]
        ph=request.form["ph"]
        rf=request.form["rainfall"]
        prediction=model.predict([[nitrogen,phosphorus,potassium,temper,hum,ph,rf]])
        return render_template('prediction.html',predict=prediction)
    return render_template('predictor.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/marketprice')
def marketprice():
    return render_template('marketprice.html')


@app.route('/soiltestcenter')
def soiltestcenter():
    return render_template('soiltestcenter.html')


@app.route('/successcrop')
def successcrop():
    return render_template('successcrop.html')


@app.route('/successitem')
def successitem():
    return render_template('successitem.html')


@app.route('/farmerdecision')
def farmerdecision():
    return render_template('farmerdecision.html')



@app.route('/register')
def register():
    print("register")
    return render_template('register.html')


@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename)


@app.route('/learning',methods=['GET','POST'])
def learning():
    if request.method == 'POST':
        input_text = request.form.get('input_text', '').lower()  # Get input_text from form
        if input_text in input_dict:
            return render_template('learning.html', video_urls=input_dict[input_text])
        else:
            return render_template('learning.html', video_urls=input_dict["farmernews"])
    else:
        return render_template('learning.html', video_urls=input_dict['farmernews'])  # Pass None to video_urls initially
    

todos = [
    {
        'id': 1,
        'name': 'Write SQL',
        'checked': False
    },
    {
        'id': 2,
        'name': 'Write Python',
        'checked': True
    }
]

# @app.route("/", methods=["GET", "POST"])
@app.route("/todo", methods=["GET", "POST"])
def todo():
    if (request.method == "POST"):
        todo_name = request.form["todo_name"]
        cur_id = random.randint(1, 1000)
        todos.append(
            {
            'id': cur_id,
            'name': todo_name,
            'checked': False
            }
        )
        return redirect(url_for("todo"))
    return render_template("todo.html", items=todos)

@app.route("/checked/<int:todo_id>", methods=["POST"])
def checked_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['checked'] = not todo['checked']  # Toggle the status
            break
    return redirect(url_for("todo"))

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    global todos
    for todo in todos:
        if todo['id'] == todo_id:
            todos.remove(todo)
    return redirect(url_for("todo"))

@app.route("/registerFarmer" ,methods=['GET','POST'])
def registerFarmer():
    print("farmer register")
    # if current_user.is_authenticated:
    #     print("authenticated")
    #     return redirect(url_for('home'))
    print("farmer not authenticated")
    form=RegistrationFormFarmer()
    if form.validate_on_submit():
        print("validate on submit")
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode ('utf-8')
        farmer=Farmer(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(farmer)
        db.session.commit()
        print(Farmer.query.filter_by(username=form.username.data).first())
        print("added to database")
        flash('Your account has been created! You are now able to log in')
        return redirect(url_for('farmerLogin'))
    return render_template('register_farmer.html',form=form)

@app.route("/registerBuyer",methods=['GET','POST'])
def registerBuyer():
    print("hello")
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    form=RegistrationFormBuyer()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode ('utf-8')
        buyer=Buyer(username=form.username.data,email=form.email.data,password=hashed_password)
        print(buyer)
        db.session.add(buyer)
        db.session.commit()
        flash('Your account has been created! You are now able to log in')
        return redirect(url_for('buyerLogin',error='Your'))
    print("hello")
    return render_template('register_buyer.html',form=form)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/farmerLogin",methods=['GET','POST'])
def farmerLogin():
    if current_user.is_authenticated:
        return redirect(url_for('farmerdecision'))
    form =LoginFormFarmer()
    if form.validate_on_submit():
        farmer=Farmer.query.filter_by(email=form.email.data).first()
        if farmer and bcrypt.check_password_hash(farmer.password,form.password.data):
            login_user(farmer)
            # return redirect(url_for('farmerDashboard'))
            next_page=request.args.get('next')
            return redirect(next_page)if next_page else redirect(url_for('farmerdecision'))
        else:
            flash('Login Unsuccessful. Please check email and password')
    return render_template('farmer_login.html', form=form)

@app.route('/farmerdashboard',methods=["GET","POST"])
def farmerDashboard():
     form=CropForm()
     if form.validate_on_submit():
        crop=Crop(crop_name=form.crop_name.data,content=form.crop_info.data,price=form.crop_rate.data,farmer_address=form.address.data)
        db.session.add(crop)
        db.session.commit()
        flash('Crop added successfully!','success')
        return redirect('/successcrop')
     return render_template('farmerdashboard.html',form=form)
 
 
@app.route('/rentdashboard',methods=["GET","POST"])
def rentDashboard():
     form=ItemForm()
     if form.validate_on_submit():
        item=Item(item_name=form.item_name.data,content=form.item_info.data,price=form.item_rate.data,farmer_address=form.address.data)
        db.session.add(item)
        db.session.commit()
        flash('Crop added successfully!','success')
        return redirect('/successitem')
     return render_template('rentdashboard.html',form=form)
    
@app.route('/rentbuyerdashboard',methods=["GET","POST"])
def rentbuyerDashboard():
     items=Item.query.all()
     print(items)
     return render_template('rentbuyerdashboard.html',items=items)
 
 
@app.route("/buyerLogin",methods=['GET','POST'])
def buyerLogin(): 
    if current_user.is_authenticated:
        return redirect('/buyerdashboard')
    form =LoginFormBuyer()
    if form.validate_on_submit():
        buyer=Buyer.query.filter_by(email=form.email.data).first()
        if buyer and bcrypt.check_password_hash(buyer.password,form.password.data):
            login_user(buyer)
            return render_template('buyerdashboard.html')
            # next_page=request.args.get('next')
            # return redirect(next_page)if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password')

    return render_template('buyer_login.html',form=form)

@app.route('/buyerdashboard',methods=["GET","POST"])
def buyerDashboard():
     crops=Crop.query.all()
     print(crops)
     return render_template('buyerdashboard.html',crops=crops)




@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')
   

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))




maps1 = []
maps = [
    {
        'id': 1,
        'location': 'chennai',
        'exact_loc': 'Kandgai',
        'distance': 5
    },
    {
        'id': 2,
        'location': 'delhi',
        'exact_loc': 'Cannaught Place',
        'distance': 10
    },
    {
        'id': 3,
        'location': 'delhi',
        'exact_loc': 'Near Rastrapathi Bhawan',
        'distance': 15
    },
    {
        'id': 4,
        'location': 'deoria',
        'exact_loc': 'New Colony',
        'distance': 12
    },
    {
        'id': 5,
        'location': 'gorakhpur',
        'exact_loc': 'Pipiganj',
        'distance': 13
    },
    {
        'id': 6,
        'location': 'chennai',
        'exact_loc': 'Kelembakkam',
        'distance': 5
    },
    {
        'id': 7,
        'location': 'delhi',
        'exact_loc': 'Chandni Chowk',
        'distance': 10
    },
    {
        'id': 8,
        'location': 'delhi',
        'exact_loc': 'Janpath Market',
        'distance': 15
    },
    {
        'id': 9,
        'location': 'deoria',
        'exact_loc': 'Garul Par',
        'distance':12
   }
]


@app.route("/map", methods=["GET", "POST"])
def map():
    if request.method == "POST":
        location = request.form["location"]
        cur_id = random.randint(1, 1000)
        maps1.clear()
        for item in maps:
            if item['location'] == location.lower():
                maps1.append(item)
        return redirect(url_for('map'))
    return render_template('map.html',items=maps1)