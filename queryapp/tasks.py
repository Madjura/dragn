from celery import shared_task

from allsteps.allsteps import all_steps

@shared_task
def all_steps_task(texts, language, alias):
    all_steps(texts, language=language, alias=alias, task=all_steps_task)
