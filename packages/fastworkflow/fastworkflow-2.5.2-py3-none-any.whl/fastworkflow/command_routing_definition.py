from __future__ import annotations

import os
import json
from enum import Enum
from typing import Any, Optional, Type
from pathlib import Path

from pydantic import BaseModel, PrivateAttr

from fastworkflow import ModuleType
from fastworkflow.command_directory import CommandDirectory, get_cached_command_directory
from fastworkflow.command_context_model import CommandContextModel
from fastworkflow.utils import python_utils


class CommandRoutingDefinition(BaseModel):
    """
    Defines the available commands for each context in a workflow.
    This object is built dynamically from the workflow's `context_model.json`
    and the `_commands/` directory. It is not intended to be persisted itself.
    """
    workflow_folderpath: str
    command_directory: CommandDirectory
    context_model: CommandContextModel
    
    # This will hold the resolved command lists for each context.
    contexts: dict[str, list[str]]

    def get_command_names(self, context: str) -> list[str]:
        """Returns the list of command names available in the given context."""
        if context not in self.contexts:
            raise ValueError(f"Context '{context}' not found in the workflow.")
        return self.contexts[context]

    _command_class_cache: dict[str, Type[Any]] = PrivateAttr(default_factory=dict)

    def get_command_class(self, command_name: str, module_type: ModuleType) -> Optional[Type[Any]]:
        """
        Retrieves a command's implementation class from the cache or loads it.
        The context is no longer needed for lookup, as command names are unique.
        """
        cache_key = f"{command_name}:{module_type.name}"
        if cache_key in self._command_class_cache:
            return self._command_class_cache[cache_key]
        
        result = self._load_command_class(command_name, module_type)
        self._command_class_cache[cache_key] = result
        return result

    def _load_command_class(self, command_name: str, module_type: ModuleType) -> Optional[Type[Any]]:
        """Loads a command's class from its source file."""
        try:
            # Lazily hydrate metadata so that Signature-related fields are available
            self.command_directory.ensure_command_hydrated(command_name)

            command_metadata = self.command_directory.get_command_metadata(command_name)
        except KeyError:
            # This is the expected path for commands in the context model that have no .py file.
            return None

        if module_type == ModuleType.INPUT_FOR_PARAM_EXTRACTION_CLASS:
            module_file_path = command_metadata.parameter_extraction_signature_module_path
            module_class_name = command_metadata.input_for_param_extraction_class
        elif module_type == ModuleType.COMMAND_PARAMETERS_CLASS:
            module_file_path = command_metadata.parameter_extraction_signature_module_path
            module_class_name = command_metadata.command_parameters_class
        elif module_type == ModuleType.RESPONSE_GENERATION_INFERENCE:
            module_file_path = command_metadata.response_generation_module_path
            module_class_name = command_metadata.response_generation_class_name
        else:
            raise ValueError(f"Invalid module type '{module_type}'")

        # If the command does not define the requested module/class (e.g. no Signature
        # for parameter-extraction), bail out early.  Returning ``None`` signals to
        # callers that the implementation is not available, which higher-level logic
        # already handles gracefully.
        if not module_file_path or not module_class_name:
            return None

        # Use the cached module loader
        module = python_utils.get_module(str(module_file_path), self.workflow_folderpath)

        # Handle nested classes like 'Signature.Input'
        if '.' in module_class_name:
            parts = module_class_name.split('.')
            cls_obj = module
            for part in parts:
                cls_obj = getattr(cls_obj, part, None)
            return cls_obj
        
        return getattr(module, module_class_name, None)

    def save(self):
        """Save the command routing definition to JSON, excluding the command_directory"""
        save_path = f"{CommandDirectory.get_commandinfo_folderpath(self.workflow_folderpath)}/command_routing_definition.json"
        # Create a dict without command_directory
        save_dict = self.model_dump(exclude={'command_directory'})
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, indent=4)

    @classmethod
    def load(cls, workflow_folderpath):
        """Load the command routing definition from JSON"""
        load_path = f"{CommandDirectory.get_commandinfo_folderpath(workflow_folderpath)}/command_routing_definition.json"
        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["workflow_folderpath"] = workflow_folderpath

        # Use cached command directory
        command_directory = get_cached_command_directory(workflow_folderpath)
        data["command_directory"] = command_directory

        return cls.model_validate(data)

    @classmethod
    def build(cls, workflow_folderpath: str) -> "CommandRoutingDefinition":
        """
        Builds the command routing definition by loading the context model
        and discovering commands from the filesystem.
        
        The command context model now uses qualified names for commands in context subdirectories,
        in the format 'ContextName/command_name'. This method ensures these qualified names
        are properly handled when building the routing definition.
        """       
        # Use cached command directory to avoid repeated filesystem scanning
        command_directory = get_cached_command_directory(workflow_folderpath)
        context_model = CommandContextModel.load(workflow_folderpath)

        # Use dynamically discovered core commands
        core_commands = command_directory.core_command_names

        resolved_contexts = {}
        for context_name in context_model._command_contexts:
            # Get commands for this context from the context model
            context_commands = context_model.commands(context_name)
            
            # Add core commands to every context
            resolved_contexts[context_name] = sorted(set(context_commands) | set(core_commands))

        # Ensure global context '*' also exists with core commands (if not in model)
        if '*' not in resolved_contexts:
            resolved_contexts['*'] = sorted(core_commands)

        command_routing_definition = cls(
            workflow_folderpath=workflow_folderpath,
            command_directory=command_directory,
            context_model=context_model,
            contexts=resolved_contexts,
        )

        command_routing_definition.save()
        return command_routing_definition


class CommandRoutingRegistry:
    """
    A registry that holds a single, active CommandRoutingDefinition per workflow.
    It builds the definition on-demand the first time it's requested for a workflow.
    """
    _definitions: dict[str, CommandRoutingDefinition] = {}

    @classmethod
    def get_definition(cls, workflow_folderpath: str) -> CommandRoutingDefinition:
        """
        Gets the command routing definition for a workflow.
        If it doesn't exist, it will be built and cached.
        """
        workflow_folderpath = str(Path(workflow_folderpath).resolve())

        if workflow_folderpath in cls._definitions:
            return cls._definitions[workflow_folderpath]

        # ------------------------------------------------------------
        # Try to load a persisted JSON definition if it is fresh enough
        # compared to the underlying command sources.
        # ------------------------------------------------------------
        try:
            cache_file = Path(CommandDirectory.get_commandinfo_folderpath(workflow_folderpath)) / "command_routing_definition.json"

            if cache_file.exists():
                commands_root = Path(workflow_folderpath) / "_commands"
                if commands_root.exists():
                    latest_src_mtime = max(p.stat().st_mtime for p in commands_root.rglob("*.py"))
                else:
                    latest_src_mtime = 0.0

                if cache_file.stat().st_mtime > latest_src_mtime:
                    definition = CommandRoutingDefinition.load(workflow_folderpath)
                    cls._definitions[workflow_folderpath] = definition
                    return definition
        except Exception:
            # Any issue falls back to build path
            pass

        # Fallback: build fresh definition and persist via .save()
        cls._definitions[workflow_folderpath] = CommandRoutingDefinition.build(workflow_folderpath)
        return cls._definitions[workflow_folderpath]

    @classmethod
    def clear_registry(cls):
        """Clears the registry. Useful for testing."""
        cls._definitions.clear()
        
        # Also clear the CommandDirectory cache to ensure fresh data on reload
        import fastworkflow.command_directory
        import functools
        if hasattr(fastworkflow.command_directory.get_cached_command_directory, 'cache_clear'):
            fastworkflow.command_directory.get_cached_command_directory.cache_clear()
        
        # Clear the python_utils module import cache
        import fastworkflow.utils.python_utils
        if hasattr(fastworkflow.utils.python_utils.get_module, 'cache_clear'):
            fastworkflow.utils.python_utils.get_module.cache_clear()
