from pydantic import BaseModel
from typing import TypeVar, Literal, Generic

DataT = TypeVar("DataT")

Currencies = Literal['EUR']
Languages = Literal['EN']
PriceTypes = Literal['NET', 'GROSS']
Units = Literal['pcs']
VatType = Literal['VAT']


class ValidationDetailsInner(BaseModel):
    value: list[str]
    message: str


class ErrorValidationDetails(BaseModel):
    Validation: dict[str, ValidationDetailsInner]


class ErrorValidation(BaseModel):
    Status: Literal['E_INPUT_PARAMS_VALIDATION_ERROR']
    Data: list
    ErrorCode: int
    ErrorMessage: str
    Error: ErrorValidationDetails


class ErrorSignature(BaseModel):
    Status: Literal['E_INVALID_SIGNATURE']
    Data: list
    ErrorCode: int
    ErrorMessage: str
    Error: list


class Ok(BaseModel, Generic[DataT]):
    Status: Literal['OK']
    Data: DataT


class PriceQty(BaseModel):
    Amount: int
    PriceValue: float
    PriceBase: int
    Special: bool


class PriceDetails(BaseModel):
    Symbol: str
    PriceList: list[PriceQty]
    Unit: Units
    VatRate: float
    VatType: VatType


class GetPricesData(BaseModel):
    Currency: Currencies
    Language: Languages
    PriceType: PriceTypes
    ProductList: list[PriceDetails]


class PriceAndStockDetails(BaseModel):
    Symbol: str
    PriceList: list[PriceQty]
    Unit: Units
    VatRate: float
    VatType: VatType
    Amount: int


class GetPricesAndStocksData(BaseModel):
    Currency: Currencies
    Language: Languages
    PriceType: PriceTypes
    ProductList: list[PriceAndStockDetails]
