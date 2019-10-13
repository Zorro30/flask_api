from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
# api = Api(app)
basedir = os.path.abspath(os.path.dirname(__file__))
#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'machine_db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#init
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Cluster Class/Model
class Cluster(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    region = db.Column(db.String(100))

    def __init__(self,name,region):
        self.name = name
        self.region = region

#Machine Class/Model
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    ip = db.Column(db.String(25))
    instance = db.Column(db.String(50))
    tags = db.Column(db.String(100))
    cluster_id = db.Column(db.Integer)

    def __init__(self,name,ip,instance,tags,cluster_id):
        self.name = name
        self.ip = ip
        self.instance = instance
        self.tags = tags
        self.cluster_id = cluster_id

class ClusterSchema(ma.Schema):
    class Meta:
        fields = ('id','name','region')

cluster_schema = ClusterSchema()
clusters_schema = ClusterSchema(many=True)

class MachineSchema(ma.Schema):
    class Meta:
        fields = ('id','name','ip','instance','tags','cluster_id')

machine_schema = MachineSchema()
machines_schema = MachineSchema(many=True)


#Get all clusters or Create a Cluster.
@app.route('/',methods=['GET','POST'])
def get_or_create_cluster():

    if request.method == "GET":
        all_clusters = Cluster.query.all()
        result = clusters_schema.dump(all_clusters)
        return jsonify(result)
    else:
        name = request.json["name"]
        region = request.json["region"]

        try:
            new_cluster = Cluster(name,region)
            db.session.add(new_cluster)
            db.session.commit()
            return cluster_schema.jsonify(new_cluster)
        except:
            return "Cluster name already in use!"

# Create a machine if a cluster is present
@app.route('/<id>',methods=['POST'])
def create_machine(id):

    machine_name = request.json['name']
    machine_ip = request.json['ip']
    machine_instance = request.json['instance']
    tags = request.json['tags'] or ''
    cluster_id = int(id)

    cluster_present = Cluster.query.get(id)
    if cluster_present:

        new_machine = Machine(machine_name,machine_ip,machine_instance,tags,cluster_id)
        db.session.add(new_machine)
        db.session.commit()

        return machine_schema.jsonify(new_machine)
    else:
        return "<h1>Please register a cluster!</h1>"
    
#Get list of all machines present in all clusters.
@app.route('/machines_list',methods=['GET'])
def get_machines():

    all_machines = Machine.query.all()
    result = machines_schema.dump(all_machines)
    return jsonify(result)


#Delete a Cluster depending on the Cluster ID.
@app.route('/delete_cluster/<id>',methods=['DELETE'])
def delete_cluster(id):

    try:
        to_delete = Cluster.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()

        to_delete = Machine.query.filter(Machine.cluster_id==id).all()
        for machine in to_delete:

            db.session.delete(machine)
            db.session.commit()

        return cluster_schema.jsonify(f"Cluster with {id} deleted!")
    except:
        return ("No Such Cluster to delete")

#Delete a cluster depending on the Machine ID
@app.route('/delete_machine/<id>',methods=['DELETE'])
def delete_machine(id):

    to_delete = Machine.query.get(id)

    db.session.delete(to_delete)
    db.session.commit()

    return machine_schema.jsonify(to_delete)

#Trigger a set of Machines according to the associated tags.
@app.route('/<trigger>/<tag>',methods=['POST'])
def trigger_function(trigger,tag):

    if trigger == "start":
        machines = Machine.query.filter(Machine.tags==tag).all()
        for machine in machines:
            pass
            # start(machine) #Start Function that can be passed the machine ID to start it.
        return (f"Machines with tag {tag} are started!")
        
    elif trigger == "stop":
        machines = Machine.query.filter(Machine.tags==tag).all()
        for machine in machines:
            pass
            # stop(machine) #Stop Function that can be passed the machine ID to stop it.
        return (f"Machines with tag {tag} are Stopped!")

    elif trigger == "reboot":
        machines = Machine.query.filter(Machine.tags==tag).all()
        for machine in machines:
            pass
            # reboot(machine) #Reboot Function that can be passed the machine ID to reboot it.
        return (f"Machines with tag {tag} are Rebooted!")


if __name__ == '__main__':
    app.run(debug=True)