# github_pr_finder
This is a tool to find and keep track of all the repos Pull Request you care about and consolidate them into a `REVIEWS.md` file.

How it works is you have to add a file called `.pr_finder.conf` to the home directory of your repo. This will have the users of the repo and the repo's that have Pull Requests that are relavant to them.
The format of `.pr_finder.conf` will look like this
```config
# Format <repo_owner> = <repo_name>
[tom]
docker = docker
kubernetes = kubernetes
[Carol]
docker = docker
kubernetes = kubernetes
apple = swift
```

Then your going to need to edit the jenkins job this script is running, too include your repo.

#### The output that is added to REVIEWS.md will look like this: [REVIEWS.example.md](https://github.com/cocoztho000/github_pr_finder/blob/master/REVIEWS.example.md)
