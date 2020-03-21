'''
This file provides a class for handling, serializing, reading, and writing animal count data.
'''

class CountData:

    def __init__(self, species:str='', number:int=1, isDuplicate:bool=False, notes:str=''):
        self.species = species
        self.number = number
        self.isDuplicate = isDuplicate
        self.notes = notes

    def toDict(self):
        '''
        Converts this class to an easily serializable dict.
        '''
        return {
            'Species': self.species,
            'Number': self.number,
            'isDuplicate': self.isDuplicate,
            'Notes': self.notes,
        }

    @staticmethod
    def fromDict(d:dict):
        '''
        Initializes object from a dict. Ideally created with `toDict` method.
        If the input dict is None, returns None.
        '''

        if d is None:
            return None

        # Retreive values
        species = d['Species']
        number = d['Number']
        isDuplicate = d['isDuplicate']
        notes = d['Notes']

        # Create instance
        return CountData(species, number, isDuplicate, notes)

    def toToolTip(self):
        '''
        Converts the data in this object into a string suitable for a tool tip.
        '''
        return f'{self.number} {self.species}'

    def __eq__(self, other):
        return (
            self.species == other.species
            and self.number == other.number
            and self.isDuplicate == other.isDuplicate
            and self.notes == other.notes
        )