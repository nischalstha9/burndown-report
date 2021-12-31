import re
from dotenv import load_dotenv
from github import Github, Project
from datetime import datetime,  timedelta
import os
load_dotenv()


token = os.getenv("GH_PAT")
repo_name = "zite-io/zite"

point_match_regex = re.compile(r'(point)\s+(\d+)')

# new_regex = re.compile(r'([pP]oint)s?[\s*\-_](\d+)')


g = Github(token)
repo = g.get_repo(repo_name)

all_sprints = repo.get_projects().reversed #THis Can be looped for every active sprint
sprint:Project = all_sprints[0]


def calculate_latest_sprint_points(sprint:Project):
    print(sprint.name)
    print(sprint.created_at)
    total_sprint_points = 0
    sprint_day_index = sprint.created_at
    points_dictionary = {}
    while (sprint_day_index<datetime.now()):
        points_dictionary[str(sprint_day_index.date())] = 0
        sprint_day_index+=timedelta(days=1)
    for col in sprint.get_columns():
        for card in col.get_cards():
            issue_id = int(card.content_url.split("/")[-1])
            issue = repo.get_issue(number=issue_id)
            for label in issue.labels:
                matches = re.findall(point_match_regex, label.name)
                if len(matches)> 0:
                    for match in matches:
                        total_sprint_points += int(match[-1])
                    for match in matches:
                        point = int(match[-1])
                        if issue.state == "closed":
                            iss_closed_date = str(issue.closed_at.date())
                            try:
                                points_dictionary[iss_closed_date] += point
                            except Exception as e:
                                points_dictionary[iss_closed_date] = point
    print(f"Total points for {sprint.name} is {total_sprint_points}")
    print(points_dictionary)


calculate_latest_sprint_points(all_sprints[0])

latest_issue = repo.get_issues()