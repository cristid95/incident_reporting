"""This module will serve the api request."""

from config import client, ObjectId
from app import app
from bson.json_util import dumps
from flask import request, jsonify, send_file, make_response
import json
import ast
import imp
import time
import codecs


# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client.incidents
# Select the collection
collection = db.reported_incidents

INCIDENT_TO_CODE = {'tornado' : 1,
					'flood' : 2,
					'wildfire' : 3,
					'earthquake' : 4,
					'tsunami' : 5,
					'storm' : 6,
					'drought' : 7,
					'avalanche' : 8,
					'landslide' : 9,
					'sinkhole' : 10,
					'volcanic_eruption' : 11,
					'thunderstorm' : 12}
CODE_TO_INCIDENT = ['', 'tornado', 'flood', 'wildfire', 'earthquake', 'tsunami',
				 'storm', 'drought', 'avalanche', 'landslide', 'sinkhole',
				 'volcanic_eruption', 'thunderstorm']
GET_ALL_SUMMARY = {'latitude' : 1, 'longitude' : 1, 'type' : 1}
IMAGE_FOLDER = '/home/cristi/Desktop/Proiect_BD/images/'
IMAGE_EXTENSION = '.jpeg'

@app.route("/")
def get_initial_response():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the Incidents Reporting Service!'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp


'''
Demo body:
{"type": "tornado","description": "Second incident","latitude": 44.467645,"longitude": 26.140665,"tags": ["wow","incident","again"]}
'''
@app.route("/api/v1/incidents", methods=['POST'])
def add_incident():
    try:
        # Create new incidents
        try:
            incident_str = request.form['data']
            image = request.files['image']
            incident = ast.literal_eval(incident_str)
        except:
            # Bad request as request body is not available
            return "", 400

        #print incident
        # Convert natural disaster name to corresponding code
        incident['code'] = INCIDENT_TO_CODE[incident['type']]

        # Add the image path to the incident information
        incident['image_path'] = ''

        # Add timestamp
        incident['timestamp'] = time.time()

        # Insert incident into mongo and get its ID
        record_id = collection.insert(incident)
        if record_id is None:
            raise IOError("Could not insert document into MongoDB")
        record_id = str(record_id)

        # Save the image to disk
        image_name = record_id + IMAGE_EXTENSION
        res = helper_module.save_filestorage_object(image, IMAGE_FOLDER, image_name)
        if not res:
            # Could not save the incident image. Roll back mongo
            collection.delete_one({"_id" : ObjectId(record_id)})
            raise IOError("Could not save file on disk")

        # Update the image path from Mongo Document
        image_path = IMAGE_FOLDER + image_name
        record = collection.find_one_and_update({"_id" : ObjectId(record_id)},
            {"$set" : {"image_path" : image_path}})

        # Return ID of the newly created item
        return jsonify(record_id), 201

    except:
        # Error while trying to create the resource
        return "", 500


@app.route("/api/v1/incidents", methods=['GET'])
def get_incidents():
    try:
        # Call the function to get the query params
        query_params = helper_module.parse_query_params(request.query_string)
        #print query_params
        # Check if dictionary is not empty
        if query_params:

            # Get all information about specific incident
            query = {"_id" : ObjectId(query_params["_id"])}
            #print query
            incident = collection.find_one(query)

            # Check if the records are found
            if incident:
                # Prepare the response
                #return dumps(incident)
                #image_data = codecs.open(incident['image_path'], 'rb').read()
                #data = {}
                #data['data'] = incident
                #data['image'] = image_data
                #resp = make_response()
                #resp.files = image_data
                #resp.data = incident
                #resp.data = data
                #return resp
                #return send_file(incident['image_path'])#, resp
                response = send_file(incident['image_path'])
                #response.form = incident
                response.headers['incident_data'] = str(incident)
                #print (len(response.data))
                return response
            else:
                # No records are found
                return "", 404

        # If dictionary is empty
        else:
            # Return all the records as query string parameters are not available
            if collection.find().count > 0:
                # Prepare response if the incidents are found
                return dumps(collection.find({}, GET_ALL_SUMMARY))
            else:
                # Return empty array if no incidents are found
                return jsonify([])
    except Exception as e:
        # Error while trying to fetch the resource
        return str(e), 500


@app.route("/api/v1/incidents/<incident_id>", methods=['DELETE'])
def remove_incident(incident_id):
    try:
        # Delete the incident
        delete_inc = collection.delete_one({"_id" : ObjectId(incident_id)})
        image_path = IMAGE_FOLDER + incident_id + IMAGE_EXTENSION
        helper_module.remove_file(image_path)

        if delete_inc.deleted_count > 0 :
            # Prepare the response
            return "", 204
        else:
            # Resource Not found
            return "", 404
    except:
        # Error while trying to delete the resource
        return "", 500


@app.route("/api/v1/users/<user_id>", methods=['POST'])
def update_user(user_id):
    """
       Function to update the user.
       """
    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return "", 400

        # Updating the user
        records_updated = collection.update_one({"id": int(user_id)}, body)

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return "", 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return "", 404
    except:
        # Error while trying to update the resource
        # Add message for debugging purpose
        return "", 500


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
