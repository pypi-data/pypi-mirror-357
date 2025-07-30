# from modelscope.hub.api import HubApi
# api = HubApi()
# api.login('aa9ce3b4-d037-4916-ba4c-d8379a34ad52')


# owner_name = 'LCM_group'
# dataset_name = 'LOOMBench'
# repo_id = f"{owner_name}/{dataset_name}"
# repo_type = "dataset"

# # 删除仓库
# api.delete_repo(repo_id=repo_id, repo_type=repo_type)
from modelscope.hub.api import HubApi
api = HubApi()
api.login('aa9ce3b4-d037-4916-ba4c-d8379a34ad52')
owner_name = 'LCM_group'
dataset_name = 'LOOMBench'
repo_id = f"{owner_name}/{dataset_name}"
repo_type = "dataset"
api.create_repo(repo_id=repo_id,repo_type=repo_type,exist_ok=True)

api.upload_folder(
    repo_id=repo_id,
    repo_type=repo_type,
    folder_path='/data/sora/lab/LOOM-Scape/data',
    commit_message='LOOMBench',
)