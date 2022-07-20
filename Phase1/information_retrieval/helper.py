class IdMap:
    """Helper class to store a mapping from strings to ids."""

    def __init__(self):
        self.t_id = 0
        self.str_to_id = {}
        self.id_to_str = []


    def __len__(self):
        """Return number of terms stored in the IdMap"""
        return len(self.id_to_str)

    def _get_str(self, i):
        """Returns the string corresponding to a given id (`i`)."""
        ### Begin your code
        return self.id_to_str[i]
        ### End your code

    def _get_id(self, s):
        """Returns the id corresponding to a string (`s`).
        If `s` is not in the IdMap yet, then assigns a new id and returns the new id.
        """
        ### Begin your code
        if s not in self.str_to_id:
            self.str_to_id[s]=self.t_id
            self.id_to_str.append(s)
            self.t_id +=1
        return self.str_to_id[s]
        ### End your code

    def __getitem__(self, key):
        """If `key` is a integer, use _get_str;
           If `key` is a string, use _get_id;"""
        if type(key) is int:
            return self._get_str(key)
        elif type(key) is str:
            return self._get_id(key)
        else:
            raise TypeError

if __name__ == '__main__':
    testIdMap = IdMap()
    assert testIdMap['a'] == 0, "Unable to add a new string to the IdMap"
    assert testIdMap['bcd'] == 1, "Unable to add a new string to the IdMap"
    assert testIdMap['a'] == 0, "Unable to retrieve the id of an existing string"
    assert testIdMap[1] == 'bcd', "Unable to retrive the string corresponding to a\
                                    given id"
    try:
        testIdMap[2]
    except IndexError as e:
        assert True, "Doesn't throw an IndexError for out of range numeric ids"
    assert len(testIdMap) == 2