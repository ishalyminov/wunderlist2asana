import argparse
import json
from operator import itemgetter

import asana


def get_workspace_id(in_asana_token, in_workspace_name):
    client = asana.Client.access_token(in_asana_token)
    workspace_ids = [
        workspace['gid']
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
    with open(in_wunderlist_backup_file, encoding='utf-8-sig') as wunderlist_in:
        wunderlist_content = json.load(wunderlist_in)

    workspace_id = get_workspace_id(in_asana_token, in_workspace_name)
    if not workspace_id:
        raise u'Couldn\'t find workspace "{}" in your Asana ' \
              u'(please note it\'s case-sensitive)'.format(in_workspace_name)

    client = asana.Client.access_token(in_asana_token)
    # Wunderlist list ID --> Asana project ID

    for project_index, project in enumerate(wunderlist_content):
        print (u'Processing Wunderlist list "{}" ({}/{})'.format(
            project['title'],
            project_index + 1,
            len(wunderlist_content)
        ))
        result = client.projects.create_in_workspace(
            workspace_id,
            {'name': project['title']}
        )
        asana_project_id = result['gid']

        for task_index, task in enumerate(sorted(
            project['tasks'],
            key=itemgetter('createdAt')
        )):
            print (u'Processing the task "{}" ({}/{})'.format(
                task['title'],
                task_index + 1,
                len(project['tasks'])
            ))
            task_json = {
                'name': task['title'],
                'projects': [asana_project_id],
                'completed': task['completed'],
            }
            if 'dueDate' in task:
                task_json['due_on'] = task['dueDate']
            if task['notes']:
                task_json['notes'] = '\n'.join([note['content'] for note in task['notes']])
            result = client.tasks.create_in_workspace(
                workspace_id,
                task_json
            )
            asana_task_id = result['gid']

            for subtask_id, subtask in enumerate(sorted(
                task['subtasks'],
                key=itemgetter('createdAt')
            )):
                print (u'Processing Wunderlist subtask "{}" ({}/{})'.format(
                    subtask['title'],
                    subtask_id + 1,
                    len(task['subtasks'])
                ))
                subtask_json = {
                    'name': subtask['title'],
                    'completed': subtask['completed'],
                    'parent': asana_task_id
                }
                if 'dueDate' in subtask:
                    subtask_json['due_on'] = subtask['dueDate']
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
