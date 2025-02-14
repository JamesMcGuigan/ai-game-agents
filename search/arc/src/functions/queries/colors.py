from fastcache import clru_cache

from src.functions.queries.grid import grid_unique_colors
from src.functions.queries.ratio import is_task_shape_ratio_consistent



@clru_cache()
def task_is_singlecolor(task) -> bool:
    if not is_task_shape_ratio_consistent(task): return False
    return all([ len(grid_unique_colors(spec['output'])) == 1 for spec in task['train'] ])

