import os
import argparse
import yaml
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)-7s - %(name)-15s - %(message)s')


def set_aicv_env_variable(setup_config, key, value):
    prefix = setup_config['envVarPrefix']
    varkey = f'{prefix}_{key}'
    os.environ[varkey] = str(value)


def log_all_AICV_env_vars():
    # Log all AICV env vars
    for k, v in os.environ.items():
        if 'AICV' in k:
            logger.debug(f'{k:<25} {v}')


def startup():
    parser = argparse.ArgumentParser(
                        prog='AI Capital Ventures config',
                        description='Commands to operate all activities of AI Capital Ventures ',
                        epilog='Please DM hthquan28@gmail.com to help')
    parser.add_argument('config', help='Config file to setup AI Capital Ventures app',type=str)
    args = parser.parse_args()

    # Read setup config 
    with open(args.config, 'r') as file:
        setup_config = yaml.safe_load(file)
    app_version = setup_config['version']
    version_control = setup_config['versionControl']
    
    # Load mode-params configure
    with open(os.path.join(setup_config['configDir'], setup_config['mode'] + '.yaml'), 'r') as file:
        mode_cfg = yaml.safe_load(file)
    logger.setLevel(mode_cfg['logLevel'])
    logger.info('Setup config %s' % setup_config)
    logger.debug('Mode params config %s' % mode_cfg)

    # Installed folders with version control setting
    root = mode_cfg['dir']['root']
    if version_control:
        parent_folder = os.path.dirname(root)
        basename = os.path.basename(root)
        root = os.path.join(parent_folder, app_version, basename)

    # Make dir and set environment variables
    insFolders = mode_cfg['dir']['installedFolder']
    os.environ['AICV'] = root
    if not os.path.exists(root):
        os.makedirs(root)
    for f in insFolders:
        key = f.upper().replace('/','_')
        fp = os.path.join(root, f)
        if not os.path.exists(fp):
            os.makedirs(fp)
        set_aicv_env_variable(setup_config, key, fp)


    # Set os environment for some setting configs
    # Token setting
    set_aicv_env_variable(setup_config, 'TOKEN_EXPIRY', mode_cfg['tokenSetting']['expiredTime'])

    log_all_AICV_env_vars()