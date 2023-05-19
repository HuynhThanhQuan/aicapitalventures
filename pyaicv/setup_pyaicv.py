import os
import argparse
import yaml
import logging
import sys
import project

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
    logger.debug('PYAICV Environment Variables: ')
    for k, v in os.environ.copy().items():
        if 'AICV' in k:
            logger.debug(f'\t{k:<25} {v}')


def load_setup_config():
    # Read setup config 
    setup_config = None
    with open('./config/setup.yaml', 'r') as file:
        setup_config = yaml.safe_load(file)
    assert setup_config, "Null setup config, cannot start initial-setup"
    assert len(setup_config) > 0, "Setup Config invalid"
    return setup_config


def load_environment_configure(setup_config):
    default_cfg = {}
    # Load default params config
    with open('./config/default_env.yaml', 'r') as file:
        default_cfg = yaml.safe_load(file)
    # Load env-params configure
    with open(os.path.join('./config/', setup_config['environment'] + '.yaml'), 'r') as file:
        env_cfg = yaml.safe_load(file)
    # Update default config with selected-env config
    default_cfg.update(env_cfg)
    
    logger.setLevel(default_cfg['logLevel'])
    logger.info('==============================================================================================')
    logger.info('==============================================================================================')
    logger.info('==============================================================================================')
    logger.info('SETUP CONFIG')
    for k, v in setup_config.items():
        logger.info(f"\t{k:<20}: {v}")
    logger.info('==============================================================================================')
    logger.info('%s' % default_cfg['desc'])
    for k, v in default_cfg.items():
        logger.debug(f"\t{k:<20}: {v}")
    logger.info('==============================================================================================')
    return default_cfg


def setup_project(setup_config, env_cfg):
    # Add PyAICV module into sys.path
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    # Version & Root folder    
    app_version = setup_config['version']
    version_control = setup_config['project']['versionControl']
    root = setup_config['project']['root']
    env = setup_config['environment']
    if version_control:
        basename = os.path.basename(root)
        root = os.path.join(root, app_version, env)
    else:
        root = os.path.join(root, env)
    os.environ['AICV'] = root

    # Directories & env vars
    insFolders = env_cfg['dir']['installedFolder']
    if not os.path.exists(root):
        os.makedirs(root)
    for f in insFolders:
        key = f.upper().replace('/','_')
        fp = os.path.join(root, f)
        if not os.path.exists(fp):
            os.makedirs(fp)
        set_aicv_env_variable(setup_config, key, fp)


def setup_project_settings(setup_config, env_cfg):
    # Set os environment for some setting configs
    # Token setting
    set_aicv_env_variable(setup_config, 'TOKEN_EXPIRY', env_cfg['tokenSetting']['expiredTime'])

    # Remote Info
    set_aicv_env_variable(setup_config, 'REMOTE',env_cfg['remote']['name'])
    set_aicv_env_variable(setup_config, 'REMOTE_METADATA', env_cfg['remote']['metadata'])


def startup():
    setup_config = load_setup_config()
    setup_logging(setup_config)
    env_cfg = load_environment_configure(setup_config)
    setup_project(setup_config, env_cfg)
    setup_project_settings(setup_config, env_cfg)
    inspect_AICV_env_vars()


startup()