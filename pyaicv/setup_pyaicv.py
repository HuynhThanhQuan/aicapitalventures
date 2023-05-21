import os
import argparse
import yaml
import logging
import sys


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
    logger.debug('*******')
    logger.debug('PYAICV Environment Variables: ')
    for k, v in os.environ.copy().items():
        if 'AICV' in k:
            try:
                v_str = str(v)
                v_str = v_str[:71] if len(v_str) <= 71 else v_str[:71] + '...'
            except:
                v_str = v
            logger.debug(f'\t{k:<25} {v_str}')
    logger.debug('*******')


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
    from project import project_instance as proj
    proj.set_config(
        config={
            'setup_config': setup_config,
            'env_cfg': env_cfg})
    proj.init()


def startup():
    setup_config = load_setup_config()
    setup_logging(setup_config)
    env_cfg = load_environment_configure(setup_config)
    setup_project(setup_config, env_cfg)
    inspect_AICV_env_vars()


startup()