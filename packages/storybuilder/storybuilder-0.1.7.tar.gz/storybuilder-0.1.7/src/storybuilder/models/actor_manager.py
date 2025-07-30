import json
from typing import Optional, Any, Dict, List
from copy import deepcopy
from .actor import Actor
from ..utils.constants import debug_print

class ActorManager:
    def __init__(self):
        self.actors: List[Actor] = []
    
    def add_actor(self, name: str, **kwargs) -> int:
        """
        Add a new actor with name and optional attributes.
        Returns the ID of the newly added actor.
        """
        actor = Actor(name, **kwargs)
        actor_id = self._get_existing_actor_id(actor.name)
        if actor_id == -1:
            self.actors.append(actor)
            actor_id = len(self.actors) - 1
        else:
            raise ValueError(f"Actor with name '{actor.name}' already exists")
        return actor_id
    
    def get_actor_name(self, actor_id: int) -> Optional[str]:
        """
        Get the name of a actor by their ID.
        Returns None if actor not found.
        """
        if actor_id < 0 or actor_id >= len(self.actors):
            return None
        return self.actors[actor_id].name
    
    def get_actor_id_or_add(self, actor_name: str) -> Optional[int]:
        """
        Get the ID of a actor by their name.
        If actor not found, add a new actor with the name and return the ID.
        """
        for idx, actor in enumerate(self.actors):
            if actor.name == Actor(actor_name).name:
                debug_print(f"get_actor_id_or_add - get_actor_id: {actor_name}, actor_id: {idx}")
                return idx

        debug_print(f"get_actor_id_or_add - add_actor_name: {actor_name}")
        return self.add_actor(actor_name)
    
    def _get_existing_actor_id(self, actor_name: str) -> int:
        """
        Get the actual actor ID by name.
        Returns -1 if actor not found.
        """
        for idx, actor in enumerate(self.actors):
            if actor.name.lower() == actor_name.lower():
                return idx
        else:
            return -1
    
    def set_actor_attribute(self, actor_name: str, attribute: str, value: Any) -> bool:
        """
        Set or update an attribute for a specific actor.
        Returns True if successful, False if actor not found.
        The 'name' attribute cannot be modified.
        """
        actor_id = self._get_existing_actor_id(actor_name)
        if actor_id is not None and actor_id > -1:
            if attribute == "name":
                raise ValueError("The 'name' attribute cannot be modified")
            setattr(self.actors[actor_id], attribute, value)
            return True
        return False
        
    def get_actor_attribute(self, actor_name: str, attribute: str) -> Optional[Any]:
        """
        Get the value of a specific attribute for a actor.
        Returns None if actor or attribute not found.
        """
        for actor in self.actors:
            if actor.name.lower() == str(actor_name).lower():
                if hasattr(actor, attribute):
                    return getattr(actor, attribute)
        return None
    
    def export(self) -> List[Dict[str, Any]]:
        """
        Export all actors as a list of dictionaries that can be used as a JSON object.
        """
        return [actor.export() for actor in self.actors]
    
    def load(self, data: List[Dict[str, Any]]) -> None:
        """
        Load actors from a list of dictionaries (JSON object).
        Each dictionary must have a 'name' key.
        Raises ValueError if any actor dict is missing the 'name' key.
        """
        for actor_dict in data:
            if "name" not in actor_dict:
                raise ValueError("Each actor must have a 'name' key")
            self.add_actor(**actor_dict)

    def copy(self) -> 'ActorManager':
        """
        Create a deep copy of the ActorManager instance.
        Returns a new ActorManager instance with copied data.
        """
        new_manager = ActorManager()
        new_manager.actors = [actor.copy() for actor in self.actors]
        return new_manager