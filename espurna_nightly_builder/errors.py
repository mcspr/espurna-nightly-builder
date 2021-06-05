class Error(Exception):
    pass


TargetReleased = Error("Skipping commit released at the target repo")
NoChecks = Error("Skipping commit without any check runs")
Unbuildable = Error("Skipping not buildable commit")
NoContent = Error("commit file has no content?")
Released = Error("Skipping already released nightly")
NotChanged = Error("Skipping because there are no changes to the source code")
NoToken = Error("No token env variable found")
MultipleParents = Error("Builder branch commit contains multiple parents")
NoParents = Error("Builder branch commit contains multiple parents")
