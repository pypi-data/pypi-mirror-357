"""
Factory functions for repository management.

This module provides utility functions for dynamically loading and managing
repository classes in the modelrepo package.
"""

from typing import TypeVar, Type, Dict, Any
import importlib

from .repository import ModelRepository


T = TypeVar("T")


def get_repository(
    model_class: Type[T], class_path: str, kwargs: Dict[str, Any]
) -> ModelRepository[T]:
    """
    Dynamically import and return a ModelRepository factory from a fully qualified path.

    This function allows for dynamic loading of repository implementations based on
    configuration, enabling flexible repository selection without hard-coded dependencies.

    Args:
        class_path: A string representing the fully qualified path to the repository class
                   (e.g., "modelrepo.repository.MongoDBModelRepository")

    Returns:
        The factory to create the ModelRepository referenced by the path

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class does not exist in the specified module

    Example:
        >>> repo_factory = get_repository_factory('modelrepo.repository.InMemoryModelRepository')
        >>> repo_instance = repo_factory()
    """
    print("Using model repository class:", class_path)

    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        my_class = getattr(module, class_name)
        return my_class[model_class](model_class=model_class, **kwargs)
    except (ImportError, AttributeError) as e:
        print(f"Error importing class '{class_path}': {e}")
        raise
