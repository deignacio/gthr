gthr
====

git tag heroku releases

Finding a sane way to see the connection between a project's git
repo and the corresponding heroku release can be a bit rough.

   [heroku releases](https://devcenter.heroku.com/articles/releases)

provides a log of deployment actions to their servers.  These can
be either a code push, or a config var or addon change.  The code
push however only lists the hash for the compiled slug that is
running as opposed to the git hash that developers can relate to.

This script is meant to wrap the git push to heroku servers and
to scrape the stdout/stderr of the push and tag the source git
repo appropriately.


thoughts:
* This process is reliant on scraping the heroku specific output
  during a deployment.  Any changes by heroku's pre-receive hook
  can break this script.
* I'm thinking that it might make sense to add a symlink of gthr.py
  to something like git-gthr in your path so that you can just use

    git gthr heroku master

  when you are deploying to heroku, and then

    git push origin master

  when you are deploying to your own git repos.


For more info or plans, probably just look at the [github page](https://github.com/deignacio/gthr)
