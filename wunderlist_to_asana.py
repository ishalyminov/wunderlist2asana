import argparse
import json

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
        raise 'Couldn\'t find workspace "{}" in your Asana (please note it\'s case-sensitive)'.format(in_workspace_name)

    client = asana.Client.access_token(in_asana_token)
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

    note_mapping = build_note_mapping(wunderlist_content)

    for task_id, task in enumerate(wunderlist_content['data']['tasks']):
        print u'Processing Wunderlist task "{}" ({}/{})'.format(task['title'], task_id + 1, len(wunderlist_content['data']['tasks']))
        task_json = {
            'name': task['title'],
            'projects': [project_mapping[task['list_id']]],
            'completed': task['completed'],
        }
        if 'due_date' in task:
            task_json['due_on'] = task['due_date']
        if task['id'] in note_mapping:
            task_json['notes'] = note_mapping[task['id']]
        client.tasks.create_in_workspace(
            workspace_id,
            task_json
        )


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