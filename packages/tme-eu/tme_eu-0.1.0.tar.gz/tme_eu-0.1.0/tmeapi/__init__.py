from collections import OrderedDict
from urllib.parse import urlencode, quote
import base64
import hmac
import hashlib
from typing import Any
from pydantic import TypeAdapter

import httpx

from .models import Ok, GetPricesData, ErrorSignature, ErrorValidation, GetPricesAndStocksData


def sign_body(action: str, params: dict[str, Any], token: str, app_secret: str):
    api_url = 'https://api.tme.eu/' + action + '.json'

    # Flatten lists into urlencoding format
    for key in list(params):
        if isinstance(params[key], list):
            for i, v in enumerate(params[key]):
                params[f'{key}[{i}]'] = v
            del params[key]

    params['Token'] = token

    params = OrderedDict(sorted(params.items()))

    encoded_params = urlencode(params, '')
    signature_base = 'POST' + '&' + quote(api_url, '') + '&' + quote(encoded_params, '')

    api_signature = base64.encodebytes(hmac.new(app_secret.encode(), signature_base.encode(), hashlib.sha1).digest()).rstrip()
    params['ApiSignature'] = api_signature

    return api_url, urlencode(params)


class TmeApi:
    def __init__(self, token: str, app_secret: str):
        self.token = token
        self.app_secret = app_secret

    def _sync_call(self, api_url: str, body: str):
        return httpx.post(api_url, content=body, headers={"Content-type": "application/x-www-form-urlencoded"})

    def get_prices(self, symbol_list: list[str], gross_prices=False, currency="EUR", lang="en", country="NL") -> Ok[GetPricesData] | ErrorSignature | ErrorValidation:
        api_url, body = sign_body('Products/GetPrices',
                                  {"SymbolList": symbol_list, "GrossPrices": gross_prices, "Currency": currency, "Country": country, "Language": lang},
                                  self.token, self.app_secret)

        adapter = TypeAdapter(Ok[GetPricesData] | ErrorSignature | ErrorValidation)
        return adapter.validate_python(self._sync_call(api_url, body).json())

    def get_prices_and_stock(self, symbol_list: list[str], gross_prices=False, currency="EUR", lang="en", country="NL") -> Ok[GetPricesAndStocksData] | ErrorSignature | ErrorValidation:
        api_url, body = sign_body('Products/GetPricesAndStocks',
                                  {"SymbolList": symbol_list, "GrossPrices": gross_prices, "Currency": currency, "Country": country, "Language": lang},
                                  self.token, self.app_secret)

        adapter = TypeAdapter(Ok[GetPricesAndStocksData] | ErrorSignature | ErrorValidation)
        return adapter.validate_python(self._sync_call(api_url, body).json())

    def autocomplete(self, phrase: str, lang="en", country="NL"):
        api_url, body = sign_body('Products/Autocomplete',
                                  {"Phrase": phrase, "Country": country, "Language": lang},
                                  self.token, self.app_secret)

        return self._sync_call(api_url, body).json()
