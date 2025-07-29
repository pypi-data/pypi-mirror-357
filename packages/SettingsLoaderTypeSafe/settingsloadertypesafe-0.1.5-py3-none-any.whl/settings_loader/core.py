import argparse
import json
import os
from typing import Generic, Optional, Type, TypeVar, Union, get_args, get_origin, get_type_hints
from dotenv import load_dotenv
from pydantic import BaseModel
import yaml

S = TypeVar("S")

class SettingsBase(BaseModel):
    app: Optional[BaseModel] = None
    env: Optional[BaseModel] = None
    args: Optional[BaseModel] = None
    secrets: Optional[BaseModel] = None

class SettingsLoader(Generic[S]):
    def __init__(self, settings_model: Optional[Type[S]]):
        self.settings_model = settings_model
        self.settings = None
        self.app_settings_path = 'app_settings.yaml'
        self.env_path = '.env'
        self.secrets_path = '.secrets.env'

    def configure_env(self, env_path: str):
        self.env_path = env_path
        return self

    def configure_secrets(self, secrets_path: str):
        self.secrets_path = secrets_path
        return self

    def configure_app(self, app_settings_path: str):
        self.app_settings_path = app_settings_path
        return self
    
    def build(self):
        def is_optional_base_model(field_type) -> bool:
            origin = get_origin(field_type)
            args = get_args(field_type)

            if origin is Union and any(issubclass(arg, BaseModel) for arg in args if isinstance(arg, type)):
                return True
            return False

        init_kwargs = {}
        type_hints = get_type_hints(self.settings_model)

        for field_name, field_type in type_hints.items():
            if not is_optional_base_model(field_type):
                if field_name == 'app':
                    if self.app_settings_path.endswith(('.yml', '.yaml')):
                        with open(self.app_settings_path, "r") as f:
                            app_settings = yaml.safe_load(f)
                        init_kwargs["app"] = field_type.model_validate(app_settings)
                    elif self.app_settings_path.endswith('.json'):
                        with open(self.app_settings_path, "r") as f:
                            app_settings = json.load(f)
                        init_kwargs["app"] = field_type(**app_settings)

                elif field_name == 'env':
                    load_dotenv(self.env_path, override=True)
                    init_kwargs["env"] =  field_type(**{k: v for k, v in os.environ.items()})
                    
                elif field_name == 'args':
                    parser = argparse.ArgumentParser()
                    for name, field in field_type.model_fields.items():
                        parser.add_argument(f"--{name}", help=field.description or "")
                    args = parser.parse_args()
                    cli_args_dict = {k: v for k, v in vars(args).items() if v is not None}
                    init_kwargs["args"] = field_type(**cli_args_dict)

                elif field_name == 'secrets':
                    if self.secrets_path.endswith('.env'):
                        load_dotenv(self.secrets_path, override=True)
                        init_kwargs["secrets"] = field_type(**{k: v for k, v in os.environ.items()})
                    elif self.secrets_path.endswith(('.yml', '.yaml')):
                        with open(self.secrets_path, "r") as f:
                            secret_data = yaml.safe_load(f)
                        init_kwargs["secrets"] = field_type(**secret_data)
                    elif self.secrets_path.endswith('.json'):
                        with open(self.secrets_path, "r") as f:
                            secret_data = json.load(f)
                        init_kwargs["secrets"] = field_type(**secret_data)

        self.settings = self.settings_model(**init_kwargs)
        return self.settings