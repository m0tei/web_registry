import tempfile
import uuid
import openpyxl
from apps.home import blueprint
from flask import make_response, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_login import login_required, logout_user, current_user
from jinja2 import TemplateNotFound
from apps.config import db
from datetime import datetime as dt
import datetime
import pymongo

@blueprint.route('/index')
@login_required
def index():
    user = db.users.find_one({'_id':session['_user_id']})
    if user['role'] == "user":
         return render_template('home/user.html', segment='user')
    return render_template('home/index.html', segment='index')

@blueprint.route('/user')
@login_required
def user():
    return render_template('home/user.html', segment='user')


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

    if (today_date.year < yearSelected.year):
        return jsonify({"error": "Entry is in the future!"}), 400

    id_entry = request.form.get('id')
    if (id_entry == ''):
        last_document = year_selected.find_one(
            sort=[("_id", pymongo.DESCENDING)])
        if (last_document):
            last_id = last_document['_id']
        else:
            last_id = 0
        last_id = last_id+1
    else:
        last_id = int(id_entry)

    # if(year_selected.find_one({"id":last_id})):
    #  update_entry()
    #  return

    entry = {
        "_id": last_id,
        "user": session["_user_id"],
        "date": str(datetime.date.today()),
        "data_inregistrarii": str(request.form.get('data')),
        "nr_si_data_documentului": request.form.get('nr_si_data'),
        "de_unde_provine_documentul": request.form.get('provine_doc'),
        "continutul_documentului": request.form.get('cont_scurt'),
        "repartizare": request.form.get('comp_repartizat'),
        "data_expedierii": str(request.form.get('data_expedierii')),
        "destinatar": request.form.get('destinatar'),
        "nr_de_inregistrare_conex_doc_indic_dos": request.form.get('nr_inregistrare'),
    }

    if (year_selected.insert_one(entry)):
        return jsonify({"msg": "Entry added"}), 200

    return jsonify({"error": "Entry allready exists!"}), 400


@blueprint.route('/api/table/show', methods=['GET'])
@login_required
def GetTable():
    last_entries_cursor = this_year_db.find().sort(
        [("_id", pymongo.DESCENDING)])
    last_entries_list = list(last_entries_cursor)

    return jsonify(last_entries_list), 200


@blueprint.route('/api/table/last', methods=['GET'])
@login_required
def last_element():
    last_document = this_year_db.find_one(sort=[("_id", pymongo.DESCENDING)])

    if (last_document != None):
        response = str(last_document['_id']) + \
            '/' + last_document['data_inregistrarii']
    else:
        response = 0

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
        if 'users' in collections:
            collections.remove('users')
        if "delete_me" in collections:
            collections.remove("delete_me")
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
    all_documents = specific_year.find()

    header = ["ID", "Data", "Nr. și data documentului", "De unde provine documentul", "Continut pe scurt",
              "Compartiment repartzat", "Data expedierii", "Destinatar", "Nr. de inregistrare la care se conex. doc. si indic. dos."]

    sheet.append(header)
    prevline = 0
    for line in all_documents:
        while (prevline+1 != line["_id"]):
            empty_line = {}
            sheet.append(empty_line)
            prevline += 1

        del line["user"]
        del line["date"]
        line_formated = list(line.values())
        sheet.append(line_formated)
        prevline = line["_id"]

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
        # Save workbook to the temporary file
        workbook.save(temp.name)

        # Get the absolute path of the temporary file
        temp_path = temp.name

    attachmentFilename = f"registru_{today_date}_{year}.xlsx"
    response = make_response(send_file(temp.name, as_attachment=True))
    response.headers['Content-Disposition'] = f'attachment; filename={attachmentFilename}'

    # Send the file to the client
    return response, 200


@blueprint.route('/api/users/show', methods=['GET'])
@login_required
def getUsers():
    users = list(db.users.find({}, {'password': 0}))
    return users, 200


@blueprint.route('/api/users/delete/<id>', methods=['GET'])
@login_required
def delUser(id):
    response = db.users.delete_one({'_id': id})

    if response.deleted_count == 1:
        return jsonify({'message': 'Entry deleted successfully'}), 200
    else:
        return jsonify({'error': 'Entry not found'}), 404


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