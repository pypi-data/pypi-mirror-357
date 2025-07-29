from jsonschema import validate
import requests

class SchemaValidatorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SchemaValidator:

    def __init__(self, url: str) -> None:
        self.url = url
        self.schema = self.__get_schema(self.url)



    def __get_schema(self, url: str) -> None:
        response = requests.get(url)
        if response.status_code != 200:
            raise SchemaValidatorException('Schema not available')

        return response.json()

    def validate(self, instance: any):
        validate(instance=instance, schema=self.schema)
