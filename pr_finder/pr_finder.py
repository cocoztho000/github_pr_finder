
import argparse
import json
import urllib2
import base64
import StringIO
import time

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
        self.max_prs_to_show = 15
        self.example_pr_finder_config = (
            '#   ____    ____      _____   ___   _   _   ____    _____   ____    #\n'
            '#  |  _ \  |  _ \    |  ___| |_ _| | \ | | |  _ \  | ____| |  _ \   #\n'
            '#  | |_) | | |_) |   | |_     | |  |  \| | | | | | |  _|   | |_) |  #\n'
            '#  |  __/  |  _ <    |  _|    | |  | |\  | | |_| | | |___  |  _ <   #\n'
            '#  |_|     |_| \_\   |_|     |___| |_| \_| |____/  |_____| |_| \_\  #\n'
            '\n'
            '# Format <repo_name> = <repo_owner>\n'
            '\n'
            '# You can find the `repo_name` and `repo_owner` in the url of your repo\n'
            '# e.g.\n'
            '# https://github.ibm.com/alchemy-containers/DevOps-Visualization-Enablement\n'
            '# https://github.ibm.com/   <REPO OWNER>   /         <REPO NAME>\n'
            '\n'
            '[Tom]\n'
            'containers-jenkins-jobs = alchemy-containers\n'
            'artsy.github.io = artsy\n'
            'Oscar-Evil-Twin = alchemy-containers\n'
            'leakcanary = square\n'
            'api-test = alchemy-containers\n'
            'kubernetes = kubernetes\n'
            'DevOps-Visualization-Enablement = alchemy-containers\n'
        )
        # REVIEWS mardown page
        self.reviews_page = markdown('')

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

        # Create file if it doesn't exits
        repo_directory_files = self.verify_files_exist(github_repo)

        # Get info about file in github
        pr_finder_file_info = repo_directory_files['.pr_finder.conf']
        REVIEWS_file_info = repo_directory_files['REVIEWS.md']
        users_pr_repos = self.read_in_config(pr_finder_file_info)

        cache_review_table = {}

        # For each person in the config
        for person, watch_repos in users_pr_repos.items():
            self.reviews_page.add_h2(person)
            # For each one of these people repos listed
            for watch_repo_name, repo_owner in watch_repos.items():
                self.reviews_page.add_h3(watch_repo_name)
                temp_repo_owner_name = repo_owner + '/' + watch_repo_name

                # search cache for pr
                if temp_repo_owner_name in cache_review_table.keys():
                    self.reviews_page.add_table(cache_review_table[temp_repo_owner_name])
                    continue

                github_repo = g.repository(repo_owner, watch_repo_name)
                repo_prs = github_repo.pull_requests(state=u'open', sort=u'open', direction=u'desc')

                temp_readme_str = ''
                # For each pull request to the above repo
                max_prs = self.max_prs_to_show

                review_table = [['Review Title', 'Number of Comments', 'DATE']]

                for repo_pr in repo_prs:
                    number_of_comments = 0
                    new_patch_since_your_last_comment = True
                    new_review_since_your_last_review = True
                    updated_date = 0

                    if max_prs <= 0:
                        break

                    # Iterate through reviews on pr and find comments by person and how many there are
                    if person in repo_pr.review_comments().as_json():
                        pass

                    # WHY IS THIS ALWAYS -1
                    if repo_pr.review_comments().count > 0:
                        import pdb; pdb.set_trace()

                    review_table.append(['[%s](%s)' % (repo_pr.title, repo_pr.html_url), '1 Review', '8/2/1992'])
                    max_prs-=1

                cache_review_table[temp_repo_owner_name] = review_table
                self.reviews_page.add_table(review_table)


        REVIEWS_file_info.update('new reviews', self.reviews_page.page.encode('utf8'))

    def verify_files_exist(self, github_repo):
        repo_directory_files = github_repo.directory_contents('', return_as=dict)
        in_repo = True
        if '.pr_finder.conf' not in repo_directory_files:
            github_repo.create_file('.pr_finder.conf', 'adding .pr_finder config file',
                                    self.example_pr_finder_config)
            in_repo = False

        if 'REVIEWS.md' not in repo_directory_files:
            github_repo.create_file('REVIEWS.md', 'adding REVIEWS markdown file',
                                    '# THIS WILL BE OVERWRITTEN')
            in_repo = False

        if not in_repo:
            # Give github 2 seconds to update server
            time.sleep(2)
            return github_repo.directory_contents('', return_as=dict)

        return repo_directory_files

    def read_in_config(self, pr_finder_info):
        # Build request
        request = urllib2.Request(pr_finder_info.git_url)
        request.add_header('Authorization', 'Token %s' % GITHUB_TOKEN)
        # Get config file
        config = urllib2.urlopen(request).read()
        t = json.loads(config)
        # Decode content which is stored as base64
        file_content = base64.b64decode(t['content'])

        return DoveConfig(file_content).getAll()

class markdown(object):
    def __init__(self, page):
        self.page = page

    def add_h1(self, title):
        self.page += '# %s\n' % title

    def add_h2(self, title):
        self.page += '## %s\n' % title

    def add_h3(self, title):
        self.page += '### %s\n' % title

    def add_h4(self, title):
        self.page += '#### %s\n' % title

    def add_h5(self, title):
        self.page += '##### %s\n' % title

    def add_h6(self, title):
        self.page += '###### %s\n' % title

    def add_table(self, table_as_list):
        '''
        example table_as_list:
        [
            [header1, header2]
            [row1,    row2]
        ]
        '''
        def _get_table_alignment_row(number_of_rows):
            temp = ''
            for x in range(number_of_rows):
                temp += '| :---: '
            return temp + '|\n'

        for idx, row in enumerate(table_as_list):
            self.page += '|' + ' | '.join(row) + ' | \n'
            if idx == 0:
                self.page += _get_table_alignment_row(len(row))


# Used to call from command line
def main():
    PRFinder().main()

if __name__ == '__main__':
    PRFinder().main()
