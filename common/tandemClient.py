from typing import Any, Dict, List
import requests

from .constants import (
    COLUMN_FAMILIES_DTPROPERTIES,
    COLUMN_FAMILIES_REFS,
    COLUMN_FAMILIES_STANDARD,
    COLUMN_FAMILIES_XREFS,
    COLUMN_NAMES_CATEGORY_ID,
    COLUMN_NAMES_CLASSIFICATION,
    COLUMN_NAMES_ELEMENT_FLAGS,
    COLUMN_NAMES_LEVEL,
    COLUMN_NAMES_NAME,
    COLUMN_NAMES_PARENT,
    COLUMN_NAMES_ROOMS,
    COLUMN_NAMES_UNIFORMAT_CLASS,
    ELEMENT_FLAGS_LEVEL,
    ELEMENT_FLAGS_ROOM,
    ELEMENT_FLAGS_STREAM,
    ELEMENT_FLAGS_SYSTEM,
    MUTATE_ACTIONS_INSERT,
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

    def create_documents(self, facility_id: str, doc_inputs: List[Any]) -> Any:
        """"
        Adds documents to the facility.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/documents'
        response = self.__post(token, endpoint, doc_inputs)
        return response

    def create_stream(self,
                      model_id: str,
                      name: str,
                      uniformat_class_id: str,
                      category_id: str,
                      classification: str | None = None,
                      parent_xref: str | None = None,
                      room_xref: str | None = None,
                      level_key: str | None = None) -> str:
        """
        Creates new stream using provided data.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/create'
        inputs = {
            'muts': [
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_NAME, name ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_ELEMENT_FLAGS, ELEMENT_FLAGS_STREAM ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_UNIFORMAT_CLASS, uniformat_class_id ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_CATEGORY_ID, category_id ]
            ],
            'desc': 'Create stream'
        }

        if classification is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_CLASSIFICATION, classification ])
        if parent_xref is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_XREFS, COLUMN_NAMES_PARENT, parent_xref ])
        if room_xref is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_XREFS, COLUMN_NAMES_ROOMS, room_xref ])
        if level_key is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_REFS, COLUMN_NAMES_LEVEL, level_key ])
        response = self.__post(token, endpoint, inputs)
        return response.get('key')
    
    def delete_stream_data(self, model_id: str, keys: List[str], substreams: List[str] | None = None, from_date: str | None = None, to_date: str | None = None) -> None:
        """
        Deletes data from given streams. It can be used to delete specified substreams or all data from give streams.
        It's also possible to delete data for given time range (from, to).
        """

        token = self.__authProvider()
        endpoint = f'timeseries/models/{model_id}/deletestreamsdata'
        inputs = {
            'keys': keys
        }
        query_params = {
        }
        if substreams is not None:
            query_params['substreams'] = ','.join(substreams)
        if from_date is not None:
            query_params['from'] = from_date
        if to_date is not None:
            query_params['to'] = to_date
        # if there are no input parameters, then delete all stream data
        if len(query_params) == 0:
            query_params['allSubstreams'] = 1
        self.__post(token, endpoint, inputs, query_params)

    def get_element(self, model_id: str, key: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns element for given key.
        """

        data = self.get_elements(model_id, [ key ], column_families)
        return data[0]

    def get_elements(self, model_id: str, element_ids: List[str] | None = None, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ], include_history: bool = False) -> Any:
        """
        Returns list of elements for given model.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': include_history,
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
    
    def get_group(self, group_id: str) -> Any:
        """
        Returns group details.
        """
        
        token = self.__authProvider()
        endpoint = f'groups/{group_id}'
        result = self.__get(token, endpoint)
        return result
    
    def get_groups(self) -> Any:
        """
        Returns list of groups.
        """
        
        token = self.__authProvider()
        endpoint = f'groups'
        result = self.__get(token, endpoint)
        return result
    
    def get_levels(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns level elements from given model.
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
            if flags == ELEMENT_FLAGS_LEVEL:
                results.append(elem)
        return results
    
    def get_model_history(self, model_id: str, timestamps: List[int], include_changes: bool = False, use_full_keys: bool = False):
        """
        Returns model changes.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/history'
        inputs = {
            'timestamps': timestamps,
            'includeChanges': include_changes,
            'useFullKeys': use_full_keys
        }
        response = self.__post(token, endpoint, inputs)
        return response
    
    def get_model_history_between_dates(self, model_id: str, from_date: int, to_date: int, include_changes: bool = True, use_full_keys: bool = True):
        """
        Returns model changes between two dates.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/history'
        inputs = {
            'min': from_date,
            'max': to_date,
            'includeChanges': include_changes,
            'useFullKeys': use_full_keys
        }
        response = self.__post(token, endpoint, inputs)
        return response

    def get_model_schema(self, model_id: str) -> Any:
        """
        Returns schema for given model URN.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/schema'
        return self.__get(token, endpoint)
    
    def get_rooms(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns room elements from given model.
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
            if flags == ELEMENT_FLAGS_ROOM:
                results.append(elem)
        return results
    
    def get_stream_data(self, model_id: str, key: str, from_date: int | None = None, to_date: int | None = None) -> Any:
        """
        Returns data for given stream. It can be used to get data for given time range (from, to).
        """
    
        token = self.__authProvider()
        endpoint = f'timeseries/models/{model_id}/streams/{key}'
        search_params = {}
        if from_date is not None:
            search_params['from'] = from_date
        if to_date is not None:
            search_params['to'] = to_date
        result = self.__get(token, endpoint, search_params)
        return result

    def get_stream_secrets(self, model_id: str, keys: List[str]) -> Any:
        """
        Returns secrets for streams.
        """

        token = self.__authProvider()
        endpoint = f'models/{model_id}/getstreamssecrets'
        inputs = {
            'keys': keys
        }
        result = self.__post(token, endpoint, inputs)
        return result
    
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
    
    def get_systems(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns system elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        };
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_SYSTEM:
                results.append(elem)
        return results
    
    def get_tagged_assets(self, model_id: str,
                          column_families: List[str] = [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES, COLUMN_FAMILIES_REFS ],
                          include_history: bool = False) -> Any:
        """
        Returns list of tagged assets from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': include_history,
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
    
    def get_views(self, facility_id: str) -> Any:
        """
        Returns list of views for given facility.
        """
        
        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/views'
        result = self.__get(token, endpoint)
        return result
    
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
    
    def reset_stream_secrets(self, model_id, stream_ids: List[str], hard_reset: bool = False) -> None:
        """
        Resets secrets for given streams.
        """
        
        token = self.__authProvider()
        endpoint = f'models/{model_id}/resetstreamssecrets'
        inputs = {
            'keys': stream_ids,
            'hardReset': hard_reset
        }
        self.__post(token, endpoint, inputs)
        return
    
    def save_document_content(self, url: str, file_path: str) -> None:
        """"
        Downloads document to local file.
        """

        token = self.__authProvider()
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return
    
    def __get(self, token: str, endpoint: str, params: Dict[str, Any] | None = None) -> Any:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def __post(self, token: str, endpoint: str, data: Any, params: Dict[str, Any] | None = None) -> Any:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.post(url, headers=headers, json=data, params=params)
        if response.status_code == 204:
            return
        return response.json()