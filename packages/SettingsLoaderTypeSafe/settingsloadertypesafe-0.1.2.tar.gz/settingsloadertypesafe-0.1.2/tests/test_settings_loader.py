from src.settings_loader.settings_loader import SettingsBase, SettingsLoader
from tests.settings import AppSettings, ArgsSettings, EnvSettings, SecretsSettings

def test_load_settings():
    class Settings(SettingsBase):
        app: AppSettings
        env: EnvSettings
        secrets: SecretsSettings

    settings = (
        SettingsLoader(Settings)
            .configure_app('settings/app_settings.yaml')
            .configure_env('settings/.env')
            .configure_secrets('settings/.secrets.env')
            .build()
    )

    assert settings.app.data_path == "data/sample1.json"
    assert settings.env.test == "hallo_world"
    assert settings.secrets.test == "hallo_world2"
    assert settings.args == None

def test_load_secrets():
    class Settings(SettingsBase):
        secrets: SecretsSettings

    settings1 = SettingsLoader(Settings).configure_secrets('settings/.secrets.env').build()
    settings2 = SettingsLoader(Settings).configure_secrets('settings/.secrets.json').build()
    settings3 = SettingsLoader(Settings).configure_secrets('settings/.secrets.yml').build()

    assert settings1.secrets == settings2.secrets
    assert settings2.secrets == settings3.secrets

def test_load_app_settings():
    class Settings(SettingsBase):
        app: AppSettings

    settings1 = SettingsLoader(Settings).configure_app('settings/app_settings.json').build()
    settings2 = SettingsLoader(Settings).configure_app('settings/app_settings.yaml').build()

    assert settings1.app == settings2.app
    
def test_load_args(monkeypatch):
    monkeypatch.setattr('sys.argv', ['program', '--show_config', 'True'])

    class Settings(SettingsBase):
        args: ArgsSettings

    settings = SettingsLoader(Settings).build()
    assert settings.args.show_config is True

def test_fallback_to_none():
    loader = SettingsLoader(SettingsBase)
    settings = loader.build()
    assert settings.app is None
    assert settings.env is None
    assert settings.args is None
    assert settings.secrets is None