class Error(Exception):
    pass


TargetReleased = Error("Skipping commit released at the target repo")
Unbuildable = Error("Skipping not buildable commit")
NoContent = Error("commit file has no content?")
Released = Error("Skipping already released nightly")
NotChanged = Error("Skipping because there are no changes to the source code")
