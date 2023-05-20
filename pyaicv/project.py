import sys
import os
import logging
import shutil
import importlib


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def set_aicv_env_variable(key, value):
    varkey = f'AICV_{key}'
    os.environ[varkey] = str(value)


class ProjectSingleton:
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def set_config(cls, config):
        cls.setup_config = config['setup_config']
        cls.env_cfg = config['env_cfg']

    def init(cls):
        cls.__init_project_module()
        cls.__setup_root_folder()
        cls.__setup_installed_folders()
        cls.__setup_remote_parties()

    def __init_project_module(cls):
        cls.pyaicv_fp = os.path.dirname(__file__)
        # Add PyAICV module into sys.path
        sys.path.append(os.path.dirname(cls.pyaicv_fp))
        # Add PyAICV submodules into sys.path
        sys.path.append(cls.pyaicv_fp)


    def __setup_root_folder(cls):
        # Versioning & Root folder    
        app_version = cls.setup_config['version']
        version_control = cls.setup_config['project']['versionControl']
        root = cls.setup_config['project']['root']
        env = cls.setup_config['environment']
        if version_control:
            basename = os.path.basename(root)
            root = os.path.join(root, app_version, env)
        else:
            root = os.path.join(root, env)

        if cls.setup_config['project']['override']:
            if os.path.exists(root):
                shutil.rmtree(root)
                logger.warn('Project root is deleted')
        if not os.path.exists(root):
            logger.info('Project root is initated')
            os.makedirs(root)
            
        os.environ['AICV'] = root
        os.environ['AICV_ROOT'] = root

    def __setup_installed_folders(cls):
        # Directories & env vars
        insFolders = cls.env_cfg['dir']['installedFolder']
        root = os.environ['AICV']
        for f in insFolders:
            key = f.upper().replace('/','_')
            fp = os.path.join(root, f)
            if not os.path.exists(fp):
                os.makedirs(fp)
            set_aicv_env_variable(key, fp)

    def __setup_remote_parties(cls):
        cls.installedRemoteParty = {}
        remotePts = cls.env_cfg['remote']
        for pt in remotePts:
            pt_name = pt['name']
            if os.path.exists(os.path.join(cls.pyaicv_fp, pt_name)):
                logger.debug(f'Searching module {pt_name}')
                cls.installedRemoteParty[pt_name] = importlib.import_module(pt_name)
                set_aicv_env_variable(key=pt_name.upper(), value=pt)
            else:
                logger.warn(f'{pt_name} remote module is not found. Safely ignore this module')


project_singleton = ProjectSingleton()