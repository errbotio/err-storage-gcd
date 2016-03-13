# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import datetime
import logging
from typing import Any
import os

from jsonpickle import encode, decode
from errbot.storage.base import StorageBase, StoragePluginBase
from gcloud import datastore

log = logging.getLogger('errbot.storage.gcd')

ACCOUNT_FILE_ENTRY = 'accountfile'
PROJECT_ENTRY = 'project'

class CloudDatastore(StorageBase):
    def __init__(self, namespace, project, credentials):
        log.debug('Try to authenticate Google cloud storage on %s with %s' % (project, credentials))
        self.ds = datastore.Client.from_service_account_json(credentials, project=project, namespace=namespace)
        log.debug('API built %s', self.ds)

    def _gkey(self, key):
        return self.ds.key('Errbot', key)

    def _get_all(self):
        query = self.ds.query(kind='Errbot')
        return list(query.fetch())

    def get(self, key: str) -> Any:
        resp = self.ds.get(self._gkey(key))
        if not resp:
            raise KeyError("%s doesn't exist." % key)
        return decode(resp['value'])

    def remove(self, key: str):
        key = self.ds.key('Errbot', key)
        self.ds.delete(key)

    def set(self, key: str, value: Any) -> None:
        ent = datastore.Entity(key=self._gkey(key))
        ent['value'] = encode(value)
        self.ds.put(ent)

    def len(self):
        return len(self._get_all())  # TODO: optimize

    def keys(self):
        return [ent.key.name for ent in self._get_all()]

    def close(self) -> None:
        pass


class CloudDataStorePlugin(StoragePluginBase):
    def __init__(self, bot_config):
        super().__init__(bot_config)
        if PROJECT_ENTRY not in self._storage_config:
            raise Exception('You need to specify a project in your config.py like this: STORAGE_CONFIG={"project":"albator"}')
        self.credentials = self._storage_config[ACCOUNT_FILE_ENTRY] if ACCOUNT_FILE_ENTRY in self._storage_config else os.path.join(bot_config.BOT_DATA_DIR, 'servacc.json')
        self.prj = self._storage_config[PROJECT_ENTRY]

    def open(self, namespace: str) -> StorageBase:
        return CloudDatastore(namespace, self.prj, self.credentials)
