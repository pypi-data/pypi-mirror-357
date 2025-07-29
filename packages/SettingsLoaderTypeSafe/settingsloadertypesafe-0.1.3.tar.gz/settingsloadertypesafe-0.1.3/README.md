# SettingsLoader
SettingsLoader is a component to load env, args, secrets and app settings into one type safe object.

## Install
You can either copy the code under the src directory or install it with:
```sh
pip install SettingsLoaderTypeSafe
```

When installed through pip, import it with:
```python
from settings_loader.core import SettingsBase, SettingsLoader
```

## Usage guide
First define the data classes to represent the information in your setting (env, args, secrets and app) files. Example:

```python
class InferenceSettings(BaseModel):
    model_name: str
    max_output_tokens: int
    timout: int
    max_retries: int

class AppServerSettings(BaseModel):
    host: str
    port: int
    workers: int

class EnvSettings(BaseModel):
    test: str

class SecretsSettings(BaseModel):
    chatbot_api_key: str
    test: str

class ArgsSettings(BaseModel):
    show_config: bool = Field(False, description="Entire config will be printed if true")

class AppSettings(BaseModel):
    data_path: str
    text_classifier: InferenceSettings
    app_server: AppServerSettings
```

Create a settings class that inherits from settingsBase. Overwrite the existing fields and give them custom types. Fields that are not overwriten, have a default value of None.

```python
class Settings(SettingsBase):
    app: AppSettings
    env: EnvSettings
    secrets: SecretsSettings
```

Finally, to load the settings you can do following:
```python
    settings = (
        SettingsLoader(Settings)
            .configure_app('settings/app_settings.yaml')
            .configure_env('settings/.env')
            .configure_secrets('settings/.secrets.env')
            .build()
    )
```
The configure functions are optional and can be used to load settings from a specific file. The default values are:
- env: .env
- secrets: .secrets.env
- app: app_settings.yaml

For more information and examples you can take a look at the unit tests.