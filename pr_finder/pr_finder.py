
import argparse
import json
import urllib
import base64
import StringIO

from config import DoveConfig

from github3 import login

# Github Information
GITHUB_TOKEN    = ''
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
        repo_directory_files = github_repo.directory_contents('', return_as=dict)

        # TODO(tjcocozz): find what error is thrown when these are not
        # here and catch it and end the program. telling user they
        # need to add these two files to repo

        # Get info about file in github
        pr_finder_file_info = repo_directory_files['.pr_finder.conf']
        REVIEWS_file_info = repo_directory_files['REVIEWS.md']

        users_pr_repos = self.read_in_config(pr_finder_file_info)

        review_file_new_content = ''

        # Cache for prs
        save_prs = {}

        # For each person in the config
        for person, watch_repos in users_pr_repos.items():
            review_file_new_content += '\n##%s' % person
            # For each one of these people repos listed
            for repo_owner, watch_repo_name in watch_repos.items():
                review_file_new_content += '\n###%s' % watch_repo_name
                temp_repo_owner_name = repo_owner + '/' + watch_repo_name

                # search cache for pr
                if temp_repo_owner_name in save_prs.keys():
                    review_file_new_content += save_prs[temp_repo_owner_name]
                    continue

                github_repo = g.repository(repo_owner, watch_repo_name)
                repo_prs = github_repo.pull_requests(state=u'open', sort=u'open', direction=u'desc')

                temp_readme_str = ''
                # For each pull request to the above repo
                for repo_pr in repo_prs:
                    temp_readme_str += '\n#####%s' % repo_pr.title

                review_file_new_content + temp_readme_str
                save_prs[temp_repo_owner_name] = temp_readme_str

        import pdb; pdb.set_trace()
        REVIEWS_file_info


    def read_in_config(self, pr_finder_info):

        # Get config file
        config = urllib.urlopen(pr_finder_info.git_url).read()
        t = json.loads(config)
        # Decode content which is stored as base64
        file_content = base64.b64decode(t['content'])

        return DoveConfig(file_content).getAll()


# Used to call from command line
def main():
    PRFinder().main()

if __name__ == '__main__':
    PRFinder().main()