
import argparse
import json
import urllib
import base64
import StringIO

from config import DoveConfig

from github3 import login

# Github Information
GITHUB_TOKEN    = '81ee0f08a9dfaf55697bb5403fc44a7f564b1b1a'
GITHUB_NAME     = 'Tom Cocozzello'
GITHUB_USERNAME = 'cocoztho000'
GITHUB_EMAIL    = 'thomas.cocozzello@gmail.com'

# Create Github Instance
#g = GitHubEnterprise('https://www.github.com')

g = login(token=GITHUB_TOKEN)

class PRFinder(object):
    """docstring for PRFinder"""
    def __init__(self):
        pass

    def main(self):
        '''main

        Find Pull Requests that are made to projects you care about and
        make a list and add them to your teams readme

        Parameters
        ----------
        repos: Comma seperated list of repos that contain the .pr_finder.conf

        Returns
        -------
        none
        '''

        parser = argparse.ArgumentParser()

        parser.add_argument(
            '--repo', type=str, required=True,
            help='Repo that contain the .pr_finder.conf')

        # Verify all arguments are valid
        args = parser.parse_args()

        self.update_pr_section_in_readme(args.repo)

    def update_pr_section_in_readme(self, repo_name):

        # Github library variables
        github_repo = g.repository(GITHUB_USERNAME, repo_name)
        # Get info about file in github
        file_info = github_repo.directory_contents('', return_as=dict)['.pr_finder.conf']
        # Get config file
        config = urllib.urlopen(file_info.git_url).read()
        t = json.loads(config)
        # Decode content which is stored as base64
        file_content = base64.b64decode(t['content'])
        print file_content
        endpoints = DoveConfig(file_content).getAll('tom')

        import pdb; pdb.set_trace()



# Used to call from command line
def main():
    PRFinder().main()

if __name__ == '__main__':
    PRFinder().main()