import logging

from .jsonl_backend import JSONLBackend
from .sqlite_backend import SQLiteBackend


class CacheBackend:
    def __init__(self, backend_name, cache_dir, logger_name):
        self._backend_name = backend_name
        self._cache_dir = cache_dir
        self.logger = logging.getLogger(logger_name)
        if self._backend_name == "jsonl":
            self._cache: JSONLBackend | SQLiteBackend =\
                JSONLBackend(self._cache_dir, self._logger_name)  # type: ignore
        elif self._backend_name == "sqlite":
            self._cache = SQLiteBackend(self._cache_dir, self._logger_name)  # type: ignore
            self._cache._create_dbs()
        else:
            raise ValueError(f"Unkonwn backend {self._backend_name}")

    def load_metadata(self):
        self._metadata, self._known_duplicates, self._inferred_duplicates, self._corpus_map =\
            self._cache.load_metadata()
        self._extid_metadata = {k: {} for k in IdKeys if k.lower() != "ss"}
        if self._metadata:
            for paper_id, extids in self._metadata.items():
                for idtype, ID in extids.items():
                    idtype = id_to_name(idtype)
                    if ID and id_to_name(idtype) in self._extid_metadata:
                        self._extid_metadata[idtype][ID] = paper_id
        for k, v in self._inferred_duplicates.items():
            for _v in v:
                self._inferred_duplicates_map[_v] = k

