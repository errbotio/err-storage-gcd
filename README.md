## Google Cloud Datastore storage plugin for errbot


### About
[Errbot](http://errbot.io) is a python chatbot, this storage plugin allows you to use it with
[Google Cloud Datastore](https://cloud.google.com/datastore/docs/concepts/overview) as a persistent storage.

### Installation


1. Configure and get the private key json of a service account for Google Cloud Datastore from the Cloud Console of your project.
2. Save the file in errbot's data directory under the name `servacc.json`.
   (Or another destination but you need to override it in the config below)
3. First you need to clone this repository somewhere, for example:
 ```bash
 mkdir /home/gbin/err-storage
 cd /home/gbin/err-storage
 git clone https://github.com/errbotio/err-storage-gcd
 ```

4. Then you need to add this section to your config.py, following the previous example:
 ```python
 BOT_EXTRA_STORAGE_PLUGINS_DIR='/home/gbin/err-storage'
 STORAGE = 'GoogleCloudDatastore'
 STORAGE_CONFIG = {
    'project': 'foo-bar-123', # Your google cloud project id
    'accountfile': '/tmp/account-12432.json', # path to your credentials in json format for a service account. (defaults to BOT_DATA_DIR/servacc.json)
    'namespace': 'Errbot'  # it will default to Errbot if you don't specify it
    }
 ```
 Start your bot in text mode: `errbot -T` to give it a shot.

 If you want to migrate from the local storage to GCD, you should be able to backup your data (with STORAGE commented)
 then restore it back with STORAGE uncommented.

### Data format

It will create a type of entity per plugin in a namespace called "Errbot" by default.
The only entry per entity will by named `value` and will be a serialized json of the object the plugin tried to store.
