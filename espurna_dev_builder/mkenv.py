def mkenv(repo):
    release = repo.latest_release()
    number = release["number"]
    with open("environment", "w") as f:
        f.write("export TRAVIS_RELEASE_NUMBER={}\n".format(number))
