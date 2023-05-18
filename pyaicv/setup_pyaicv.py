import os
import argparse
import yaml
import logging


logger = None


def setup_logging(setup_config):
    global logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(format=setup_config['loggingFormat'])


def set_aicv_env_variable(setup_config, key, value):
    prefix = setup_config['envVarPrefix']
    varkey = f'{prefix}_{key}'
    os.environ[varkey] = str(value)


def inspect_AICV_env_vars():
    # Log all AICV env vars
    for k, v in os.environ.copy().items():
        if 'AICV' in k:
            logger.debug(f'{k:<25} {v}')


def load_setup_config():
    # Read setup config 
    setup_config = None
    with open('./config/setup.yaml', 'r') as file:
        setup_config = yaml.safe_load(file)
    assert setup_config, "Null setup config, cannot start initial-setup"
    return setup_config


def load_mode_configure(setup_config):
    default_cfg = {}
    # Load default params config
    with open('./config/default_config.yaml', 'r') as file:
        default_cfg = yaml.safe_load(file)
    # Load mode-params configure
    with open(os.path.join('./config/', setup_config['mode'] + '.yaml'), 'r') as file:
        mode_cfg = yaml.safe_load(file)
    # Update default config with selected-mode config
    default_cfg.update(mode_cfg)
    
    logger.setLevel(default_cfg['logLevel'])
    logger.info('Setup config %s' % setup_config)
    logger.info('Mode params config %s' % default_cfg)
    logger.info('%s' % default_cfg['desc'])
    return default_cfg


def setup_project(setup_config, mode_cfg):
    app_version = setup_config['version']
    version_control = setup_config['project']['versionControl']
    # Installed folders with version control setting
    root = setup_config['project']['root']
    mode = setup_config['mode']
    if version_control:
        basename = os.path.basename(root)
        root = os.path.join(root, app_version, mode)
    else:
        root = os.path.join(root, mode)

    os.environ['AICV'] = root

    # Make dir and set environment variables
    insFolders = mode_cfg['dir']['installedFolder']
    if not os.path.exists(root):
        os.makedirs(root)
    for f in insFolders:
        key = f.upper().replace('/','_')
        fp = os.path.join(root, f)
        if not os.path.exists(fp):
            os.makedirs(fp)
        set_aicv_env_variable(setup_config, key, fp)


def setup_project_settings(setup_config, mode_cfg):
    # Set os environment for some setting configs
    # Token setting
    set_aicv_env_variable(setup_config, 'TOKEN_EXPIRY', mode_cfg['tokenSetting']['expiredTime'])


def startup():
    setup_config = load_setup_config()
    setup_logging(setup_config)
    mode_cfg = load_mode_configure(setup_config)
    setup_project(setup_config, mode_cfg)
    setup_project_settings(setup_config, mode_cfg)
    inspect_AICV_env_vars()


if __name__ == '__main__':
    startup()