# ------------------------------------------------------------------------------
# Imports ----------------------------------------------------------------------
# ------------------------------------------------------------------------------


import os
import json
import requests
import io
from datetime import datetime

from flask import Flask, request, jsonify, redirect, url_for, render_template, send_from_directory, send_file
from rest_api import REST_API_PORT
from flask import Response

# ------------------------------------------------------------------------------
# Constants --------------------------------------------------------------------
# ------------------------------------------------------------------------------


UI_PORT = 5000



# ------------------------------------------------------------------------------
# Functions --------------------------------------------------------------------
# ------------------------------------------------------------------------------


ui_app = Flask( __name__ + "_ui" )

@ui_app.route( "/" )
def mission_page():
    """A simple function that retreives the pipeline job request page HTML.

    :returns: The HTML for the pipeline job request page.
    """

    with open( "ui.html", "r" ) as html:
        return html.read()


@ui_app.route( "/submit", methods=["POST"] )
def submit():
    """A function called upon submission of a pipeline job request. This
       function parses the user request form, retrieving the user request data.
       This data is then organized into a dictionary to be sent in a REST
       POST request to the REST API.

       In the case of a job request containing invalid parameters, the user will
       be sent to an error page, asking them to redo their request.

       :returns: The HTML for a thank you page.
    """

    mission = ""
    output = ""
    program_list = []
    included_program_list = []
    image_list = []
    source_list = []
    form = request.form


    for key in form.keys():
        if( key == "mission" ):
            mission = form[key]
            continue
        elif( key == "output" ):
            output = form[key]
            continue
        elif( key == "sources" ):
            source_list = form[key]
            source_list = source_list.split(',')
            continue


        program = key.split("!")

        # The submit button is sometimes included in the data, which breaks
        # things. This gets rid of it.
        if( len(program) != 2 ):
            continue

        name = program[0]
        attribute = program[1]

        if( "img" in name ):
            if( form[key] == "on" ):
                image_name = name.split("~")[1]
                # TODO: This will be the archival image format
                image_list.append( image_name )

            continue

        if( attribute == "check" and form[key] == "on" ):
            program_list.append([name, []])
            included_program_list.append( name )
        elif( name in included_program_list ):
            program_list[-1][1].append( [attribute, form[key]] )

    if( output == "default" ):
        filename = datetime.now().strftime( "%Y_%m_%d_%H_%M_%S" )
    else:
        filename = output + "_" + datetime.now().strftime( "%Y_%m_%d_%H_%M_%S" )

    recipe = {"mission":mission, "tasks":program_list, "output": output, "images": image_list, "sources": source_list, "filename": filename }
    recipe_string = json.dumps( recipe )
    recipe_json = json.loads( recipe_string )
    
    response = requests.post( "http://localhost:" + str(REST_API_PORT) + "/submit", headers={"content-type": "application/json"}, json=recipe_json )
    print( response.text )
    response_json = json.loads( response.text )
    if( response_json["Response"] == "parameter error" ):
        return render_template( "error.html", text=filename )

    return render_template("thank_you.html", text=(filename + '.zip') )

@ui_app.route( "/handle_data", methods=["POST"] )
def handle_data():
    print( request.form )
    print( request.form["test"] )
    return "test"


# Sends a simple test
@ui_app.route( "/test" )
def test():

    #os.system( "curl http://localhost:" + str(REST_API_PORT) + "/test -X POST -d \"data=\"" )
    requests.post( "http://localhost:" + str(REST_API_PORT) + "/test", headers={"content-type": "application/json"}, json={} )

    return "test"


# Sends a more complex test, which passes in pre-generated recipe data
# TODO: Make curling nicer
@ui_app.route( "/dagtest" )
def dag_test():
    """A function to test the ability of the UI to send a request to the REST
    API, using a pregenerated request.

    :returns: A simple message to indicate a successful test.
    """

    with open( "REST_json.json", "r" ) as recipe_file:
        recipe_json = json.load( recipe_file )
        #os.system( "curl http://localhost:" + str(REST_API_PORT) + "/dagtest -X POST -d \"data=" + json.dumps(data).replace(" ", "").replace( "\"", "\\\"") + "\"" )
        requests.post( "http://localhost:" + str(REST_API_PORT) + "/dagtest", headers={"content-type": "application/json"}, json=recipe_json )

    return "dag test"

@ui_app.route('/download/<path:filename>', methods=['GET','POST'])
def download(filename):
    exists = os.path.isfile('./dags/' + filename)
    if exists:
        path = os.path.realpath('./dags/')
        return send_from_directory(path, filename, as_attachment=True, mimetype='application/zip')


# ------------------------------------------------------------------------------
# Main -------------------------------------------------------------------------
# ------------------------------------------------------------------------------


if( __name__ == "__main__" ):
    ui_app.run( port=UI_PORT, debug=False )
