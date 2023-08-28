import requests
import os 
from datetime import datetime, timedelta

class GithubCommitExtractor:
    def __init__(self, repo_url, ):
        self.repo_url  = repo_url
        self.api_url = self._create_api_url()
        self.git_token = os.environ.get("GITHUB_TOKEN")

    def _create_api_url(self):
        api_url = self.repo_url.replace('https://github.com', 'https://api.github.com/repos')
        return api_url
    
    def fetch_commits(self, time_window_days = 180):
        try:
            api_commits_url = f"{self.api_url}/commits"
            commits = []

            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()
            
            headers = {"Authorization": "token {}".format(self.git_token)}
            params = {'since': since_date, 'per_page': 100}
            while True:
                response = requests.get(api_commits_url, params={'since': since_date}, headers=headers)
                response_json = response.json()

                if response.status_code != 200:
                    raise Exception(f"Error fetching commits: {response_json['message']}")

                commits.extend(response_json)

                if 'next' in response.links:
                    api_commits_url = response.links['next']['url']
                else:
                    break

            return commits

        except requests.exceptions.RequestException as e:
            return {"error": f"Request error: {e}"}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}

# # Example usage
# if __name__ == "__main__":
#     repo_url = "https://github.com/apache/airflow"
#     commit_extractor = GithubCommitExtractor(repo_url)
#     commits = commit_extractor.fetch_commits(time_window_days=180)
#     print(commits)
