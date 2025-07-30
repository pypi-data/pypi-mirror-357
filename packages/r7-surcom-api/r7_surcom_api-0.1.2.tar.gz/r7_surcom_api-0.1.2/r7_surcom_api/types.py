"""Module that defines a SurcomType"""

from abc import ABC


class SurcomType(ABC):
    """
    A 'Type' in SurfaceCommand where its `content` is
    a dict containing the data for the type and its
    class name is the Type Name

    Here is an example using it in a connector:

        ```
        from r7_surcom_api import surcom_function, SurcomType, MoreDataManager

        class MockConnectorAssetType(SurcomType):
            pass

        @surcom_function()
        def get_assets(
            __user_log,
            more_data: MoreDataManager = None,
            settings: dict = None
        ):

            t1 = MockConnectorAssetType({"name": "asset_1"})
            t2 = MockConnectorAssetType({"name": "asset_2"})
            t3 = MockConnectorAssetType({"name": "asset_3"})

            items = [t1, t2, t3]

            more_data.done()

            return items
        ```
    """
    def __init__(self, content: dict):
        self.content = content

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def to_batch_item(self) -> dict:
        return {"type": str(self), "content": self.content}
