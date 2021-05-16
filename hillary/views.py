# /hillary/views.py
import os
from datetime import datetime
# from datetime import timedelta

from flask import Blueprint
from flask import render_template
from flask import url_for
from flask import redirect

from flask_dance.consumer import OAuth2ConsumerBlueprint

from pyclickup import ClickUp
from hillary.utils import parse_tasks, filter_tasks, sort_tasks, choose_task
from hillary.forms import GetTaskForm, TaskListForm

clickup_client_id = os.environ['CLICKUP_CLIENT_ID']
clickup_client_secret = os.environ['CLICKUP_CLIENT_SECRET']
redirect_url = "centagoj.herokuapp.com/login"
BASE_URL = "https://app.clickup.com"


clickup_blueprint = OAuth2ConsumerBlueprint(
    "clickup",
    __name__,
    client_id=clickup_client_id,
    client_secret=clickup_client_secret,
    redirect_url=redirect_url,
    base_url="https://app.clickup.com/",
    authorization_url="https://app.clickup.com/api",
    token_url="https://app.clickup.com/api/v2/oauth/token/",
    token_url_params={"include_client_id": True, "include_client_secret": True},
)
hillary_blueprint = Blueprint("hillary", __name__, template_folder="templates")


@hillary_blueprint.route("/", methods=["GET", "POST"])
def hillary():

    if not clickup_blueprint.session.authorized:
        return render_template("hillary.html", logged_in=False)
    clup = ClickUp(clickup_blueprint.session.access_token)

    form = GetTaskForm()

    if form.log_progress.data:
        prev_task_id = form.prev_task.data
        comment_text = f"Progress logged {datetime.now().isoformat()}"
        clup.add_comment_to_task(prev_task_id, comment_text=comment_text)

    if form.completed.data:
        prev_task_id = form.prev_task.data
        clup.complete_task(prev_task_id)

    if form.not_now.data:
        prev_task_id = form.prev_task.data
        comment_text = f"Postponing task at {datetime.now().isoformat()}"
        clup.add_comment_to_task(prev_task_id, comment_text=comment_text)
        clup.add_tag_to_task(prev_task_id, "postponed")

    # speed = form.speed.data
    # if not speed:
    #     speed = "a"
    # speed_lookup = {
    #     "a": None,
    #     "q": timedelta(minutes=16),
    #     "m": timedelta(minutes=31),
    #     "p": timedelta(minutes=121),
    # }
    # time_avail = speed_lookup[speed]

    # energy = form.energy_type.data
    # if not energy:
    #    energy = "a"
    # energy_lookup = {"a": None, "m": "mental", "p": "physical"}
    # energy_type = energy_lookup[energy]

    if form.random.data:
        choice_type = "random"
    elif form.tiny_task.data:
        choice_type = "tiny_task"
    elif form.should.data:
        choice_type = "should"
    elif form.easy.data:
        choice_type = "easy"
    else:
        choice_type = "should"

    include_tags = form.include_tags.data
    exclude_tags = form.exclude_tags.data

    task_list = clup.teams[0].spaces[0].get_tasks(statuses=['Open'], subtasks=True)

    # Now we filter the tasks a bunch
    task_list = filter_tasks(
        task_list,
        current_tasks=True,
        include_blocked=False,
        tags=include_tags,
        not_tags=exclude_tags
    )
    task_list = parse_tasks(task_list, custom_fields=["Energy", "Goal"])
    task = choose_task(task_list, how=choice_type, recent_comments_ok=False)

    if task:
        form.prev_task.data = task["id"]

    return render_template("hillary.html", logged_in=True, task=task, form=form)


@hillary_blueprint.route("/load-profile")
def load_profile():
    return redirect(url_for("hillary.hillary"))


@hillary_blueprint.route("/tasks", methods=["GET", "POST"])
def tasks():
    clup = ClickUp(clickup_blueprint.session.access_token)

    form = TaskListForm()
    include_tags = []
    exclude_tags = []
    energy_type = None
    if form.validate_on_submit():
        energy_type = form.energy_type.data
        if energy_type == "any":
            energy_type = None
        include_tags = form.include_tags.data
        exclude_tags = form.exclude_tags.data

    task_list = clup.teams[0].spaces[0].get_tasks(statuses=['Open'], subtasks=True)

    # Now we filter the tasks a bunch
    task_list = filter_tasks(
        task_list,
        current_tasks=True,
        include_blocked=False,
        tags=include_tags,
        not_tags=exclude_tags
    )
    custom_fields = ["Energy", "Goal"]
    task_list = parse_tasks(task_list, custom_fields=custom_fields)
    task_list = sort_tasks(task_list, sort_by="score", due_first=True)

    include_columns = [
        # "id",
        "id_link",
        "name",
        "due_date",
        # "list",
        # "status",
        # "priority",
        "time_estimate",
        # "waiting_on",
        "blocking",
        "Energy",
        "tags",
        "Goal",
        "score",
    ]

    return render_template(
        "tasks.html",
        logged_in=True,
        clickup=clup,
        task_list=task_list,
        columns=include_columns,
        form=form
    )
