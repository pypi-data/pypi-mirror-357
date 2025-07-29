from typing import List
from ...interface import IData
from ...packer.trade.save_Financial_param_data_packer import SaveFinancialParamDataPacker
from .financial_filed_data import FinancialFiledData


class SaveFinancialParamData(IData):
    def __init__(self):
        super().__init__(SaveFinancialParamDataPacker(self))
        self._DataList: List[FinancialFiledData] = []

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[FinancialFiledData]):
        self._DataList = value
