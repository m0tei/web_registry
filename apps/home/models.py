from flask import Flask, jsonify, request, session, redirect, send_file, render_template, make_response
from passlib.hash import pbkdf2_sha256
from . import db
import pymongo
import uuid
from datetime import datetime as dt
import datetime
import openpyxl
import tempfile

today_date = datetime.date.today()
current_year = str(today_date.year)
this_year_db = getattr(db, current_year, None)

class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    session['role']=user['role']
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password'),
      "role": request.form.get('admin')
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    if(user["role"]=="on"):
      user["role"]="admin"
    else:
      user["role"]="user"

    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.users.insert_one(user):
      return jsonify({ "error": "Account added" }), 200

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "email": request.form.get('email')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)

    
    
    return jsonify({ "error": "Invalid login credentials" }), 401
  
  def getUsers(self):
    users = list(db.users.find())
    return users,200

class Table:
  def showTable(self):
    last_entries_cursor = this_year_db.find().sort([("_id", pymongo.DESCENDING)])
    last_entries_list = list(last_entries_cursor)

    return jsonify(last_entries_list), 200;

  def collectionList(self):
    try:
      collections = db.list_collection_names()
      if 'users' in collections:
        collections.remove('users')
      if "delete_me" in collections:
        collections.remove("delete_me")
      return jsonify(collections)
    except Exception as e:
        return jsonify({"error": f"Error fetching collections: {e}"}),
  
  def verifyDownload(self):
    verifyYear = request.args.get('selectedOption')
  
    if  verifyYear in db.list_collection_names():
      print("exist")
      return "table found", 200
    else:
      return jsonify({ "error": "Table not found!" }), 404

  def download(self,year):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    specific_year = getattr(db, year, None)
    all_documents = specific_year.find()
    
    header = ["ID","Data", "Nr. și data documentului", "De unde provine documentul", "Continut pe scurt", "Compartiment repartzat", "Data expedierii", "Destinatar", "Nr. de inregistrare la care se conex. doc. si indic. dos."]

    sheet.append(header)
    prevline=0
    for line in all_documents:
      while(prevline+1!=line["_id"]):
        empty_line={}
        sheet.append(empty_line)
        prevline+=1
    
      del line["user"]
      del line["date"]
      line_formated = list(line.values())
      sheet.append(line_formated)
      prevline=line["_id"]


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

  def last_element(self):
    last_document = this_year_db.find_one(sort=[("_id", pymongo.DESCENDING)])

    if(last_document!=None):
      response = str(last_document['_id']) + '/' + last_document['data_inregistrarii']
    else:
      response = 0

    if response:
      return jsonify(response),200
    else:
      return jsonify({ "error": "Error giving last element" }), 400

class Entry:
  def add(self):
      date_string = request.form.get('data')
      yearSelected = dt.strptime(date_string, "%Y-%m-%d")
      year_selected = getattr(db, str(yearSelected.year), None)

      if(today_date.year < yearSelected.year):
        return jsonify({ "error": "Entry is in the future!" }), 400
      
      id_entry=request.form.get('id')
      if(id_entry==''):
        last_document = year_selected.find_one(sort=[("_id", pymongo.DESCENDING)])
        if(last_document):
          last_id = last_document['_id']
        else:
          last_id = 0
        last_id = last_id+1;
        print(last_id)
      else:
          last_id=int(id_entry);
      
      if(year_selected.find_one({"id":last_id})):
        self.update_entry()
        return

      entry = {
        "_id": last_id,
        "user": "",##session['user'],
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

      if(year_selected.insert_one(entry)):
        return jsonify({ "error": "Entry added" }), 200
      
      return jsonify({ "error": "Entry allready exists!" }), 400

  def delete(seld, id):
    response = this_year_db.delete_one({'_id': int(id)})
    
    if response.deleted_count == 1:
      return jsonify({'message': 'Entry deleted successfully'}), 200
    else:
      return jsonify({'error': 'Entry not found'}), 404