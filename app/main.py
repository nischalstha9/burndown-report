import re
from utils import calculate_latest_sprint_points, get_optimized_df_for_plot, upload_to_s3_and_get_url
from dotenv import load_dotenv
from github import Github
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


load_dotenv()

KEY = os.getenv("KEY")
SECRET = os.getenv("SECRET")
bucket_name = os.getenv("BUCKET_NAME")
region = os.getenv("REGION")
CLOSED_ISSUE_NUMBER=int(os.getenv("CLOSED_ISSUE_NUMBER"))
token = os.getenv("GH_PAT")

def main():
    repo_name = "naxa-developers/cycle-app-greenway-backend"

    # point_match_regex = re.compile(r'(\bpoints?\b)[\s+-_](\d+)')
    point_match_regex = re.compile(r'([pP]oint)s?[\s*\-_](\d+)')


    g = Github(token)
    repo = g.get_repo(repo_name)

    all_sprints = repo.get_projects().reversed #THis Can be looped for every active sprint
    sprint = all_sprints[0]

    points = calculate_latest_sprint_points(sprint, repo)

    points_df = get_optimized_df_for_plot(points)


    fig = points_df.plot()
    fig.yaxis.set_major_locator(MaxNLocator(integer=True)) # to force y axis to use integer
    plt.xticks(rotation=90)
    fig.set_xlabel('Dates')
    fig.set_ylabel('Points')
    plot = fig.get_figure()
    image = plot.savefig('output.jpg', format='jpg', bbox_inches="tight") #main image


    image_url = upload_to_s3_and_get_url(KEY, SECRET, region, bucket_name, repo_name)

    issue = repo.get_issue(CLOSED_ISSUE_NUMBER)
    cmnt = f"Closing this issue affected project burndown as: \n ![]({image_url})"
    issue.create_comment(body= cmnt)


if __name__ == "__main__":
    main()