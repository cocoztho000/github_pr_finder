
import argparse
import json
import urllib2
import base64
import StringIO
import time

from config import DoveConfig

from datetime import datetime
from dateutil import tz
from github3 import login
# from github3 import exceptions as Github_Exceptions
# from github3 import GitHubEnterprise


# Github Information
GITHUB_TOKEN    = 'c91e29666c2792db6175269ad866a9a2e41f297e'
GITHUB_NAME     = 'Tom Cocozzello'
GITHUB_USERNAME = 'cocoztho000'
GITHUB_EMAIL    = 'thomas.cocozzello@gmail.com'



# Create Github Instance
# g = GitHubEnterprise('https://github.ibm.com')
g = login(token=GITHUB_TOKEN)

class PRFinder(object):
    """docstring for PRFinder"""
    def __init__(self):
        self.max_prs_to_show = 15
        self.example_pr_finder_config = """
#   ____    ____      _____   ___   _   _   ____    _____   ____    #
#  |  _ \  |  _ \    |  ___| |_ _| | \ | | |  _ \  | ____| |  _ \   #
#  | |_) | | |_) |   | |_     | |  |  \| | | | | | |  _|   | |_) |  #
#  |  __/  |  _ <    |  _|    | |  | |\  | | |_| | | |___  |  _ <   #
#  |_|     |_| \_\   |_|     |___| |_| \_| |____/  |_____| |_| \_\  #

# Format <repo_name> = { "repo_owner": "<REPO OWNER>",
#                        "github_usrname": "tjcocozz",
#                        "issue_labels": "comma,seperated,list",
#                        "time_zone": "US/Central"}
# List of all possible time_zones: http://stackoverflow.com/questions/13866926/python-pytz-list-of-timezones

# You can find the `repo_name` and `repo_owner` in the url of your repo
# e.g.
# https://github.ibm.com/alchemy-containers/DevOps-Visualization-Enablement
# https://github.ibm.com/   <REPO OWNER>   /         <REPO NAME>
# Your name should be your github username to find your comments
[Tom]
# DICTIONARY KEYS AND VALUES MUST BE WRAPPED IN DOUBLE QUOTES
setup = {"text_size": "regular"}
containers-jenkins-jobs = { "repo_owner": "alchemy-containers",
                            "issue_labels": "bug"}
artsy.github.io = { "repo_owner": "artsy",
                    "issue_labels": "bug"}
Oscar-Evil-Twin = { "repo_owner": "alchemy-containers",
                    "issue_labels": "bug"}
leakcanary = { "repo_owner": "square",
               "issue_labels": "bug"}
api-test = { "repo_owner": "alchemy-containers",
             "issue_labels": "bug"}
kubernetes = { "repo_owner": "kubernetes",
               "issue_labels": "bug"}
DevOps-Visualization-Enablement = { "repo_owner": "alchemy-containers",
                                    "issue_labels": "bug" }
        """

        # REVIEWS mardown page
        self.reviews_page = markdown('')

        self.default_setup_info = {'text_size': 'regular',
                                   'github_usrname': '',
                                   'issue_labels': '',
                                   'time_zone': 'US/Central'}

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
        '''Updates the REVIEWS markdown
        Loop through users in config and find all pull requests
        for the specified projects
        Parameters
        ----------
        repos: name of the repo that has the .pr_finder config
        Returns
        -------
        none
        '''
        # Github library variables
        github_repo          = g.repository(GITHUB_USERNAME, repo_name)
        # Create file if it doesn't exits
        repo_directory_files = self.verify_files_exist(github_repo)
        # Get info about file in github
        pr_finder_file_info  = repo_directory_files['.pr_finder.conf']
        REVIEWS_file_info    = repo_directory_files['REVIEWS.md']
        users_pr_repos       = self.read_in_config(pr_finder_file_info)
        cache_review_table   = {}
        cache_issue_table    = {}

        self.reviews_page.add_h3("Legend")
        self.reviews_page.add_h5("Merge State")
        self.reviews_page.add_h6("**clean**: Ready to go :bowtie:")
        self.reviews_page.add_h6("**dirty**: Merge Conflicts :fearful:")
        self.reviews_page.add_h6("**unstable**: Tests are not passing :tired_face:")
        self.reviews_page.add_h6("**unknown**: uhh idk :no_mouth:")


        # For each person in the config
        for person, watch_repos in users_pr_repos.items():
            self.reviews_page.add_h2(person)
            # For each one of these people repos listed
            setup, repos_to_review = self._strip_setup_from_config(watch_repos)
            for watch_repo_name, repo_metadata in repos_to_review.items():
                repo_owner           = repo_metadata['repo_owner']
                issue_labels         = repo_metadata['issue_labels']
                temp_repo_owner_name = repo_owner + '/' + watch_repo_name
                github_repo          = g.repository(repo_owner, watch_repo_name)
                # For each pull request to the above repo
                max_prs              = self.max_prs_to_show
                review_table         = [['Review Title', 'Submitted By', '# of Comments', ':date:', 'merge state',
                                         'Lines +/-', 'New Patch to ' + person,
                                         'New Comments', 'Needs Review']]
                issue_table          = [['Issue Title', 'Issue #', 'Submitted By', '# of Comments', ':date:','Labels', 'New Comments']]

                # Add header to readme
                self.reviews_page.add_h3(watch_repo_name)

                # search cache for pr
                if temp_repo_owner_name in cache_review_table.keys():
                    # If repo table has already been indexed add it to the markdown
                    # and continue
                    self.reviews_page.add_table(cache_review_table[temp_repo_owner_name], setup['text_size'])
                else:
                    # Get an iterator for all the pull requests
                    repo_prs = github_repo.pull_requests(state=u'open', sort=u'open', direction=u'desc')

                    for repo_pr in repo_prs:
                        repo_pr.refresh()
                        repo_href          = '[%s](%s)' % (repo_pr.title, repo_pr.html_url)
                        number_of_comments = '%d' % ((repo_pr.review_comments_count or 0) + (repo_pr.comments_count or 0))
                        updated_date       = repo_pr.updated_at.astimezone(tz.gettz(setup['time_zone'])).strftime('%m/%d/%y %I:%M:%S %p')
                        merge_state        = repo_pr.mergeable_state or ''
                        lines_count        = '%d / %d' % (repo_pr.additions_count or 0, (repo_pr.deletions_count * -1) or 0)
                        users_name         = repo_pr.user.login
                        new_patch, new_review, needs_review = self.anylize_review_and_comments(repo_pr, setup)


                        # Only show a certain number of reviews to not clutter the page
                        if max_prs <= 0:
                            break

                        review_table.append([repo_href, users_name, number_of_comments, updated_date, merge_state,
                                             lines_count, str(new_patch),
                                             str(new_review), str(needs_review)])
                        max_prs-=1

                    cache_review_table[temp_repo_owner_name] = review_table
                    self.reviews_page.add_table(review_table, setup['text_size'])

                # search cache for pr
                if temp_repo_owner_name in cache_issue_table.keys():
                    # If repo table has already been indexed add it to the markdown
                    # and continue
                    self.reviews_page.add_table(cache_issue_table[temp_repo_owner_name], setup['text_size'])
                else:
                    if setup['issue_labels']:
                        repo_issues = github_repo.issues(state='all', sort='updated', direction='desc', labels=setup['issue_labels'] )

                        for issue in repo_issues:
                            issue.refresh()
                            issue_href          = '[%s](%s)' % (issue.title, issue.html_url)
                            issue_number        = '%d' % issue.number
                            users_name          = issue.user.login
                            number_of_comments  = '%d' % issue.comments_count or 0
                            updated_date        = issue.updated_at.astimezone(tz.gettz(setup['time_zone'])).strftime('%m/%d/%y %I:%M:%S %p')
                            labels              = ', '.join([ label.name for label in issue.labels()])
                            new_comments        = False
                            user_latest_comment = None

                            # ------------------------------------------------------------------------------
                            # Loop through comments on issue and find users latest comment if they have one
                            # ------------------------------------------------------------------------------
                            for comment in issue.comments():
                                if comment.user.login == setup['github_usrname']:
                                    if not user_latest_comment or user_latest_comment.updated_at < comment.updated_at:
                                        user_latest_comment = comment
                                    if not all_reviewers_latest_comment or all_reviewers_latest_comment.updated_at < comment.updated_at:
                                        all_reviewers_latest_comment = comment


                            # ------------------------------------------------------------------------------
                            #   See if there are newer comments then the user comment
                            # ------------------------------------------------------------------------------
                            for comment in issue.comments():
                                if user_latest_comment.updated_at < comment.updated_at:
                                    new_comments = True
                                    break

                            # ------------------------------------------------------------------------------
                            #   If user hans't commented set to true
                            # ------------------------------------------------------------------------------
                            if not user_latest_comment:
                                new_comments = True

                            issue_table.append([issue_href, issue_number, users_name, number_of_comments, updated_date, labels, str(new_comments)])

                        cache_issue_table[temp_repo_owner_name] = issue_table
                        self.reviews_page.add_table(issue_table, setup['text_size'])

        REVIEWS_file_info.update('new reviews', self.reviews_page.page.encode('utf8'))

    def _strip_setup_from_config(self, repo_info):
        temp_setup = repo_info.pop('setup', self.default_setup_info)
        for key, value in self.default_setup_info.items():
            if key not in temp_setup:
                temp_setup[key] = value
        return (temp_setup, repo_info)

    def anylize_review_and_comments(self, repo_pr, setup):
        new_patch = False
        new_review = False
        needs_review = False
        all_reviewers_latest_comment = None
        user_latest_comment = None
        # Iterate through reviews on pr and find comments by `person`
        if setup['github_usrname'] != '':
            # ------------------------------------------------------------------------------
            #    Find the latest comment the user has added
            # ------------------------------------------------------------------------------
            # Loop through comments on patch and find users latest comment if they have one
            for comment in repo_pr.issue_comments():
                comment.refresh()
                if comment.user.login == setup['github_usrname']:
                    if not user_latest_comment or user_latest_comment.updated_at < comment.updated_at:
                        user_latest_comment = comment
                    if not all_reviewers_latest_comment or all_reviewers_latest_comment.updated_at < comment.updated_at:
                        all_reviewers_latest_comment = comment

            # Loop through comments on patch and find users latest review if they have one
            for review in repo_pr.review_comments():
                if review.user.login == setup['github_usrname']:
                    if not user_latest_comment or user_latest_comment.updated_at < review.updated_at:
                        user_latest_comment = review
                    if not all_reviewers_latest_comment or all_reviewers_latest_comment.updated_at < review.updated_at:
                        all_reviewers_latest_comment = review


            # ------------------------------------------------------------------------------
            #   See if there are newer comments then the user comment
            # ------------------------------------------------------------------------------
            for comment in repo_pr.issue_comments():
                if user_latest_comment.updated_at < comment.updated_at:
                    new_review = True
                    break

            if new_review:
                for review in repo_pr.review_comments():
                    if user_latest_comment.updated_at < review.updated_at:
                        new_review = True
                        break

            # ------------------------------------------------------------------------------
            #    See if this patch needs review or is new to the user
            # ------------------------------------------------------------------------------

            for commit in repo_pr.commits():
                commit.refresh()
                date_object = datetime.strptime(commit.as_dict()['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
                date_object = date_object.replace(tzinfo=tz.gettz('UTC'))

                if user_latest_comment.updated_at < date_object:
                    new_patch = True

                if all_reviewers_latest_comment.updated_at < date_object:
                    needs_review = True


            # ------------------------------------------------------------------------------
            #   If user hans't commented set both to true
            # ------------------------------------------------------------------------------
            if not user_latest_comment:
                new_review = True
                new_patch = True

        return (new_patch, new_review, needs_review)

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

    def add_table(self, table_as_list, text_size):
        '''
        example table_as_list:
        [
            [header1, header2]
            [row1,    row2]
        ]
        '''
        if (text_size == 'small'):
            text_size_before = '<sub>'
            text_size_after = '</sub>'
        elif (text_size == 'regular'):
            text_size_before = ''
            text_size_after = ''
        else:
            text_size_before = ''
            text_size_after = ''

        def _get_table_alignment_row(number_of_rows):
            temp = ''
            for x in range(number_of_rows):
                temp += '| :---: '
            return temp + '|\n'
        if len(table_as_list) > 1:
            for idx, row in enumerate(table_as_list):
                self.page += ('| %(before)s' + '%(after)s | %(before)s'.join(row) + '%(after)s | \n') % {'before': text_size_before, 'after': text_size_after}
                if idx == 0:
                    self.page += _get_table_alignment_row(len(row))
            self.page += '\n'
        else:
            self.add_h5('No Reviews :smiley:')

# Used to call from command line
def main():
    PRFinder().main()

if __name__ == '__main__':
    PRFinder().main()
