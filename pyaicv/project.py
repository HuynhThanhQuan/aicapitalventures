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


class ProjectInstance:
    def __init__(self):
        logger.debug('--------------------------------------------------------------------------------------------------')
        logger.debug('Init project AICV')

    def set_config(self, config):
        self.setup_config = config['setup_config']
        self.env_cfg = config['env_cfg']

    def init(self):
        self.__init_project_module()
        self.__setup_root_folder()
        self.__setup_installed_folders()
        self.__setup_remote_parties()
        self.__setup_security_parties()
        self.post_setup()

    def post_setup(self):
        logger.debug('--------------------------------------------------------------------------------------------------')

    def __init_project_module(self):
        self.pyaicv_fp = os.path.dirname(__file__)
        # Add PyAICV module into sys.path
        sys.path.append(os.path.dirname(self.pyaicv_fp))
        # Add PyAICV submodules into sys.path
        sys.path.append(self.pyaicv_fp)

    def __setup_root_folder(self):
        # Versioning & Root folder    
        app_version = self.setup_config['version']
        version_control = self.setup_config['project']['versionControl']
        root = self.setup_config['project']['root']
        env = self.setup_config['environment']
        if version_control:
            basename = os.path.basename(root)
            root = os.path.join(root, app_version, env)
        else:
            root = os.path.join(root, env)

        if self.setup_config['project']['override']:
            if os.path.exists(root):
                shutil.rmtree(root)
                logger.warn('Project root is deleted')
        if not os.path.exists(root):
            logger.info('Project root is initated')
            os.makedirs(root)
            
        os.environ['AICV'] = root
        os.environ['AICV_ROOT'] = root

    def __setup_installed_folders(self):
        # Directories & env vars
        insFolders = self.env_cfg['dir']['installedFolder']
        root = os.environ['AICV']
        for f in insFolders:
            key = f.upper().replace('/','_')
            fp = os.path.join(root, f)
            if not os.path.exists(fp):
                os.makedirs(fp)
            set_aicv_env_variable(key, fp)

    def __setup_remote_parties(self):
        self.installedRemoteParty = {}
        remotePts = self.env_cfg['remote']
        valid_remote_pts = []
        for pt in remotePts:
            pt_name = pt['name']
            if os.path.exists(os.path.join(self.pyaicv_fp, pt_name)):
                logger.debug(f'Importing remote module: {pt_name}')
                self.installedRemoteParty[pt_name] = importlib.import_module(pt_name)
                valid_remote_pts.append(pt)
            else:
                logger.warn(f'{pt_name} remote module is not found. Safely ignore this module')
        set_aicv_env_variable(key='REMOTE', value=valid_remote_pts)

    def __setup_security_parties(self):
        # Add Security submodules into sys.path
        sys.path.append(os.path.join(self.pyaicv_fp, 'security'))
        self.installedSecurityParty = {}
        secPts = self.env_cfg['security']
        valid_sec_pts = []
        for sec in secPts:
            sec_name = sec['name']
            if os.path.exists(os.path.join(self.pyaicv_fp, 'security', sec_name)):
                logger.debug(f'Importing security module: {sec_name.upper()}')
                self.installedSecurityParty[sec_name] = importlib.import_module(sec_name)
                valid_sec_pts.append(sec)
            else:
                logger.warn(f'{sec_name} security module is not found. Safely ignore this module')
        set_aicv_env_variable(key='SECURITY', value=valid_sec_pts)


project_instance = ProjectInstance()