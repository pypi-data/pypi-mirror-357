class translation:
    """ This ciass is responsible for single translation in the library.

    This store single translation, and its state. Could be casted to string
    and formated. When translated phrase must contain variables, that 
    could be passed by format function, and `#{ name }` in the phrase.

    Attributes
    ----------
    text : str
        Phrase content as string.

    valid : bool
        True when phrase was translated correctly or False when not.

    Methods
    -------
    format(params: dict) -> dict
        That method could format translated phrase with given dict.
    """

    def __init__(self, content: str, success: bool = True) -> None:
        """ This create new translaed phrase. 
        
        It require string content of the translated phrase, and also state
        of the translation. When phrase was translated successfull, then 
        state is True but when phrase could not being found, state is False.

        Parameters
        ----------
        content : str
            Content of the translated phrase.
        success : bool, default: True
            State of the translation. 
        """

        self.__success = success
        self.__content = content

    def __str__(self) -> str:
        """ This returns content of the phrase.

        Returns
        -------
        str
            Content of the translated phrase.
        """

        return self.__content

    @property
    def text(self) -> str:
        """ String content of the phrase.

        Returns
        -------
        str
            Content of the translated phrase.
        """

        return self.__content

    @property
    def valid(self) -> bool:
        """ This returns that phrase was translated propertly.

        Returns
        -------
        bool
            True when phrase was translated propertly or false when not.
        """

        return self.__success

    def format(self, params: dict) -> str:
        """ This format translated phrase by inserting given items into it.

        Parameters
        ----------
        params : str
            Items to insert into translated string.

        Returns
        -------
        str
            Translated content with inserted given values.
        """

        if not self.__success:
            return self.__content

        parts = self.__content.split("#{")
        results = parts.pop(0)

        for count in parts:
            elements = count.split("}")

            if len(elements) == 1:
                results = results + count
                continue

            name = elements.pop(0).strip()
            rest = str("}").join(elements)

            if not name in params:
                results = results + rest
                continue

            results = results + str(params[name]) + rest

        return results