import math
import random
from datetime import datetime
from datetime import timedelta

from pyclickup.models import Task
from pyclickup.utils.text import strfdelta


def parse_task(task: Task, custom_fields):
    """Convert task to a printable dictionary."""

    t = task._data
    t[
        "id_link"
    ] = f"<a href='{task.url}' target='_blank' rel='noopener noreferrer'>{task.id}</a>"
    t["creator"] = task.creator
    t["status"] = task.status.status
    if task.due_date:
        t["due_date"] = task.due_date.strftime("%b %d")
    else:
        t["due_date"] = ""
    if task.start_date:
        t["start_date"] = task.start_date
    else:
        t["start_date"] = ""
    t["date_created"] = task.date_created
    t["date_updated"] = task.date_updated
    t["date_closed"] = task.date_closed
    t["time_estimate"] = strfdelta(task.time_estimate)
    t["tags"] = " ".join([x.name for x in task.tags])
    # t["dependencies"] = task.dependencies
    t["waiting_on"] = " ".join(task.waiting_on)
    t["blocking"] = " ".join(task.blocking)
    t["custom_fields"] = {cf.name: cf.value for cf in task.custom_fields.values()}
    t["list"] = task.list["name"]
    if task.priority:
        t["priority"] = task.priority["priority"]
    else:
        t["priority"] = ""

    for field_name in custom_fields:
        t[field_name] = t["custom_fields"][field_name]
        if isinstance(t[field_name], list):
            t[field_name] = " ".join(t[field_name])

    t["score"] = score_task(task)
    t["client"] = task._client

    return t


def parse_tasks(task_list, custom_fields):
    """Convert an entire list of Task elements to list of string JSON-ed tasks."""
    return [parse_task(t, custom_fields) for t in task_list]


def score_task(task: Task):
    """Create a score for how much you 'should' do this task."""

    goal_rubric = {
        "agency": 7,
        "career": 2,
        "confidence": 3,
        "digital organized": 5,
        "money": 4,
        "organized": 8,
        "translogigi": 9,
        "relationships": 6,
        "systems": 10,
        "fun": 1,
    }
    priority_rubric = {"urgent": 8, "high": 5, "normal": 3, "low": 2}
    tags_rubric = {"next": 2, "timesensitive": 3}

    rubric = {
        "custom_fields": {"Goal": {"how": "sum", "rubric": goal_rubric}},
        "priority": {"how": "mul", "rubric": priority_rubric},
        "tags": {"how": "mul", "rubric": tags_rubric},
        "blocking": {"how": "mul", "rubric": 1},
    }
    cur_score = 0
    for field in rubric:
        cur_score = score_field(task, cur_score, field, rubric[field])
        # print("cur score", cur_score)

    return cur_score


def score_field(task: Task, cur_score: int, field_name: str, field_rubric):

    if field_name == "custom_fields":
        for cf, cf_rubric in field_rubric.items():
            if task.custom_fields[cf].value is None:
                continue
            values = list(task.custom_fields[cf].value)
            scores = [cf_rubric["rubric"].get(val, 0) for val in values]
            cur_score = update_score(cur_score, scores, cf_rubric["how"])

    elif field_name == "priority":
        if task.priority is None:
            return cur_score
        p_score = field_rubric["rubric"][task.priority["priority"]]
        cur_score = update_score(cur_score, p_score, field_rubric["how"])

    elif field_name == "tags":
        if task.tags is None:
            return cur_score
        values = [t.name for t in task.tags]
        scores = [field_rubric["rubric"].get(val, 0) for val in values]
        cur_score = update_score(cur_score, scores, field_rubric["how"])

    elif field_name == "blocking":
        if len(task.blocking) == 0:
            return cur_score
        multiplier = field_rubric["rubric"] * len(task.blocking)
        cur_score = update_score(cur_score, cur_score * multiplier, "sum")

    return cur_score


def update_score(cur_score: int, new_scores, how: str):

    if how == "sum":
        if isinstance(new_scores, int):
            return cur_score + new_scores
        return cur_score + sum(new_scores)

    if how == "mul":
        if isinstance(new_scores, int):
            if new_scores == 0:
                return cur_score
            return cur_score * new_scores
        return cur_score * math.prod([s for s in new_scores if s != 0])

    return cur_score


def filter_tasks(
    task_list, current_tasks=True, include_blocked=False, tags=None, not_tags=None
):

    if current_tasks:
        task_list = [
            task
            for task in task_list
            if task.due_date is None or task.due_date <= datetime.now()
        ]

    if not include_blocked:
        # only tasks that are not waiting on any other tasks
        task_list = [task for task in task_list if len(task.waiting_on) == 0]

    if tags:
        for tag in tags:
            task_list = [
                task for task in task_list if tag in [tag.name for tag in task.tags]
            ]

    if not_tags:
        for tag in tags:
            task_list = [
                task for task in task_list if tag not in [tag.name for tag in task.tags]
            ]

    return task_list


def sort_tasks(task_list, sort_by="score", due_first=True):
    """
    Need to parse before sort, so that scores are computed.
    """

    task_list.sort(key=lambda x: x[sort_by], reverse=True)

    if due_first:
        sorted_due_date = [t for t in task_list if t["due_date"]]
        sorted_due_date.extend([t for t in task_list if not t["due_date"]])
        task_list = sorted_due_date

    return task_list


def choose_task(task_list, how="should", recent_comments_ok=False):

    def check_recent_comments(task, window=timedelta(hours=1)):
        comments = task["client"].get_task_comments(task["id"])
        if len(comments) == 0:
            return False
        most_recent_time = max([c.date for c in comments])
        print("most_recent_time", most_recent_time)
        return datetime.now() - most_recent_time < window

    def pick_task(task_list, how):
        if how == "should":
            task_list = sort_tasks(task_list, sort_by="score", due_first=True)
            return task_list[0]
        elif how == "random":
            return random.choice(task_list)

    task = pick_task(task_list, how)
    while check_recent_comments(task):
        task_list.remove(task)
        task = pick_task(task_list, how)

    return task
