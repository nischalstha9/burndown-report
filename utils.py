from datetime import datetime, timedelta
import re
import boto3
from github.Project import Project
from github.Repository import Repository
import pandas as pd
from botocore.client import Config

point_match_regex = re.compile(r'([pP]oint)s?[\s*\-_](\d+)')

def calculate_latest_sprint_points(sprint:Project, repo:Repository,point_match_regex=point_match_regex):
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
    return {"points":points_dictionary, "total_sprint_points":total_sprint_points}


def get_optimized_df_for_plot(points): # here points is return value from above calculate_latest_sprint_points function
    points_df = pd.DataFrame.from_dict(points['points'], orient="index", columns=['Points_Completed_on_Date'])
    points_df['Total_Points_Completed'] = points_df['Points_Completed_on_Date'].cumsum()


    total = points['total_sprint_points'] #total spr points
    no_days = int(points_df.shape[0]) #total days 

    avg =total/no_days
    points_df['index'] = range(1,1+len(points_df))

    def get_required_burn(index):
        point = int(avg*index)
        return (point if point > 0 else 1)

    points_df['Required_Burn'] = [get_required_burn(x) for x in points_df['index']]

    # points_df.drop('Total_Points_Completed', axis=1, inplace=True)
    # points_df.drop('Points_Completed_on_Date', axis=1, inplace=True)
    points_df.drop('index', axis=1, inplace=True)
    return points_df

def upload_to_s3_and_get_url(key,secret,region, bucket_name, repo_name):
    s3 = boto3.resource('s3',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name=region,
        config=Config(signature_version='s3v4')
        )
    data = open('output.jpg', 'rb')
    file_name = f'output{datetime.now().timestamp()}.jpg'
    file_path = f"naxa-test/projects/{repo_name}/{file_name}"
    obj = s3.Bucket(bucket_name).upload_file("output.jpg", file_path, ExtraArgs={
            "ContentType": "image/jpeg"
        })
    url = f"https://{bucket_name}.s3.amazonaws.com/{file_path}"
    return url