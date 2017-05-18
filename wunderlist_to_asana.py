import argparse
import json
from operator import itemgetter

import asana


def get_workspace_id(in_asana_token, in_workspace_name):
    client = asana.Client.access_token(in_asana_token)
    workspace_ids = [
        workspace['id']
        for workspace in client.workspaces.find_all()
        if workspace['name'] == in_workspace_name
    ]
    result = workspace_ids[0] if len(workspace_ids) else None
    return result


def build_note_mapping(in_wunderlist_content):
    result = {}
    for note in in_wunderlist_content['data']['notes']:
        result[note['task_id']] = note['content']
    return result


def move_content(in_wunderlist_backup_file, in_asana_token, in_workspace_name):
    with open(in_wunderlist_backup_file) as wunderlist_in:
        wunderlist_content = json.load(wunderlist_in)

    workspace_id = get_workspace_id(in_asana_token, in_workspace_name)
    if not workspace_id:
        raise u'Couldn\'t find workspace "{}" in your Asana ' \
              u'(please note it\'s case-sensitive)'.format(in_workspace_name)

    client = asana.Client.access_token(in_asana_token)
    # Wunderlist list ID --> Asana project ID
    project_mapping = {}
    for project_index, project in enumerate(wunderlist_content['data']['lists']):
        print u'Processing Wunderlist list "{}" ({}/{})'.format(
            project['title'],
            project_index + 1,
            len(wunderlist_content['data']['lists'])
        )
        result = client.projects.create_in_workspace(
            workspace_id,
            {'name': project['title']}
        )
        project_mapping[project['id']] = result['id']

    # Wunderlist task ID --> note content
    note_mapping = build_note_mapping(wunderlist_content)
    # Wunderlist task ID --> Asana task ID
    task_mapping = {}
    # Wunderlist task ID --> Wunderlist list ID
    task_project_mapping = {}

    for task_index, task in enumerate(sorted(
        wunderlist_content['data']['tasks'],
        key=itemgetter('created_at')
    )):
        print u'Processing Wunderlist task "{}" ({}/{})'.format(
            task['title'],
            task_index + 1,
            len(wunderlist_content['data']['tasks'])
        )
        task_json = {
            'name': task['title'],
            'projects': [project_mapping[task['list_id']]],
            'completed': task['completed'],
        }
        if 'due_date' in task:
            task_json['due_on'] = task['due_date']
        if task['id'] in note_mapping:
            task_json['notes'] = note_mapping[task['id']]
        result = client.tasks.create_in_workspace(
            workspace_id,
            task_json
        )
        task_mapping[task['id']] = result['id']
        task_project_mapping[task['id']] = task['list_id']

    for subtask_id, subtask in enumerate(sorted(
        wunderlist_content['data']['subtasks'],
        key=itemgetter('created_at')
    )):
        print u'Processing Wunderlist subtask "{}" ({}/{})'.format(
            subtask['title'],
            subtask_id + 1,
            len(wunderlist_content['data']['subtasks'])
        )
        subtask_json = {
            'name': subtask['title'],
            'projects': [task_project_mapping[subtask['task_id']]],
            'completed': subtask['completed'],
            'parent': task_mapping[subtask['task_id']]
        }
        if 'due_date' in subtask:
            subtask_json['due_on'] = subtask['due_date']
        client.tasks.create_in_workspace(workspace_id, subtask_json)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Export your Wunderlist content to Asana'
    )
    parser.add_argument(
        'wunderlist_backup',
        type=str,
        help='Wunderlist backup file (json)'
    )
    parser.add_argument(
        'asana_token',
        type=str,
        help='Asana personal access token'
    )
    parser.add_argument('workspace_name', type=str, help='Asana workspace name')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    move_content(args.wunderlist_backup, args.asana_token, args.workspace_name)
