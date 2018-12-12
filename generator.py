# ------------------------------------------------------------------------------
# Imports ----------------------------------------------------------------------
# ------------------------------------------------------------------------------


import json

from datetime import datetime

# May be unnecessary
#import sys



# ------------------------------------------------------------------------------
# Constants --------------------------------------------------------------------
# ------------------------------------------------------------------------------


DEBUG = False
TEST = True
TEST_FILE = "REST_json.json"
DAG_DIRECTORY = "/root/airflow/dags/"



# ------------------------------------------------------------------------------
# Classes ----------------------------------------------------------------------
# ------------------------------------------------------------------------------


class CommandObject:

    def __init__( self, command, parameters, image ):
        self.command = command
        self.parameters = parameters
        self.image = image

    def __str__( self ):
        output = self.command

        for parameter in self.parameters:
            output += " " + parameter[0] + "=" + parameter[1]

        output += " " + self.image

        return output


class DAGObject:

    # Command is a CommandObject
    def __init__( self, command ):
        self.command = command

    def __str__( self ):
        output = '''%s = BashOperator(
    task_id="%s",
    bash_command="echo %s",
    retries=3,
    dag=dag
)'''
        command_id = self.command.command + self.command.image.replace(".jpg", "")
        output = output % (command_id, command_id, str(self.command))

        return output

    def get_command( self ):
        return self.command.command + self.command.image.replace(".jpg", "")



# ------------------------------------------------------------------------------
# Functions --------------------------------------------------------------------
# ------------------------------------------------------------------------------


# Generates the string for a DAG file from given list of DAG objects
# TODO: Generate full dag for all included images
# TODO: Move dag string
# TODO: Move start object to object generation
# TODO: Format dag, e.g. put spaces between parentheses
# TODO: Place name of dag in dag
def generate_dag( mission, dag_objects ):

    dag_string = '''from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.today(),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta( minutes=5 ),
}

dag = DAG( "%s", default_args=default_args, schedule_interval="@once" )

start = BashOperator(
    task_id="start",
    bash_command="echo Starting...",
    retries=3,
    dag=dag
)''' % mission

    for dag_object in dag_objects:
        dag_string += "\n\n" + str( dag_object )

    dag_string += "\n"
    dag_string += "\nstart.set_downstream(" + dag_objects[0].get_command() + ")"

    for index in range( len( dag_objects ) - 1 ):
        dag_string += "\n" + dag_objects[index].get_command() + ".set_downstream(" + dag_objects[index + 1].get_command() + ")"

    return dag_string


# DEPRECATED
# Gets a list of DAG objects from a json file containing UI output, using filename
def get_commands_from_filename( recipe_filename ):

    with open( recipe_filename, "r", ) as file:
        recipe = json.load( file )

        mission = recipe["mission"]
        output = recipe["output"]
        tasks = recipe["tasks"]

        commands = []
        dag_objects = []

        for task in tasks:
            commands.append( CommandObject( task[0], task[1] ) )

        for command in commands:
            dag_objects.append( DAGObject( command ) )

        return dag_objects


# DEPRECATED
# Gets a list of DAG objects from a json file containing UI output, using file
def get_commands_from_file( recipe_file ):

    recipe = json.load( recipe_file )

    mission = recipe["mission"]
    output = recipe["output"]
    tasks = recipe["tasks"]

    commands = []
    dag_objects = []

    for task in tasks:
        commands.append( CommandObject( task[0], task[1] ) )

    for command in commands:
        dag_objects.append( DAGObject( command ) )

    return dag_objects


# Gets a list of DAG objects from a json file containing UI output, using json object
def get_commands_from_json( recipe ):

    mission = recipe["mission"]
    output = recipe["output"]
    tasks = recipe["tasks"]
    images = recipe["images"]

    commands = []
    dag_objects = []

    for image in images:
        for task in tasks:
            commands.append( CommandObject( task[0], task[1], image ) )

    for command in commands:
        dag_objects.append( DAGObject( command ) )

    return dag_objects


# Generates a pipeline job
# TODO: Improve identification of job
# TODO: Change data to recipe
# Parameter is JSON recipe
def generate( data ):

    # print( data )

    mission = data["mission"]

    dag_objects = get_commands_from_json( data )
    dag_string = generate_dag( mission, dag_objects )
    timestamp = datetime.now().strftime( "%Y_%m_%d_%H_%M_%S" )
    with open( DAG_DIRECTORY + timestamp + ".py", "w" ) as job_file:
        job_file.write( dag_string )


# Tests generator library import
def test():

    return "Test successful response."



# ------------------------------------------------------------------------------
# Main -------------------------------------------------------------------------
# ------------------------------------------------------------------------------


if( __name__ == "__main__" and TEST ):
    commands = get_commands_from_filename( TEST_FILE )
    dag = generate_dag( commands )
    print( dag )
