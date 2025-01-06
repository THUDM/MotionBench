from typing import Optional

from tqdm import tqdm
from pathlib import Path


def get_job_list(to_deal_path: str, max_total_jobs: Optional[int] = None, use_subdir: bool = False, pattern: str = "*"):
    if isinstance(to_deal_path,str):
        to_deal_directory = Path(to_deal_path)
    else:
        to_deal_directory = to_deal_path
    if not to_deal_directory.exists():
        print(f"{to_deal_path} not exists")
        exit()

    job_files = []

    if use_subdir:
        for sub_dir in tqdm(to_deal_directory.iterdir()):
            job_files.extend([str(file_path) for file_path in list(sub_dir.glob(pattern))])
            if max_total_jobs is not None and len(job_files) >= max_total_jobs:
                break
    else:
        job_files.extend([str(file_path) for file_path in list(to_deal_directory.glob(pattern))])

    if max_total_jobs is not None:
        job_files = job_files[:max_total_jobs]
    # print(f"Get total {len(job_files)} files")
    if not job_files:
        return []

    return job_files