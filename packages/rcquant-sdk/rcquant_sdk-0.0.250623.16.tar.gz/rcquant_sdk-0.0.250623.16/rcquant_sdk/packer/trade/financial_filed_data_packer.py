from ...interface import IPacker


class FinancialFiledDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [int(self._obj.ID), str(self._obj.InsID),
                int(self._obj.StatDate), int(self._obj.PubDate),
                int(self._obj.Type), str(self._obj.JsonData)]

    def tuple_to_obj(self, t):
        if len(t) >= 6:
            self._obj.ID = t[0]
            self._obj.InsID = t[1]
            self._obj.StatDate = t[2]
            self._obj.PubDate = t[3]
            self._obj.Type = t[4]
            self._obj.JsonData = t[5]

            return True
        return False
