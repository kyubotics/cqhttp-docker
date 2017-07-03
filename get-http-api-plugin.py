import os
import re
import json
from urllib.request import urlopen

COOLQ_DIR = '/home/user/coolq/'

APP_DIR = os.path.join(COOLQ_DIR, 'app')
CPK_NAME = 'io.github.richardchien.coolqhttpapi.cpk'
VERSION_FILE = os.path.join(
    APP_DIR, 'io.github.richardchien.coolqhttpapi.version')
CPK_FILES_URL = 'http://git.oschina.net/api/v5/repos/richardchien/coolq-http-api-cpk/contents//?page=1&per_page=100'
LATEST_RELEASE_URL = 'https://api.github.com/repos/richardchien/coolq-http-api/releases/latest'


def download():
    os.makedirs(APP_DIR, exist_ok=True)

    version = os.getenv('CQHTTP_VERSION')

    try:
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            curr_version = f.read()
    except FileNotFoundError:
        curr_version = None

    def need_download(version_needed):
        if curr_version == version_needed:
            print(
                'The current local version is exactly the version specified, so we are done.')
            return False
        return True

    if not version:
        with urlopen(LATEST_RELEASE_URL) as resp:
            release_info = json.loads(resp.read().decode('utf-8'))
            tag = release_info.get('tag_name')
            if tag and tag.startswith('v'):
                version = tag
    elif not version.startswith('v'):
        version = 'v' + version

    if not version:
        print('No version specified, or cannot fetch the latest version number.')
        return

    if not need_download(version):
        return

    print(version + ' is needed')

    cpk_url = None
    with urlopen(CPK_FILES_URL) as resp:
        dirs = json.loads(resp.read().decode('utf-8'))
        for d in dirs:
            if d.get('name') == version:
                cpk_url = d.get('download_url', '') + '/' + CPK_NAME
                break

    if not cpk_url or cpk_url.startswith('/'):
        print('The version specified is not supported in this docker image.')
        return

    print('Got cpk url:', cpk_url)

    with urlopen(cpk_url) as cpk_dl, open(os.path.join(APP_DIR, CPK_NAME), 'wb') as cpk_file:
        print('Start download...')
        cpk_file.write(cpk_dl.read())
        with open(VERSION_FILE, 'w', encoding='utf-8') as version_f:
            version_f.write(version)

        print('Download OK!')


COOLQ_CONF_DIR = os.path.join(COOLQ_DIR, 'conf')
COOLQ_CFG_FILE = os.path.join(COOLQ_CONF_DIR, 'CQP.cfg')


def enable():
    os.makedirs(COOLQ_CONF_DIR, exist_ok=True)

    try:
        with open(COOLQ_CFG_FILE, 'r') as cfg_f:
            config = cfg_f.read()
    except FileNotFoundError:
        config = ''

    has_app_section = False
    enabled = False

    if '[App]' in config:
        if 'io.github.richardchien.coolqhttpapi.status' in config:
            config = re.sub(r'io\.github\.richardchien\.coolqhttpapi\.status=?.*',
                            'io.github.richardchien.coolqhttpapi.status=1',
                            config)
        else:
            config = config.replace('[App]',
                                    '[App]\nio.github.richardchien.coolqhttpapi.status=1')
    else:
        config = '[App]\nio.github.richardchien.coolqhttpapi.status=1\n' + config

    with open(COOLQ_CFG_FILE, 'w') as cfg_f:
        cfg_f.write(config)

    print('Plugin is enabled!')


PLUGIN_CONFIG_DIR = os.path.join(
    APP_DIR, 'io.github.richardchien.coolqhttpapi')
PLUGIN_CONFIG_FILE = os.path.join(PLUGIN_CONFIG_DIR, 'config.cfg')


def make_config():
    # if os.path.exists(PLUGIN_CONFIG_FILE):
    #     print('Configuration file already exists.')
    #     return

    os.makedirs(PLUGIN_CONFIG_DIR, exist_ok=True)

    configs = ['[general]']

    for key, value in os.environ.items():
        key = key.lower()
        if not key.startswith('cqhttp_'):
            continue

        key = key[7:]
        if key == 'version':
            continue
        configs.append(key + '=' + value)

    with open(PLUGIN_CONFIG_FILE, 'w', encoding='utf-8') as cfg_f:
        cfg_f.write('\n'.join(configs))

    print('Configuration file created.')


if __name__ == '__main__':
    download()
    enable()
    make_config()
