# coding: utf-8


class GeneralError(Exception): pass

class CommandErrorException(GeneralError): pass

class ParamOOBException(GeneralError): pass

class ConversionException(GeneralError): pass

class NothingToDoResult(GeneralError): pass

class CancelledByUser(GeneralError): pass
