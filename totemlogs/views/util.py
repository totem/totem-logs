

def program_name_for(log_request):
    program_name = log_request.get('program-name')
    if program_name:
        return program_name
    meta_info = log_request['meta-info']
    git = meta_info['git']
    owner = git.get('owner') or '*'
    repo = git.get('repo') or '*'
    ref = git.get('ref') or '*'
    unit_no = meta_info.get('unit-no') or '*'
    unit_type = meta_info.get('unit-type') or 'app'
    version = meta_info.get('version') or '*'

    return '{owner}-{repo}-{ref}.{version}.{unit_no}.{unit_type}'.format(
        owner=owner, repo=repo, ref=ref, version=version, unit_no=unit_no,
        unit_type=unit_type)
