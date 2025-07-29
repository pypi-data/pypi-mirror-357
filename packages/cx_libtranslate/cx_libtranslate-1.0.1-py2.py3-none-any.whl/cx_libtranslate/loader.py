import json
import pathlib 

from .phrasebook import phrasebook

class loader:
    """ It load phrasebook from JSNO file.
    
    Methods
    -------
    load() -> phrasebook    
        This load phrasebook from path in constructor.
    """

    def __init__(self, path: pathlib.Path) -> None:
        """ This create new phrasebook loader from path to phrasebook.

        Parameters
        ----------
        path : pathlib.Path
            Path to the phrasebook to load.
        """

        self.__path = path
    
    def load(self) -> object:
        """ This load phrasebook given in constructor
        
        Raises
        ------
        RuntimeError
            When phrasebook file does not exists.
        SyntaxError
            When phrasebook file has invalid syntax.
        
        Returns
        -------
        phrasebook
            Loaded phrasebook
        """

        if not self.__path.is_file():
            raise RuntimeError(
                "Phrasebook file \"" + \
                str(self.__path) + \
                "\" not exists."
            )

        with self.__path.open() as handle:
            try:
                return self.__parse(json.loads(handle.read()))

            except Exception as error:
                raise SyntaxError(
                    "Phrasebook file \"" + \
                    str(self.__path) + \
                    "\" has invalid syntax.\n" + \
                    str(error)
                ) 

    def __parse(self, content: dict) -> phrasebook:
        """ This parse phrasebook file to phrasebook object.

        Parameters
        ----------
        content : dict
            Content of the JSON phrasebook file.

        Returns
        -------
        phrasebook
            Loaded phrasebook file.
        """

        has_objects = ( 
            "objects" in content and \
            type(content["objects"]) is dict
        )

        has_phrases = (
            "phrases" in content and \
            type(content["phrases"]) is dict
        )

        is_nested = (has_objects or has_phrases)

        if is_nested:
            phrases = content["phrases"] if has_phrases else dict()
            objects = content["objects"] if has_objects else dict()

            return phrasebook(self.__parse_phrases(phrases), objects)

        return phrasebook(self.__parse_phrases(content))

    def __parse_phrases(self, content: dict) -> dict:
        """ This parse phrases from phrasebook file to dict.

        Parameters
        ----------
        content : dict
            Content of the phrases part from file to parse.

        Returns
        -------
        dict
            Parsed phrases from file.
        """

        result = dict()
        
        for phrase, translation in content.items():
            result[phrasebook.prepare(phrase)] = translation

        return result


