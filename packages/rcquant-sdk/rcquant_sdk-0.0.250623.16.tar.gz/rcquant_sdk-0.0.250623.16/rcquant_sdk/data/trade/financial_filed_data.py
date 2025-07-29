from ...interface import IData
from ...packer.trade.financial_filed_data_packer import FinancialFiledDataPacker


class FinancialFiledData(IData):
    def __init__(self, instrument_id: str, stat_date: int, pub_date: int, type: int, json_data: str):
        super().__init__(FinancialFiledDataPacker(self))
        self._ID: int = -1
        self._InstrumentID: str = instrument_id
        self._StatDate: int = stat_date
        self._PubDate: int = pub_date
        self._Type: int = type
        self._JsonData: str = json_data

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value: int):
        self._ID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def StatDate(self):
        return self._StatDate

    @StatDate.setter
    def StatDate(self, value: int):
        self._StatDate = value

    @property
    def PubDate(self):
        return self._PubDate

    @PubDate.setter
    def PubDate(self, value: int):
        self._PubDate = value

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value: int):
        self._Type = value

    @property
    def JsonData(self):
        return self._JsonData

    @JsonData.setter
    def JsonData(self, value: str):
        self._JsonData = value
