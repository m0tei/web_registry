import json
import tempfile
import uuid
import openpyxl
from apps.home import blueprint
from flask import make_response, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_login import login_required, logout_user, current_user
from jinja2 import TemplateNotFound
from apps.config import db
from datetime import datetime as dt
from apps.home.util import format_date, format_reverse_date
import datetime
import pymongo


@blueprint.route('/index')
@login_required
def index():
    user = db.users.find_one({'_id': session['_user_id']})
    if user['role'] == "user":
         return render_template('home/user.html', segment='user')
    return render_template('home/index.html', segment='index')


@blueprint.route('/user')
@login_required
def user():
    user = db.users.find_one({'_id': session['_user_id']})
    if user['role'] == "admin":
         return render_template('home/index.html', segment='index')
    return render_template('home/user.html', segment='user')

@blueprint.route('/edit/<int:id>')
@login_required
def edit(id):
    user = db.users.find_one({'_id':session['_user_id']})
    if user['role'] == "user":
         return render_template('home/user.html', segment='user')
    
    entry = this_year_db.find_one({"_id": id})
    if entry is None:
        render_template('home/index.html', segment= 'index')

    return render_template('home/edit.html', entry=json.dumps(entry))

@blueprint.route('/users/<id>')
@login_required
def users(id):
    user = db.users.find_one({'_id':session['_user_id']})
    if user['role'] == "user":
         return render_template('home/user.html', segment='user')

    if db.users.find_one({"_id": id}):
        user_data = db.users.find_one({"_id": id})
    else:
        user_data["name"] =  "user deleted!"
        user_data["_id"] = "0"
    return render_template('home/userPage.html', user=user_data)



@blueprint.route('/<template>')
@login_required
def route_template(template):
    if '_user_id' in session:
        user = db.users.find_one({'_id':session['_user_id']})
        if user['role'] == "user":
            return render_template('home/user.html', segment='user')
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


#####################################################################


today_date = datetime.date.today()
current_year = str(today_date.year)
this_year_db = getattr(db, current_year, None)


@blueprint.route('/api/entry/add', methods=['POST'])
@login_required
def add():
    date_string = request.form.get('data')
    yearSelected = dt.strptime(date_string, "%Y-%m-%d")
    year_selected = getattr(db, str(yearSelected.year), None)

    if dt.today().year < yearSelected.year:
        return jsonify({"error": "Entry is in the future!"}), 400

    id_entry = request.form.get('id')
    if not id_entry:
        last_document = year_selected.find_one(sort=[("_id", pymongo.DESCENDING)])
        last_id = last_document['_id'] + 1 if last_document else 1
    else:
        last_id = id_entry

    entry = {
        "_id": int(last_id),
        "user": session["_user_id"],
        "date": str(dt.today().date()),
        "data_inregistrarii": str(request.form.get('data')),
        "nr_si_data_documentului": request.form.get('nr_si_data'),
        "de_unde_provine_documentul": request.form.get('provine_doc'),
        "continutul_documentului": request.form.get('cont_scurt'),
        "repartizare": request.form.get('comp_repartizat'),
        "data_expedierii": str(request.form.get('data_expedierii')),
        "destinatar": request.form.get('destinatar'),
        "nr_de_inregistrare_conex_doc_indic_dos": request.form.get('nr_inregistrare'),
    }

    existing_entry = year_selected.find_one({"_id": int(last_id)})
    if existing_entry and request.form.get('from') == "admin":
        try:
            year_selected.update_one({"_id": int(last_id)}, {"$set": entry})
            return jsonify({"msg": "Entry updated"}), 200
        except Exception as e:
            print("Error updating entry:", e)
            return jsonify({"error": "Failed to update entry"}), 500
    else:
        if not existing_entry:
            try:
                result = year_selected.insert_one(entry)
                if result.inserted_id:
                    return jsonify({"msg":"Entry added!"}), 200
            except Exception as e:
                print("Error inserting entry:", e)
                return jsonify({"error": "Failed to insert entry"}), 500

    return jsonify({"error": "Already exists and you cannot edit it!"}), 400


@blueprint.route('/api/table/show', methods=['GET'])
@login_required
def GetTable():
    # Get the page number from the request query parameters, default to 1 if not provided
    page = int(request.args.get('page', 1))

    # Number of entries per page
    per_page = 10 # You can adjust this as needed

    # Calculate the skip value based on the page number and number of entries per page
    skip = (page - 1) * per_page

    # Get the entries for the requested page using pagination
    entries_cursor = this_year_db.find().sort([("_id", -1)]).skip(skip).limit(per_page)
    entries_list = [entry for entry in entries_cursor]

    # Optionally, you can modify the entries here
    for entry in entries_list:
        entry["user_id"] = entry["user"]
        entry["user_name"] = db.users.find_one({"_id": entry["user"]})["name"]
        entry["data_inregistrarii"] = format_date(entry["data_inregistrarii"])
        entry["data_expedierii"] = format_date(entry["data_expedierii"])

    return jsonify(entries_list), 200

@blueprint.route('/api/table/show/<id>', methods=['GET'])
@login_required
def GetTableUser(id):
    # Get the page number from the request query parameters, default to 1 if not provided
    page = int(request.args.get('page', 1))

    # Number of entries per page
    per_page = 10 # You can adjust this as needed

    # Calculate the skip value based on the page number and number of entries per page
    skip = (page - 1) * per_page

    # Get the entries for the requested page using pagination
    entries_cursor = this_year_db.find({"user": id}).sort([("_id", -1)]).skip(skip).limit(per_page)
    entries_list = [entry for entry in entries_cursor]

    # Optionally, you can modify the entries here
    for entry in entries_list:
        entry["user_id"] = entry["user"]
        entry["user_name"] = db.users.find_one({"_id": entry["user"]})["name"]
        entry["data_inregistrarii"] = format_date(entry["data_inregistrarii"])
        entry["data_expedierii"] = format_date(entry["data_expedierii"])
    
    return jsonify(entries_list), 200


@blueprint.route('/api/table/next', methods=['GET'])
@login_required
def next_element():
    last_document = this_year_db.find_one(sort=[("_id", pymongo.DESCENDING)])

    if (last_document != None):
        response = int(last_document["_id"]) + 1
    else:
        response = 1

    if response:
        return jsonify(response), 200
    else:
        return jsonify({"error": "Error giving last element"}), 400


@blueprint.route('/api/table/del/<id>', methods=['GET'])
@login_required
def DeleteRow(id):
    response = this_year_db.delete_one({'_id': int(id)})

    if response.deleted_count == 1:
        return jsonify({'message': 'Entry deleted successfully'}), 200
    else:
        return jsonify({'error': 'Entry not found'}), 404


@blueprint.route('/api/table/collections', methods=['GET'])
@login_required
def collectionList():
    try:
        collections = db.list_collection_names()
        collections.reverse()
        if "delete_me" in collections:
            collections.remove("delete_me")
        if "users" in collections:
            collections.remove("users")
        return jsonify(collections)
    except Exception as e:
        return jsonify({"error": f"Error fetching collections: {e}"}),


@blueprint.route('/api/table/verif', methods={'GET'})
@login_required
def verifyDownload():
    verifyYear = request.args.get('selectedOption')

    if verifyYear in db.list_collection_names():
        return "table found", 200
    else:
        return jsonify({"error": "Table not found!"}), 404


@blueprint.route('/api/table/download/<year>', methods=['GET'])
@login_required
def download(year):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    specific_year = getattr(db, year, None)
    all_documents = specific_year.find().sort("_id", 1)

    header = ["ID", "Data", "Nr. și data documentului", "De unde provine documentul", "Continut pe scurt",
              "Compartiment repartzat", "Data expedierii", "Destinatar", "Nr. de inregistrare la care se conex. doc. si indic. dos."]

    sheet.append(header)
    prevline = 1
    for line in all_documents:
        while (prevline != line["_id"]):
            empty_line = {}
            sheet.append(empty_line)
            prevline += 1

        if "user" in line:
            del line["user"]
        if "date" in line:
            del line["date"]
        line_formated = list(line.values())
        sheet.append(line_formated)
        prevline = prevline+1

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
        # Save workbook to the temporary file
        workbook.save(temp.name)

        # Get the absolute path of the temporary file
        temp_path = temp.name

    attachmentFilename = f"{today_date}_registru__{year}.xlsx"
    response = make_response(send_file(temp.name, as_attachment=True))
    response.headers['Content-Disposition'] = f'attachment; filename={attachmentFilename}'
    response.status_code = 200
    # Send the file to the client
    return response


@blueprint.route('/api/users/show', methods=['GET'])
@login_required
def getUsers():
    users = list(db.users.find({}, {'password': 0}))
    return users, 200


@blueprint.route('/api/users/switchstatus/<id>', methods=['GET'])
@login_required
def SwitchStatusUser(id):
        if current_user._id == id:
            return jsonify({'message': 'Cannot change current user role!'}), 400

        if db.users.find_one({"_id": id})["active"] == True:
            result = db.users.update_one(
                {'_id': id},
                {'$set': {'active': False}}
            )
        else:
            result = db.users.update_one(
                {'_id': id},
                {'$set': {'active': True}}
            )

        if result.modified_count == 1:
            return jsonify({'message': 'User inactive successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
        


#####################################################################

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
