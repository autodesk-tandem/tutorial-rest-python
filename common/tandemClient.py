from typing import Any, List
import requests

from .constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_REFS,
    COLUMN_FAMILIES_STANDARD,
    ELEMENT_FLAGS_STREAM,
    QC_ELEMENT_FLAGS
)

class TandemClient:
    """ A simple wrapper for Tandem Data API """

    def __init__(self, callback) -> None:
        """
        Creates new instance of TandemClient.
        """

        self.__authProvider = callback
        self.__base_url = 'https://developer.api.autodesk.com/tandem/v1'
        pass

    def __enter__(self) -> "TandemClient":
        return self
    
    def __exit__(self, *args: any)-> None:
        pass

    def get_elements(self, model_id: str, element_ids: List[str] | None = None) -> Any:
        """
        Returns list of elements for given model.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': [ COLUMN_FAMILIES_STANDARD ],
            'includeHistory': False,
            'skipArrays': True
        }
        if element_ids is not None and len(element_ids) > 0:
            inputs['keys'] = element_ids
        result = self.__post(token, endpoint, inputs)
        return result[1:]
    
    def get_facility(self, facility_id: str) -> Any:
        """
        Retuns facility for given facilty urn.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}'
        return self.__get(token, endpoint)
    
    def get_facility_template(self, facility_id: str) -> Any:
        """
        Retuns facility teplate for given facilty urn.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/inlinetemplate'
        return self.__get(token, endpoint)
    
    def get_model_schema(self, model_id: str) -> Any:
        """
        Returns schema for given model URN.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/schema'
        return self.__get(token, endpoint)
    
    def get_tagged_assets(self, model_id: str) -> Any:
        """
        Returns list of tagged assets from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': [
                COLUMN_FAMILIES_STANDARD,
                COLUMN_FAMILIES_DTPROPERTIES,
                COLUMN_FAMILIES_REFS ],
            'includeHistory': False,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            keys = elem.keys()
            custom_props = []

            for k in keys:
                if k.startswith('z:'):
                    custom_props.append(k)
            if len(custom_props) > 0:
                results.append(elem)
        return results
    
    def get_streams(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns stream elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_STREAM:
                results.append(elem)
        return results
    
    def mutate_elements(self, model_id: str, keys: List[str], mutations, description: str) -> Any:
        """
        Modifies given elements.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/mutate'
        inputs = {
            'keys': keys,
            'muts': mutations,
            'desc': description
        }
        result = self.__post(token, endpoint, inputs)
        return result
    
    def __get(self, token: str, endpoint: str) -> Any:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.get(url, headers=headers)
        return response.json()
    
    def __post(self, token: str, endpoint: str, data: Any) -> Any:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.post(url, headers=headers, json=data)
        return response.json()