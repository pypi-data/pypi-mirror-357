import pathlib
import json
import typing

from .loader import loader
from .phrasebook import phrasebook

class languages:
    """ It manage languages in the project.
    
    It represents languages library, store location of languages directory,
    and also names of laguages in the POSIX locale format, with paths to it 
    in the directory. 

    POSIX locale format mean that first two letters comes from ISO 639-1. and 
    second two letters come from ISO 3166-1. For example: "en_US", "pl_PL".
    
    Methods
    -------
    add(name: str, file: pathlib.Path) -> languages
        This add new languages file to library.
    load(index: pathlib.Path) -> languages
        This load languages library from index file.
    select(name: str) -> phrasebook
        This load phrasebook for given locales.
    
    Properties
    ----------
    avairable : typing.Iterable[str]
        List of avairable languages names.
    default : str
        Default language name.
    """

    def __init__(self, path: pathlib.Path) -> None:
        """ This create new languages library from path to languages library. 
        
        Parameters
        ----------
        path : pathlib.Path
            Path to the languages directory.

        Raises
        ------
        RuntimeError
            When path is not directory or not exists.
        """

        if not path.is_dir():
            raise RuntimeError("Path \"" + str(path) + "\" is not directory.")

        if not path.exists():
            raise RuntimeError("Directory \"" + str(path) + "\" not exists.")

        self.__languages = dict()
        self.__path = path        

    def add(self, name: str, file: pathlib.Path) -> object:
        """ This add new language to languages library.

        Parameters
        ----------
        name : str
            Name of the language in standard POSIX format, like "en_US", 
            or "pl_PL".
        file : pathlib.Path
            Path to the file in the languages. It must be relative path. 
        
        Raises
        ------
        RuntimeError
            When location of the language is not relavice.
        Exception
            When language already exists.
        TypeError
            When name of the language is not in property POSIX format.

        Returns
        -------
        languages
            Self to chain loading.
        """

        if name in self.__languages:
            raise Exception("Language \"" + name + "\" already exists.")

        if not self.__valid_locale(name):
            raise TypeError("Name \"" + name + "\" is not property locale.")

        if file.is_absolute():
            raise RuntimeError(
                "Location of the \"" + \
                name + \
                "\" must be relative."
            )

        self.__languages[name] = file
        return self

    @property
    def avairable(self) -> typing.Iterable[str]:
        """ It returns avairable languages.

        Returns
        -------
        typing.Iterable[str]    
            Languages which currently exists in the library.
        """

        return self.__languages.keys()

    @property
    def default(self) -> str:
        """ This return default language name.

        Returns
        -------
        str
            Default language name.
        """

        if len(self.avairable) == 0:
            raise RuntimeError("Load any language first.")
            
        for count in self.avairable:
            return count

    def __valid_locale(self, name: str) -> bool:
        """ Check that language name is in property POSIX format.

        Parameters
        ----------
        name : str
            Name of the languages to check.

        Returns
        -------
        bool
            True when name is property formater, False when not.
        """

        splited = name.split("_")

        if len(splited) != 2:
            return False

        first = splited[0]
        second = splited[1]

        if len(first) != 2 or len(second) != 2:
            return False

        if first != first.lower():
            return False

        if second != second.upper():
            return False

        return True

    def load(self, index: pathlib.Path) -> object:
        """ That load index of the languages.

        To minimalize use of add function, it is avairable to create index
        of the languages file. Index must be simple JSON file, with dict where
        keys are POSIX formated languages names, and values are relative path
        to the phrasebook files for that language. For example:
        
        ```JSON
        {
            "en_US": "english.json",
            "pl_PL": "polish.json"
        }
        ``` 

        Parameters
        ----------
        index : pathlib.Path
            Relative to the index file from languages directory.
        
        Raises
        ------
        SyntaxError 
            When index file has invalid syntax.
        RuntimeError
            When index file not exists or is not path to the file, or path
            is not relative.
        TypeError
            When any item in index JSON file is not str.

        Returns
        -------
        languages
            Self to the chain loading.
        """

        if index.is_absolute():
            raise RuntimeError(
                "Index path \"" + \
                str(intex) + \
                "\" is absolute."
            )

        store = self.__path / index

        if not store.is_file() or not store.exists():
            raise RuntimeError("Index \"" + str(store) + "\" not exists.")

        with store.open() as handle:
            try:
                loaded = json.loads(handle.read())
            
            except Exception as error:
                raise SyntaxError(
                    "Index file \"" + \
                    str(self.__path) + \
                    "\" has invalid syntax.\n" + \
                    str(error)
                ) 
            
        for name, file in loaded.items():
            if type(name) is not str or not self.__valid_locale(name):
                raise TypeError("Invalid \"" + str(name) + "\" locale.")

            if type(file) is not str:
                raise TypeError("Invalid file for \"" + name + "\".")

            self.add(name, pathlib.Path(file))

        return self
    
    def __get_lang_file(self, name: str) -> pathlib.Path:
        """ This returns full path to the language with given name.

        Parameters
        ----------
        name : str
            Name of the file to get language of.

        Returns
        -------
        pathlib.Path
            Full path to that file.
        """

        return self.__path / self.__languages[name]

    def select(self, name: str) -> phrasebook:
        """ That load phrasebook from languages directory
        
        Parameters
        ----------
        name : str  
            Name of the language to load phrasebook for.

        Raises
        ------
        ValueError
            When not exists in library.

        Returns
        -------
        phrasebook
            Loaded phrasebook for that language.
        """

        if not name in self.__languages:
            raise ValueError("Language \"" + name + "\" not exists.")

        return loader(self.__get_lang_file(name)).load()
