import json
import logging
import base64

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests


log = logging.getLogger(__name__)


# log sent requests. received data isn't shown
def enable_requests_debug():
    import http.client

    http.client.HTTPConnection.debuglevel = 1

    log.setLevel(logging.DEBUG)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class File(object):
    def __init__(self, data, enc="ascii"):
        self.name = data["name"]
        self.path = data["path"]
        self.sha = data["sha"]

        content = base64.b64decode(data["content"])
        content = content.decode(enc).strip()
        self.content = content

    def encode_content(self, enc=None):
        data = self.content.encode("ascii")
        data = base64.b64encode(data)
        if enc:
            data = data.decode(enc)

        return data

    def __repr__(self):
        return '<File(path="{}",sha="{}">'.format(self.path, self.sha)


# TODO separate lib?
class Api(object):

    BASE_REST = "https://api.github.com/"
    BASE_GRAPHQL = "https://api.github.com/graphql"
    USER_AGENT = "mcspr/espurna-travis-test/builder-v1.0"

    def __init__(self, token):
        self.token = token

        self._http = requests.Session()
        self._http.headers.update(
            {"User-Agent": self.USER_AGENT, "Authorization": "token {}".format(token)}
        )

    def get(self, path, params=None, headers=None):
        url = urljoin(self.BASE_REST, path)
        res = self._http.get(url, params=params, headers=headers)
        return res

    def get_json(self, path, params=None, headers=None):
        return self.get(path, params=params, headers=headers).json()

    def put_json(self, path, data, headers=None):
        url = urljoin(self.BASE_REST, path)
        res = self._http.put(url, json=data, headers=None)
        return res.json()

    def post_json(self, path, data, headers=None):
        url = urljoin(self.BASE_REST, path)
        res = self._http.post(url, json=data, headers=None)
        return res.json()

    def graphql_query(self, query):
        data = json.dumps({"query": query})
        res = self._http.post(self.BASE_GRAPHQL, data=data)
        res = res.json()

        return res


class Repo(object):
    def __init__(self, slug, api):
        self.slug = slug
        self.api = api
        self.base = "repos/{}".format(slug)

        owner, name = slug.split("/")
        self.owner = owner
        self.name = name

    # TODO uritemplate?
    def _base(self, path):
        return "{}/{}".format(self.base, path)

    @property
    def clone_url(self):
        return "https://github.com/{owner}/{name}.git".format(
            owner=self.owner, name=self.name
        )

    def compare_url(self, start, end):
        url = "https://github.com/{owner}/{name}/compare/{start}...{end}".format(
            owner=self.owner, name=self.name, start=start, end=end
        )
        return url

    def file(self, ref, filepath):
        path = self._base("contents/{}".format(filepath))
        res = self.api.get_json(path, params={"ref": ref})
        return File(res)

    def update_file(self, branch, fileobj, message):
        path = self._base("contents/{}".format(fileobj.path))
        res = self.api.put_json(
            path,
            data={
                "branch": branch,
                "message": message,
                "content": fileobj.encode_content(enc="ascii"),
                "sha": fileobj.sha,
            },
        )
        return (res["content"], res["commit"])

    def release(self, sha, tag, body, name=None, prerelease=False):
        path = self._base("releases")
        data = {
            "tag_name": tag,
            "target_commitish": sha,
            "body": body,
            "prerelease": prerelease,
        }
        if name:
            data["name"] = name

        res = self.api.post_json(path, data)

        return res

    # TODO tag object, not ref. does github display this ever?
    def tag_object(self, commit, name, message):
        path = self._base("git/tags")
        sha = commit["sha"]
        res = self.api.post_json(
            path, {"type": "commit", "tag": name, "object": sha, "message": message}
        )
        return res

    def commit_status(self, sha):
        path = self._base("commits/{}/status".format(sha))
        res = self.api.get_json(path)
        return (res["state"], res["statuses"])

    def branch_head(self, branch):
        path = self._base("branches/{}".format(branch))
        res = self.api.get_json(path)
        return res["commit"]["sha"]

    # TODO find lib that does both api v3 and v4?
    # v4: graphql returns MUCH less data.
    # v3: /releases/latest also contains assets, which we don't need
    def latest_release(self):
        query = """
        query {
            repository(owner:\"OWNER\", name:\"NAME\") {
                releases(last:1) {
                    nodes {
                        id
                        url
                        publishedAt
                        tag {
                            target {
                                oid
                                commitUrl
                            }
                        }
                    }
                }
            }
        }"""
        query = query.replace("OWNER", self.owner).replace("NAME", self.name).strip()

        res = self.api.graphql_query(query)
        (release,) = res["data"]["repository"]["releases"]["nodes"]

        # XXX is this reliable?
        id = release["id"]
        del release["id"]
        id = base64.b64decode(id.encode("ascii")).decode("ascii")
        number = id.partition("Release")[-1]
        release["number"] = int(number)

        sha = release["tag"]["target"]["oid"]
        del release["tag"]
        release["sha"] = sha

        return release


# latest release will likely have same commit on both master (release branch) and dev
def release_is_head(repo, head_sha):
    release = repo.latest_release()
    release_sha = release["sha"]

    return release_sha == head_sha
