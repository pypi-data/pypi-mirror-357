from futurehouse_client.clients.rest_client import RestClient
from futurehouse_client.models.app import Stage
from futurehouse_client.models.rest import WorldModel
from uuid import UUID
from aviary.core import Tool


class WorldModelTools:
    CLIENT = RestClient(
            stage = Stage.DEV,
            api_key="Dk7WJRLpqTFNxp5dYRoj6A.platformv01.eyJqdGkiOiI4ODAyZmZiNy1hNjM2LTRkMWYtYWE4NC1lZTQzYTMzMzRjZGMiLCJzdWIiOiJuN1dJbGU5VDljZ1BkTjd2OUJlM0pEUlpZVTgyIiwiaWF0IjoxNzQ5MDc2NzYzfQ.vThmFNLChP54DZBwB+qeMTB6CvAQ1IVXkTcpB0+efZ0",
        )
    
    @staticmethod
    def create_world_model(name: str, description: str, content: str) -> UUID:
        """Create a new world model.
        
        Args:
            name: The name of the world model.
            description: A description of the world model.
            content: The content/data of the world model.
            
        Returns:
            UUID: The ID of the newly created world model.
        """
        world_model = WorldModel(
            name=name,
            description=description,
            content=content,
        )
        return WorldModelTools.CLIENT.create_world_model(world_model)
    
    @staticmethod
    def search_world_models(query: str) -> list[str]:
        """Search for world models using a text query.
        
        Args:
            query: The search query string to match against world model content.
            
        Returns:
            list[str]: A list of world model IDs that match the search query.
        """
        return WorldModelTools.CLIENT.search_world_models(query, size=1)
    
create_world_model_tool = Tool.from_function(WorldModelTools.create_world_model)
search_world_model_tool = Tool.from_function(WorldModelTools.search_world_models)

def make_world_model_tools() -> list[Tool]:
    return [
        search_world_model_tool,
        create_world_model_tool,
    ]