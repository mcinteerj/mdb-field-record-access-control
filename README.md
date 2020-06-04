# MongoDB Field/Record Level Access Control
The content provided in this repo shows a simple demo of an approach to implementing field and/or record level access control in an application on top MongoDB - using permissions stored in a MongoDB collection.

The recommended way to deliver on field or record level access requirements is through the use of [Read Only Views](https://docs.mongodb.com/manual/core/views/) as described in [this blog post](https://www.mongodb.com/blog/post/providing-least-privileged-data-access-in-mongodb). However, there are situations where you may have more specific access control requirements that mean views are not an appropriate option - particularly if there are many different possible views which can change arbirtrarily on a regular basis. In such cases, it may be necessary to implement such controls in the application layer as described in this repository. 

The data in this repository is generated dummy data, and the code is provided as a functional/conceptual approach to delivering field and/or record level access control - rather than being a production-ready implementation fo such control. It is provided for demo/example purposes only. 

## Use Case
The example is based on a system which contains a series of events. Each event is a document stored in an 'events' collection within a MongoDB database. Each event contains some basic event information, as well as some PII data stored in a personalInformation sub-object.

Part of the basic event information includes an 'office' field which records and office the event is associated with. 

From an access control perspective, we are implementing a solution to the following requirements:

* Users must only see data relating to the office with which they are associated (as defined in the user_perms collection)
* Junior users must not see any PII data (in the Personal Information sub-object of each event in the events collection)

The application (based on a provided query and user), should be able to automatically generate the appropriate query to ensure that a user is only returned data which they are authorised to see. 

## Set-up
### MongoDB Atlas Cluster Creation
This demo was built using a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) Cluster running MongoDB 4.2. It will work against any MongoDB 4.2 cluster, however if you don't have one available, you can create one for free on Atlas following the [Get Started with Atlas instructions](https://docs.atlas.mongodb.com/getting-started/).

> **Note:** Make sure you follow the step to [whitelist your connection IP address](https://docs.atlas.mongodb.com/tutorial/whitelist-connection-ip-address/) for the IP address you intend to run this test/demo from. 

### Import data to your Atlas Cluster
In this step, we will load data in the [events.json](./events.json) into the events collection, and the data in [user_perms.json](./user_perms.json) into the `access_control` database of your MongoDB Atlas Cluster.

If you have cURL installed, the easiest way to do this is to run the following two commands:

```bash
curl https://raw.githubusercontent.com/mcinteerj/mdb-field-record-access-control/master/events.json | mongoimport --host <CLUSTER-URI> --ssl --username <USERNAME> --password <PASSWORD> --authenticationDatabase admin --db access_control --collection events

curl https://raw.githubusercontent.com/mcinteerj/mdb-field-record-access-control/master/user_perms.json | mongoimport --host <CLUSTER-URI> --ssl --username <USERNAME> --password <PASSWORD> --authenticationDatabase admin --db access_control --collection user_perms
```

>Note: you will need to update the relevant parameters in the `mongoimport` command. You will be able to find sample `mongoimport` commands for your cluster by navigating to the 'Command Line Tools' page for your cluster by clicking on the "`...`" button for the given cluster on your main cluster dashboard or by following [these instructions](https://docs.atlas.mongodb.com/import/mongoimport/).

The commands will automatically download the content in the provided sample data files from this GitRepo and pipe this into the `mongoimport` command. If you would prefer to do this as separate steps, you can download the respective files ([events.json](./events.json) and [user_perms.json](./user_perms.json))and load them using the `--file` parameter for mongoimport. 

#### user_perms.json
This file was manually created and contains a series of user permission records of the following structure:

```json
{
  "userid": "junior_manchester_user",
  "filter": {
    "office": "Manchester"
  },
  "projection": {
    "personalInformation": 0
  }
}
```

#### events.json
This file was created using [mgeneratejs](https://github.com/rueckstiess/mgeneratejs) along with the template provided in this repository - [basic_event_template.json](./basic_event_template.json). 

All of the events in the provided file are for the month of May 2020, and all other data has been randomly generated. You can adjust the shape of the data and/or re-generate your own data as you wish. 

Each event record has the following structure:

```json
{
    "office": "Liverpool",
    "eventDateTime": {
        "$date": "2020-05-05T15:02:20.257Z"
    },
    "personalInformation": {
        "fullName": "Maude Lopez",
        "dob": {
            "$date": "1986-01-17T11:48:15.262Z"
        },
        "documentNumber": "LN289560",
        "birthPlace": "Sizcadot",
        "gender": "male",
        "nationality": "Yemen",
        "residenceCountry": "Israel"
    }
}
```

## Running the Demo

These instructions assume you have `python3` installed, and the `pymongo`, `dnspython`, `bson` modules installed. 

Download the [./run_demo.py](./run_demo.py) script to the machine you will run your test from (and have whitelisted the IP address for). 

Update the `URI_STRING` value in the `./run_demo.py` script with the URI for your MongoDB Atlas cluster. 

Run the script using the following command:
```bash
python3 ./run_demo.py <user>
```

You will need to replace `<user>` with one of the users defined in the `user_perms` collection. The script will return three documents based on the query toward the end of the `run_demo.py` script:

```python3
{"eventDateTime": {"$gt": datetime(2020, 5, 10), "$lt": datetime(2020, 5, 11)}}
```

It will also automatically apply the restrictions based on the user provided (based on what is defined in the `user_perms` collection).

With the data sets provided in this repository, you should have four users defined, each with different permissions:

> `london_user` will only see events where `office == London`

> `manchester_user` will only see events where `office == Manchester`

> `junior_london_user` will only see events where `office == London`, all personalInformation will be removed (field level acess control)

> `junior_london_user` will only see events where `office == London`, all personalInformation will be removed (field level acess control)

None of the users provided will see events relating to the Liverpool office - adding a user with the ability to see Liverpool data may be a good extension to get familiar with the concepts implemented in this repository.