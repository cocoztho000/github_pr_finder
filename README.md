# github_pr_finder
This is a tool to find and keep track of all the repos Pull Request you care about and consolidate them into a `REVIEWS.md` file.

How it works is you have to add a file called `.pr_finder.conf` to the home directory of your repo you would like to show your relavant Pull Request for.
The format of `.pr_finder.conf` will look like this
```config
# Format :owner/:repo
[tom]
docker = docker
kubernetes = kubernetes
[Carol]
docker = docker
kubernetes = kubernetes
apple = swift
```

Then your going to need to edit the jenkins job this script is running to include your repo.

#### The output that is added to REVIEWS.md will look like this
