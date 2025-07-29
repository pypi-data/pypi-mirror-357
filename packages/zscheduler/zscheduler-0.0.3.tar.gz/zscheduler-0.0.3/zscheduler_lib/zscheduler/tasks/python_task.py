"""
PythonTask class for executing Python functions and objects
"""

import inspect
import logging
import pickle
import base64
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .task import Task

logger = logging.getLogger(__name__)

class PythonTask(Task):
    """
    Task for executing Python functions and objects.

    This task can execute:
    - Plain Python functions and methods
    - Object methods (storing a reference to the object)
    - Module-level functions
    - Class methods
    """

    def __init__(
        self,
        target: Union[Callable, Any],
        *args,
        **kwargs
    ):
        """
        Initialize a new Python task.

        Args:
            target: The function, method, or object to call
            *args: Positional arguments to pass to the target
            **kwargs: Keyword arguments to pass to the target
        """
        # Determine name from target
        if hasattr(target, "__name__"):
            name = f"Python: {target.__name__}"
        elif hasattr(target, "__class__") and hasattr(target.__class__, "__name__"):
            name = f"Python: {target.__class__.__name__}"
        else:
            name = f"Python: {str(target)[:30]}"

        super().__init__(name)
        self.target = target
        self.args = args
        self.kwargs = kwargs

        # Determine if target is a method on an object
        self.is_bound_method = hasattr(target, "__self__") and inspect.ismethod(target)

        # Determine if target is callable
        self.is_callable = callable(target)

        # Store info about the function/method for serialization
        if callable(target):
            self.callable_name = getattr(target, "__name__", None)
            self.module_name = getattr(target.__module__, "__name__", None) if hasattr(target, "__module__") else None
            self.qualname = getattr(target, "__qualname__", None)
        else:
            self.callable_name = None
            self.module_name = None
            self.qualname = None

    def execute(self) -> Any:
        """
        Execute the Python function or method.

        Returns:
            The return value from the called function
        """
        logger.info(f"Executing Python task: {self.name}")

        try:
            if self.is_callable:
                result = self.target(*self.args, **self.kwargs)
                return result
            else:
                raise ValueError(f"Target is not callable: {self.target}")

        except Exception as e:
            logger.exception(f"Error executing Python task: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary for serialization.

        Note: This can only fully serialize certain types of targets.
        Complex objects or closures may not serialize properly.

        Returns:
            A dictionary representation of the task
        """
        data = super().to_dict()

        # Try to pickle the target, args, and kwargs
        try:
            pickled_target = base64.b64encode(pickle.dumps(self.target)).decode("utf-8")
            pickled_args = base64.b64encode(pickle.dumps(self.args)).decode("utf-8")
            pickled_kwargs = base64.b64encode(pickle.dumps(self.kwargs)).decode("utf-8")

            data.update({
                "pickled_target": pickled_target,
                "pickled_args": pickled_args,
                "pickled_kwargs": pickled_kwargs,
                "is_pickled": True
            })
        except Exception as e:
            # Pickling failed, store info about the function instead
            logger.warning(f"Could not pickle Python task: {e}")

            data.update({
                "callable_name": self.callable_name,
                "module_name": self.module_name,
                "qualname": self.qualname,
                "is_bound_method": self.is_bound_method,
                "is_pickled": False,
                # Provide a string representation of args and kwargs for reference
                "args_repr": repr(self.args),
                "kwargs_repr": repr(self.kwargs)
            })

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PythonTask':
        """
        Create a task from a dictionary representation.

        Args:
            data: Dictionary containing task data

        Returns:
            A new PythonTask instance or raises ValueError if cannot be deserialized
        """
        # Check if the data contains a pickled target
        if data.get("is_pickled", False):
            try:
                target = pickle.loads(base64.b64decode(data["pickled_target"]))
                args = pickle.loads(base64.b64decode(data["pickled_args"]))
                kwargs = pickle.loads(base64.b64decode(data["pickled_kwargs"]))

                task = cls(target, *args, **kwargs)

                if "id" in data:
                    task.id = data["id"]
                if "name" in data:
                    task.name = data["name"]

                return task

            except Exception as e:
                raise ValueError(f"Failed to unpickle Python task: {e}")
        else:
            # Without pickle data, we need to try to find the function by name
            module_name = data.get("module_name")
            callable_name = data.get("callable_name")

            if module_name and callable_name:
                try:
                    import importlib
                    module = importlib.import_module(module_name)
                    target = getattr(module, callable_name)

                    # Create task with empty args/kwargs
                    task = cls(target)

                    if "id" in data:
                        task.id = data["id"]
                    if "name" in data:
                        task.name = data["name"]

                    logger.warning(f"Created Python task for {module_name}.{callable_name} but without original arguments")
                    return task

                except (ImportError, AttributeError) as e:
                    raise ValueError(f"Failed to import Python task target: {e}")
            else:
                raise ValueError("Cannot deserialize Python task: missing pickled data and module/callable information")

