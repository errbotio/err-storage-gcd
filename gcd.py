# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import logging
from typing import Any, Mapping
import shelve
import os

from errbot.storage.base import StorageBase, StoragePluginBase
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
log = logging.getLogger('errbot.storage.gcd')

ACCOUNT_FILE_ENTRY = 'accountfile'
PROJECT_ENTRY = 'project'

class CloudDatastore(StorageBase):
    def __init__(self, namespace, project, credentials):
        log.debug('Try to authenticate Google cloud storage on %s with %s' % (project, credentials))
        self.ds = build('datastore', 'v1beta2', credentials=credentials)
        log.debug('API built %s', self.ds)
        log.debug('Datasets = %r', self.ds.datasets())
        ts = self.ds.datasets().beginTransaction(datasetId=project, body={'isolationLevel':'NON_TRANSACTIONAL'}).execute()
        log.debug('ts = %r', ts['transaction'])


    def get(self, key: str) -> Any:
        return self.shelf[key]

    def remove(self, key: str):
        if key not in self.shelf:
            raise KeyError("%s doesn't exist." % key)
        del self.shelf[key]

    def set(self, key: str, value: Any) -> None:
        self.shelf[key] = value

    def len(self):
        return len(self.shelf)

    def keys(self):
        return self.shelf.keys()

    def close(self) -> None:
        self.shelf.close()
        self.shelf = None


class CloudDataStorePlugin(StoragePluginBase):
    def __init__(self, bot_config):
        super().__init__(bot_config)
        if PROJECT_ENTRY not in self._storage_config:
            raise Exception('You need to specify a project in your config.py like this: STORAGE_CONFIG={"project":"albator"}')
        acc = self._storage_config[ACCOUNT_FILE_ENTRY] if ACCOUNT_FILE_ENTRY in self._storage_config else  os.path.join(bot_config.BOT_DATA_DIR, 'servacc.json')
        self.prj = self._storage_config[PROJECT_ENTRY]
        self.credentials = GoogleCredentials.from_stream(acc)
        self.credentials._scopes = 'https://www.googleapis.com/auth/cloud-platform'

    def open(self, namespace: str) -> StorageBase:
        config = self._storage_config
        return CloudDatastore(namespace, self.prj, self.credentials)
