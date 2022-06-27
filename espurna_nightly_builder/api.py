import io
import re
import json
import logging
import base64
import http.client

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests

from . import __version__
from . import errors


log = logging.getLogger(__name__)


# log sent requests. received data isn't shown
def enable_requests_debug():
    http.client.HTTPConnection.debuglevel = 1

    log.setLevel(logging.DEBUG)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class File:
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
        return '<File path="{}" sha={}>'.format(self.path, self.sha)


def simple_response_error(response):
    try:
        content = response.json()
    except json.decoder.JSONDecodeError:
        content = "(no json content)"

    return errors.Error(
        "API {} {} {}: {}".format(
            response.request.method, response.status_code, response.request.url, content
        )
    )


class Api:

    BASE_REST = "https://api.github.com/"
    BASE_GRAPHQL = "https://api.github.com/graphql"
    USER_AGENT = f"mcspr/espurna_nightly_builder-v{__version__}"

    def __init__(self, token):
        self.token = token

        self._http = requests.Session()
        self._http.headers.update(
            {"User-Agent": self.USER_AGENT, "Authorization": "token {}".format(token)}
        )

    def get(self, path, params=None, headers=None, expect_status=200):
        url = urljoin(self.BASE_REST, path)
        res = self._http.get(url, params=params, headers=headers)

        if res.status_code != expect_status:
            raise simple_response_error(res)

        return res

    def get_json(self, path, params=None, headers=None):
        return self.get(path, params=params, headers=headers).json()

    def put_json(self, path, data, headers=None, expect_status=200):
        url = urljoin(self.BASE_REST, path)
        res = self._http.put(url, json=data, headers=headers)
        if res.status_code != expect_status:
            raise simple_response_error(res)

        return res.json()

    def post_json(self, path, data, headers=None, expect_status=200):
        url = urljoin(self.BASE_REST, path)

        copied = self._http.headers.copy()
        copied.update(headers)
        res = self._http.post(url, json=data, headers=copied)

        if res.status_code != expect_status:
            raise simple_response_error(res)

        if res.status_code == 204:
            return None

        return res.json()

    def delete(self, path, params=None, headers=None):
        url = urljoin(self.BASE_REST, path)
        res = self._http.delete(url, params=params, headers=headers)
        if res.status_code != 204:
            raise simple_response_error(res)

    def graphql_query(self, query):
        data = json.dumps({"query": query})
        res = self._http.post(self.BASE_GRAPHQL, data=data)

        # graphql endpoint supposed to report errors through the json,
        # so http status error still goes through the simple handler
        if res.status_code != 200:
            raise simple_response_error(res)

        data = res.json()
        if "errors" in data.keys():
            raise errors.Error(
                "API GraphQL POST errors: {}".format(
                    ",".join(error["message"] for error in data["errors"])
                )
            )

        return data


class Repo:
    def __init__(self, slug, api):
        self.slug = slug
        self.api = api
        self.base = "repos/{}".format(slug)

        owner, name = slug.split("/")
        self.owner = owner
        self.name = name

    def _base(self, path):
        return "{}/{}".format(self.base, path)

    def tags(self):
        path = self._base("tags")
        res = self.api.get_json(path)
        return res

    @property
    def clone_url(self):
        return "https://github.com/{owner}/{name}.git".format(
            owner=self.owner, name=self.name
        )

    def compare(self, start, end, diff=True):
        path = self._base("compare/{}...{}".format(start, end))

        headers = {}
        if diff:
            headers["Accept"] = "application/vnd.github.VERSION.diff"

        res = self.api.get(path, headers=headers)
        return res.text

    def contents(self, ref, filepath):
        path = self._base("contents/{}".format(filepath))
        return self.api.get_json(path, params={"ref": ref})

    def file(self, ref, filepath):
        return File(self.contents(ref, filepath))

    def update_file(self, branch, fileobj, message):
        return self.api.put_json(
            self._base("contents/{}".format(fileobj.path)),
            data={
                "branch": branch,
                "message": message,
                "content": fileobj.encode_content(enc="ascii"),
                "sha": fileobj.sha,
            },
        )

    def tag_object(self, sha):
        return self.api.get_json(self._base("git/tags/{}".format(sha)))

    def add_tag(self, name, message, sha):
        data = {"tag": name, "message": message, "object": sha, "type": "commit"}
        print(data)
        return self.api.post_json(
            self._base("git/tags"),
            data=data,
            headers={"accept": "application/vnd.github.v3+json"},
            expect_status=201,
        )

    def delete_tag(self, sha):
        return self.api.delete(self._base("git/tags/{}".format(sha)))

    def add_ref(self, ref, sha):
        return self.api.post_json(
            self._base("git/refs"),
            data={"ref": ref, "sha": sha},
            headers={"accept": "application/vnd.github.v3+json"},
            expect_status=201,
        )

    def delete_ref(self, ref):
        self.api.delete(self._base("git/refs/{}".format(ref)))

    def ref_object(self, ref):
        return self.api.get_json(self._base("git/ref/{}".format(ref)))

    def delete_release(self, number):
        self.api.delete(self._base("releases/{}".format(number)))

    def create_release(self, sha, tag, body, name=None, prerelease=False):
        data = {
            "tag_name": tag,
            "target_commitish": sha,
            "body": body,
            "prerelease": prerelease,
        }
        if name:
            data["name"] = name

        return self.api.post_json(self._base("releases"), data)

    def commit_object(self, sha):
        path = self._base("git/commits/{}".format(sha))
        res = self.api.get(path)

        return res.json()

    def commit_check_runs(self, sha):
        path = self._base("commits/{}/check-runs".format(sha))
        res = self.api.get_json(path)
        return (res["total_count"], res["check_runs"])

    def branches(self, name):
        path = self._base("branches/{}".format(name))
        res = self.api.get_json(path)
        return res

    def workflow_dispatch(self, workflow_id, ref, inputs=None):
        path = self._base("actions/workflows/{}/dispatches".format(workflow_id))
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        return self.api.post_json(
            path,
            data=data,
            headers={"accept": "application/vnd.github.v3+json"},
            expect_status=204,
        )

    def releases(self, last=1):
        template = """
        query {{
            repository(owner:"{owner}", name:"{name}") {{
                releases(last:{last}) {{
                    nodes {{
                        id
                        url
                        publishedAt
                        tag {{
                            name
                            target {{
                                oid
                                commitUrl
                            }}
                        }}
                    }}
                }}
            }}
        }}"""

        res = self.api.graphql_query(
            template.format(owner=self.owner, name=self.name, last=last).strip()
        )
        releases = res["data"]["repository"]["releases"]["nodes"]

        for release in releases:
            # wonderful implementation detail, graphql encodes the real numeric ID for some reason
            release_id = release["id"]
            del release["id"]

            release_id = base64.b64decode(release_id.encode("ascii")).decode("ascii")
            release["number"] = int(release_id.partition("Release")[-1])

            if release["tag"]:
                sha = release["tag"]["target"]["oid"]
                tag = release["tag"]["name"]
                del release["tag"]
                release["tagName"] = tag
                release["sha"] = sha
            else:
                release["sha"] = None
                release["tagName"] = None

        return releases

    def latest_release(self):
        return self.releases(last=1)[0]


class CommitRange:

    RE_BINARY_FILES = re.compile(
        r"^Binary files (?P<source_filename>[^\t\n]+) and (?P<target_filename>[^\t\n]+) differ"
    )
    RE_SOURCE_FILE = re.compile(
        r"^--- (?P<filename>[^\t\n]+)(?:\t(?P<timestamp>[^\n]+))?"
    )
    RE_TARGET_FILE = re.compile(
        r"^\+\+\+ (?P<filename>[^\t\n]+)(?:\t(?P<timestamp>[^\n]+))?"
    )

    def __init__(self, repo, start, end):
        self._repo = repo
        self._start = start
        self._end = end

    @property
    def compare_url(self):
        url = "https://github.com/{owner}/{name}/compare/{start}...{end}".format(
            owner=self._repo.owner,
            name=self._repo.name,
            start=self._start,
            end=self._end,
        )
        return url

    def path_changed(self, path_match):
        text = self._repo.compare(self._start, self._end, diff=True)
        stream = io.StringIO(text)

        def git_path(path):
            if path.startswith("a/") or path.startswith("b/"):
                return path[2:]
            return path

        # adapted from unidiff (https://github.com/matiasb/python-unidiff) + binary files support
        for line in stream:
            src_file = self.RE_SOURCE_FILE.match(line)
            if src_file:
                path = git_path(src_file.group("filename"))
                if path.startswith(path_match):
                    return True

            trg_file = self.RE_TARGET_FILE.match(line)
            if trg_file:
                path = git_path(trg_file.group("filename"))
                if path.startswith(path_match):
                    return True

            bin_files = self.RE_BINARY_FILES.match(line)
            if bin_files:
                src = git_path(bin_files.group("source_filename"))
                trg = git_path(bin_files.group("target_filename"))
                if src.startswith(path_match) or trg.startswith(path_match):
                    return True

        return False


# latest release will likely have same commit on both master (release branch) and dev
def release_is_head(repo, head_sha):
    release = repo.latest_release()
    release_sha = release["sha"]

    return release_sha == head_sha
