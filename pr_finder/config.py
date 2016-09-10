import ConfigParser
import os
import io
import json


class DoveConfig(object):
    '''---------------------------------------------------------------

                Dove Config Interaction Tool
                ----------------------------

    This class is used to read in the dove config file.  You can
    interact with the config by getting a single config option or
    getting all the config options for a single section.

    Definitions
    -----------
    Section: sections are led by a `[section]` header and followed
             by `name: value` entries

    e.g. In the config it looks like:
        [environments]

    Examples
    --------

    # Get all config options under the environments section
    env_endpoint = DoveConfig().getAll('environments')

    # Get endpoint for prod-lon02-kraken1
    prod_lon02_kraken1_endpoint = DoveConfig().get('environments', 'prod-lon02-kraken1')

    ------------------------------------------------------------------
    '''
    def __init__(self, cfg_string=''):
        self.config = ConfigParser.ConfigParser()
        # Current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))

        if cfg_string:
            self.config.readfp(io.StringIO(cfg_string.decode('utf8')))
        else:
            self.config.read(current_dir + '/../../dove_config/dove.conf')

    def getAll(self):
        env_dict = {}
        for section in self.config.sections():
            env_dict[section] = self.getAllSection(section)
        return env_dict

    def getAllSection(self, section):
        '''Get all config options under a specific section

        Parameters
        ----------
        section: Section you want all the config values for

        Returns
        -------
        dict: key value pair of the variables defined in the section
        '''
        env_dict = {}
        for key, value in self.config.items(section):
            try:
                env_dict[key] = json.loads(value)
            except ValueError:
                env_dict[key] = value

        return env_dict

    def get(self, section, key):
        '''Get one config options under a specific section

        Parameters
        ----------
        section: Section you want all the config values for
        key:     Name of variable in config that holds the value that
                 will be returned

        Returns
        -------
        str: value of variable name defined in the specified section
        '''
        return self.config.get(section, key)