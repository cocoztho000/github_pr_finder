

class PRFinder(object):
	"""docstring for PRFinder"""
	def __init__(self):
		pass

	def main(self)
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

	def update_pr_section_in_readme(self, repo)
		pass

# Used to call from command line
def main()
	PRFinder().main()
