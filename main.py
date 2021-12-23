import re
from dotenv import load_dotenv
from github import Github, Issue
from datetime import datetime, timedelta
import os
load_dotenv()


token = os.getenv("GH_PAT")
repo_name = "zite-io/zite"

point_match_regex = re.compile(r'(point)\s+(\d+)')


g = Github(token)
repo = g.get_repo(repo_name)

"""CARD"""
for i in repo.get_projects(): #sprints
    print(i.created_at)
    print(i.body)
    # for j in i.get_columns(): #cols
    #     for k in j.get_cards(): #cards
    #         print(k.get_content()) 
    break
"""CARD END"""

last_24_hr = datetime.now() - timedelta(days=15)

issues = repo.get_issues(state="closed", since=last_24_hr)

# for i in issues:
#     print(i.state)
#     break

total_points_obtained:int = 0
for issue in issues:
    for label in issue.labels:
        matches = re.findall(point_match_regex, label.name)
        if len(matches)> 0:
            for i in matches:
                print(i)
                total_points_obtained += int(i[-1])
print(f"Total Points obtained: {total_points_obtained}")