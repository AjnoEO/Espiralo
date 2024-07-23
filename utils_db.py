from __future__ import annotations
import json
from typing import Any, Iterable, SupportsIndex, overload
import os

DATABASE_FILE = "db.json"

def _DBize(obj: dict | list | Any, parent: Database | __DBdict | __DBlist | __NoneParent) -> __DBdict | __DBlist | Any:
    if isinstance(obj, dict):
        obj = __DBdict(obj, parent)
    if isinstance(obj, list):
        obj = __DBlist(obj, parent)
    return obj

class __DBlist(list):
    """Listo el datumbazo"""
    def __init__(self, iterable: Iterable, parent: Database | __DBdict | __DBlist | __NoneParent):
        super().__init__(iterable)
        for index, item in enumerate(self):
            self.__setitem__(index, item, update = False)
        self.parent = parent

    def _update(self):
        self.parent._update()

    def __setitem__(self, key: SupportsIndex, value: Any, update: bool = True) -> None:
        value = _DBize(value, self)
        super().__setitem__(key, value)
        if update:
            self._update()

    def __delitem__(self, key: SupportsIndex | slice):
        super().__delitem__(key)
        self._update()

    def append(self, object: Any) -> None:
        object = _DBize(object, self)
        super().append(object)
        self._update()

    def clear(self) -> None:
        super().clear()
        self._update()

    def extend(self, iterable: Iterable) -> None:
        super().extend(iterable)
        self._update()

    def insert(self, index: SupportsIndex, object: Any) -> None:
        object = _DBize(object, self)
        super().insert(index, object)
        self._update()

    def pop(self, index: SupportsIndex = -1) -> Any:
        result = super().pop(index)
        self._update()
        return result
    
    def remove(self, value: Any) -> None:
        value = _DBize(value, self)
        super().remove(value)
        self._update()

    def reverse(self) -> None:
        super().reverse()
        self._update()

    def __repr__(self) -> str:
        return super().__repr__() #+ f" (Parent: {self.parent})"

class __DBdict(dict):
    """Vortaro el datumbazo"""
    def __init__(self, map, parent: Database | __DBdict | __DBlist | __NoneParent):
        super().__init__(map)
        for k, v in self.items():
            self.__setitem__(k, v, update = False)
        self.parent = parent
    
    def _update(self):
        self.parent._update()

    def __setitem__(self, key: Any, value: Any, update: bool = True) -> None:
        value = _DBize(value, self)
        super().__setitem__(key, value)
        if update:
            self._update()

    def __delitem__(self, key: Any) -> None:
        super().__delitem__(key)
        self._update()

    def clear(self) -> None:
        super().clear()
        self._update()

    @overload
    def pop(self, key: Any, /) -> Any: ...
    @overload
    def pop(self, key: Any, default: Any, /) -> Any: ...    
    def pop(self, *items):
        result = super().pop(*items)
        self._update()
        return result

    def popitem(self) -> tuple:
        result = super().popitem()
        self._update()
        return result

    def setdefault(self, key: Any, default: Any | None = None) -> Any | None:
        default = _DBize(default, self)
        result = super().setdefault(key, default)
        self._update()
        return result

    def __repr__(self) -> str:
        return super().__repr__() #+ f" (Parent: {self.parent})"

class __NoneParent():
    def __init__(self): ...
    def _update(self): ...

class Database(__DBdict):
    """Ebligas laboron pri la datumbazo, tenata en DATABASE_FILE ĉe certa ŝlosilo"""
    def __init__(self, key: str):
        """La datumbazo, tenata en DATABASE_FILE ĉe la ŝlosilo `key`

        `key`
            La ŝlosilo, per kiu troveblas la datumbazo
        """
        self.db_key = key
        if not os.path.exists("db.json"):
            with open(DATABASE_FILE, "w", encoding="utf8") as file:
                json.dump({}, file, indent=4)
        with open(DATABASE_FILE, "r", encoding="utf8") as file:
            contents = file.read().strip()
        if not contents:
            json_contents = {}
        else:
            json_contents: dict[str, dict] = json.loads(contents)
        if key not in json_contents:
            json_contents[key] = {}
            with open(DATABASE_FILE, "w", encoding="utf8") as file:
                json.dump(json_contents, file, indent=4, ensure_ascii=False)
        if not isinstance(json_contents[key], dict):
            raise TypeError(f"Ĉe la ŝlosilo «{key}» en {DATABASE_FILE} teniĝas ne objekto (dict)")
        super().__init__(json_contents[key], self)

    def _update(self):
        with open(DATABASE_FILE, "r", encoding="utf8") as file:
            old_json_contents: dict[str, dict] = json.load(file)
        new_json_contents = old_json_contents
        new_json_contents[self.db_key] = dict(self)
        with open(DATABASE_FILE, "w", encoding="utf8") as file:
            try:
                json.dump(new_json_contents, file, indent=4, ensure_ascii=False)
            except Exception as err:
                json.dump(old_json_contents, file, indent=4, ensure_ascii=False)
                print(f"Eraro dum aktualigado de la datumbaza dosiero! {err=}, {type(err)=}\n{new_json_contents=}")
                raise err

    def __repr__(self) -> str:
        return super().__repr__() + f" ({DATABASE_FILE} > ['{self.db_key}'])"

if __name__ == "__main__":
    db = Database("Testo")
    print(db)