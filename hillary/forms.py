# hillary/tasks/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import HiddenField, SelectField
from wtforms import SelectMultipleField
from wtforms import widgets


tags_list = ["@couch", "@myroom", "babysteps"]


class GetTaskForm(FlaskForm):
    time_avail = StringField("How much time do you have?")
    random = SubmitField("Random")
    should = SubmitField("Should")
    easy = SubmitField("Easy")
    tiny_task = SubmitField("Tiny Task")
    log_progress = SubmitField("Log Progress")
    not_now = SubmitField("Not Now")
    completed = SubmitField("Completed")

    include_tags = SelectMultipleField(
        "Include Tags",
        choices=[(t, t) for t in tags_list],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
    exclude_tags = SelectMultipleField(
        "Exclude Tags",
        choices=[(t, t) for t in tags_list],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )

    speed = SelectField(
        choices=[("a", "any"), ("q", "quick"), ("m", "medium"), ("p", "project")]
    )
    energy_type = SelectField(
        choices=[("a", "any"), ("m", "mental"), ("p", "physical")]
    )
    prev_task = HiddenField()


class TaskListForm(FlaskForm):
    next_actions = SubmitField("Update List")

    energy_type = SelectField(
        choices=[("any", "any"), ("mental", "mental"), ("physical", "physical")]
    )

    include_tags = SelectMultipleField(
        "Include Tags",
        choices=[(t, t) for t in tags_list],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
    exclude_tags = SelectMultipleField(
        "Exclude Tags",
        choices=[(t, t) for t in tags_list],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
