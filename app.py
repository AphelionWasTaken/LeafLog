import os
import uuid
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from kivy.utils import platform


# Configuration
if platform == "android":
    BASE_DIR = os.environ.get("PYTHON_SERVICE_ARGUMENT", os.getcwd())
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "journal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this is a super secret key")

db = SQLAlchemy(app)


# Database Models
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    photos = db.Column(db.Text)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    entries = db.relationship("JournalEntry", backref="plant", lazy=True, cascade="all, delete-orphan")


with app.app_context():
    db.create_all()


# Routes
@app.route("/")
def home():
    plants = Plant.query.all()
    
    plant_entries = []
    for plant in plants:
        latest_entry = JournalEntry.query.filter_by(plant_id=plant.id)\
                            .order_by(JournalEntry.entry_date.desc())\
                            .first()
        plant_entries.append({"plant": plant, "entry": latest_entry})

    return render_template("home.html", plant_entries=plant_entries, plants=plants, active_plant=None)


@app.route("/journal")
def journal():
    plants = Plant.query.all()

    if plants:
        active_id = request.args.get("plant", plants[0].id, type=int)
    else:
        active_id = request.args.get("plant", None, type=int)

    active_plant = Plant.query.get(active_id) if active_id else None

    entries = []
    if active_plant:
        entries = JournalEntry.query.filter_by(
            plant_id=active_plant.id
            ).order_by(JournalEntry.entry_date.desc()).all()

    return render_template("index.html", plants=plants, active_plant=active_plant, entries=entries)


@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    plant_id = request.args.get("plant_id", type=int)
    entry = JournalEntry.query.get(entry_id)
    if not entry:
        abort(404)

    if entry.photos:
        for fname in entry.photos.split(","):
            path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
            if os.path.exists(path):
                os.remove(path)

    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("journal", plant=plant_id))


@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    prev_plant_id = request.args.get("plant", type=int)

    if prev_plant_id:
        active_plant = Plant.query.get(prev_plant_id)
    else:
        active_plant = Plant.query.get(entry.plant_id)

    if request.method == "POST":
        entry.entry_date = date.fromisoformat(request.form.get("entry_date"))
        entry.notes = request.form.get("notes")
        photo_files = request.files.getlist("photo")
        new_filenames = []

        if entry.photos:
            filenames = entry.photos.split(",")
        else:
            filenames = []

        for file in photo_files:
            if file and file.filename:
                unique_id = uuid.uuid4().hex[:8]
                safe_name = file.filename.replace(" ", "_")
                filename = f"{entry.entry_date}_{unique_id}_{safe_name}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                filenames.append(filename)
        entry.photos = ",".join(filenames)

        remove_photos = request.form.getlist("remove_photos")
        if remove_photos:
            for f in filenames:
                if f not in remove_photos:
                    new_filenames.append(f)
            filenames = new_filenames
            entry.photos = ",".join(filenames)

        db.session.commit()

        redirect_plant_id = prev_plant_id or entry.plant_id
        return redirect(url_for("journal", plant=redirect_plant_id))

    return render_template("edit.html", entry=entry, active_plant=active_plant)


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    plants = Plant.query.all()
    plant_id = request.args.get("plant_id", type=int)

    if plant_id:
        active_plant = Plant.query.get(plant_id)
    else:
        if plants:
            active_plant = plants[0]
        else:
            active_plant = None
    
    if request.method == "POST":
        entry_date = request.form.get("entry_date")
        notes = request.form.get("notes")
        plant_id = int(request.form.get("plant_id"))
        active_plant = Plant.query.get(plant_id)
        photo_files = request.files.getlist("photo")
        filenames = []

        for file in photo_files:
            if file and file.filename:
                unique_id = uuid.uuid4().hex[:8]
                safe_name = file.filename.replace(" ", "_")
                filename = f"{entry_date}_{unique_id}_{safe_name}"
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                filenames.append(filename)

        entry = JournalEntry(
            entry_date=date.fromisoformat(entry_date),
            notes=notes,
            photos=",".join(filenames),
            plant_id=plant_id
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for("journal", plant=plant_id))

    return render_template("add.html", plants=plants, active_plant=active_plant)


@app.route("/plants/new", methods=["GET", "POST"])
def new_plant():
    plants = Plant.query.all()
    prev_plant_id = request.args.get("plant", type=int)

    if prev_plant_id:
        prev_active_plant = Plant.query.get(prev_plant_id)
    else:
        prev_active_plant = None

    if request.method == "POST":
        name = request.form.get("name")
        if name:
            new_plant_obj = Plant(name=name)
            db.session.add(new_plant_obj)
            db.session.commit()

            if prev_active_plant:
                return redirect(url_for("journal", plant=new_plant_obj.id))
            return redirect(url_for("home"))
    return render_template("new_plant.html", plants=plants, active_plant=prev_active_plant)


@app.route("/plants/delete/<int:plant_id>", methods=["POST"])
def delete_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404)
    db.session.delete(plant)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/plants/edit/<int:plant_id>", methods=["GET", "POST"])
def edit_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if new_name:
            plant.name = new_name
            db.session.commit()

        return redirect(url_for("journal", plant=plant.id))
    return render_template("edit_plant.html", plant=plant)


@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "photo" not in request.files:
        return "No file", 400

    file = request.files["photo"]
    if file.filename == ""''"":
        return "No filename", 400

    filename = f"{uuid.uuid4().hex}_{file.filename.replace(' ', '_')}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return "OK", 200


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
