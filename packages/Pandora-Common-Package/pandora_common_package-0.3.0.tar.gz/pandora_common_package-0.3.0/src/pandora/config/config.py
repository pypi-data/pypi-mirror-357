import configparser
import os.path


class Config:
    user_name_1: str
    user_name_2: str
    password: str
    appli_key: str
    appli_server: str
    app_name: str
    mailinator_token: str
    mailinator_base_url: str
    mailinator_domain: str

    org: str
    project: str
    ado_group_ids: list
    ado_api_url: str

    def __init__(self, config_path: str = None):
        config = configparser.ConfigParser()
        file_path = "config/config.ini"
        print("config file path:", os.path.abspath(file_path))
        config.read(file_path)
        self.user_name_1 = config['common']['user_name_1']
        self.user_name_2 = config['common']['user_name_2']
        self.password = config['common']['password']
        self.mailinator_token = config['common']['mailinator_token']
        self.mailinator_base_url = config['common']['mailinator_base_url']
        self.mailinator_domain = config['common']['mailinator_domain']
        self.ado_org = config['ado']['ado_org']
        self.group_ids = [gid.strip() for gid in config['ado'].get('ado_group_ids', '').split(',') if gid.strip()]
        self.ado_api_url = config['ado']['ado_api_url']
        self.ado_token = config['ado']['ado_token']

c_config = Config(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
