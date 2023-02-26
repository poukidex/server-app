from abc import ABC, abstractmethod


class AbstractClient(ABC):
    @abstractmethod
    def get_object(self, object_name: str):
        pass

    @abstractmethod
    def delete_object(self, object_name: str):
        pass

    @abstractmethod
    def copy_object(
        self, source_object_name: str, destination_object_name: str
    ):
        pass

    @abstractmethod
    def generate_presigned_url(
        self, object_name: str, expiration: int = 3600
    ) -> str:
        pass

    @abstractmethod
    def generate_presigned_post_url(
        self, object_name: str, file_type: str, expiration: int = 3600
    ) -> dict:
        pass

    @abstractmethod
    def close_connection(self):
        pass
