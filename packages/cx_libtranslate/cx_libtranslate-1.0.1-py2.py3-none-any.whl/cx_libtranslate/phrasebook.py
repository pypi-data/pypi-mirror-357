from .translation import translation

class phrasebook:
    """ It store single collection of phrases.
    
    This is responsible for searching phrases in the phrasebook, or when
    object exists, then also in the object notation.


    Methods
    -------
    tr(phrase: str) -> translation
        Translate phrase, short version of translate.

    translate(phrase: str) -> translation
        Translate phrase.

    prepare(phrase: str) -> str
        This prepare phrase, remove dots and white chars.  
    """

    def __init__(self, phrases: dict, objects: dict|None = None) -> None:
        """ This initialize new phrasebook.

        It require phrases dict and also objects for objects notation. Objects
        is optional, could be leave empty.

        Parameters
        ----------
        phrases : dict
            Dictionary with phrases.
        
        objects : dict | None, default: None
            Objects to take phrases for object notation.
        """

        self.__phrases = self.__parse_phrases(phrases)
        self.__objects = objects

    def __parse_phrases(self, phrases: dict) -> dict:
        """ This prepare phrasebook, by flattending dictionary keys.

        Parameters
        ----------
        phrases : dict
            Dictionary to parse

        Returns
        -------
        dict
            Flattened dictionary with phrases.
        """

        flattened = dict()

        for key in phrases.keys():
            flat_key = phrasebook.prepare(key)

            if flat_key in flattened:
                raise TypeError("Key \"" + flat_key + "\" exists twice.")

            flattened[flat_key] = phrases[key]

        return flattened

    def tr(self, phrase: str) -> translation:
        """ This translate phrase, from phrases or objects.

        Parameters
        ----------
        phrase : str
            Phrase to translate.

        Returns
        -------
        translation
            Translated phrase.
        """

        return self.translate(phrase)

    def translate(self, phrase: str) -> translation:
        """ This translate phrase, from phrases or objects.

        Parameters
        ----------
        phrase : str
            Phrase to translate.

        Returns
        -------
        translation
            Translated phrase.
        """
        
        if self.__is_nested(phrase):
            return self.__translate_nested(phrase)

        return self.__translate_flat(phrasebook.prepare(phrase))

    def __translate_nested(self, phrase: str) -> translation:
        """ This translate nested phrase.
        
        This transalate nested phrase, that mean phrase in object 
        notation. When objects is not set, then return phrase as
        failed translation.

        Parameters
        ----------
        phrase : str
            Nested phrase to translate.

        Raises
        ------
        SyntaxError
            When two dots '..' found in phrase.

        Returns
        -------
        translation
            Translated nested phrase.
        """

        if phrase.find("..") != -1:
            raise SyntaxError("Symbol \"..\" in \"" + phrase + "\".")

        if self.__objects is None:
            return translation(phrase, False)

        parts = phrase.split(".")
        current = self.__objects

        for part in parts:
            if type(current) is not dict:
                return translation(phrase, False)

            if not part in current:
                return translation(phrase, False)
            
            current = current[part]

        if type(current) is str:
            return translation(current, True)

        return translation(phrase, False)

    def __is_nested(self, phrase: str) -> bool:
        """ This check that phrase is nested or not. 
        
        When phrase contain white chars, or dot only as last chat, then
        it is not nested. When phrase contain dot, then phrase is nested.

        Parameters
        ----------
        phrase : str
            Phrase to check.

        Returns
        -------
        bool
            True when phrase is nested, False if not.
        """

        if phrase.find(" ") != -1:
            return False

        if phrase[-1] == ".":
            return False

        return phrase.find(".") != -1

    def __translate_flat(self, phrase: str) -> translation:
        """ This translate standard flat phrase.

        Parameters
        ----------
        phrase : str
            Phrase to translate.

        Returns
        -------
        translation
            Translation of the phrase.
        """

        if phrase in self.__phrases:
            return translation(self.__phrases[phrase], True)

        return translation(phrase, False)

    def set_as_default(self) -> None:   
        """ This set phrasebook as default.

        This create new builtin function named "_", which could be used to 
        translate phrase by phrasebook on which it is called, simple by
        use _("phrase")
        """

        import builtins
        builtins._ = lambda phrase: self.translate(phrase) 

    def prepare(phrase: str) -> str:
        """ This prepare phrase to being phrasebook dict key.
        
        Parameters
        ----------
        phrase : str
            Phrase to translate.

        Returns
        -------
        str
            Prepared phrase.
        """

        return phrase.lower().replace(" ", "_").replace(".", "")