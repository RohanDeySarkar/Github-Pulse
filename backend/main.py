from github import Github
from github import Auth
import config
from flask import Flask, request, jsonify
from flask_cors import CORS

class GithubData:
    def __init__(self, token):
        auth = Auth.Token(token)
        self.g = Github(auth=auth)
        self.g.get_user().login
        self.github_data = []

    def get_data(self, repository):
        print(f'Fetching data for {repository} Repository...')
        try:
            repo = self.g.get_repo(repository)
            # print(dir(repo))

            count = 0
            n_latest = 12
            
            latest_open_issues = []
            open_issues = repo.get_issues(state='open')
            for issue in open_issues:
                if count == n_latest:
                    count = 0
                    break
                latest_open_issues.append({
                    "issue" : issue.title,
                    "user" : issue.user.login,
                    "href" : f'https://github.com/{repository}/pull/{issue.number}'
                })
                count += 1

            last_releases = []
            releases = repo.get_releases()
            for release in releases:
                if count == n_latest:
                    count = 0
                    break 
                last_releases.append({
                    "release" : release.title
                })
                count += 1

            languages = []
            repo_languages = repo.get_languages()
            for language in repo_languages:
                languages.append({
                    "language" : language,
                    "loc" : repo_languages[language]
                })

            contributors = 0
            page = 1
            not_empty = True
            while not_empty:
                curr_page = repo.get_contributors(anon=True).get_page(page)
                if len(curr_page) == 0:
                    not_empty = False
                    break
                for item in curr_page:
                    contributors += 1
                page += 1

            temp_data = {
                "repoName" : repo.name,
                "description": repo.description,
                "stars" : repo.stargazers_count,
                "forks" : repo.forks_count,
                "created_at" : repo.created_at,
                "updated_at" : repo.updated_at,
                "homepage" : repo.homepage,
                "latest_open_issues" : latest_open_issues,
                "releases" : last_releases,
                "languages" : languages,
                "contributors" : contributors,
                "latest_release" : last_releases[0]["release"],
            }
            return temp_data
        except:
            return f'{repository} not found'


app = Flask(__name__)
CORS(app)

@app.route('/reponame', methods=['POST'])
def get_repo_data():
    query = request.args.get('query')
    git_hub = GithubData(config.token)
    data = git_hub.get_data(query)
    return data

if __name__ == '__main__':
    app.run(debug=True)




# flask --app main --debum run





