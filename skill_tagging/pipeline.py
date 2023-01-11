"""
Module that contains the openedx_filters pipeline steps.
"""
import logging
import random

import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep

logger = logging.getLogger(__name__)
DEFAULT_PROBABILITY = 0.5

def resource_string(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


class VerificationPipelineBase(PipelineStep):
    """
    Common functions for verification pipelines.
    """
    def fetch_related_skills(self, block):
        """Checks `has_verified_tags` and fetchs related skills."""
        has_verified_tags = getattr(block, "has_verified_tags", None)
        if has_verified_tags is None or has_verified_tags is True:
            return []
        fetch_tags = getattr(block, "fetch_skill_tags", None)
        if fetch_tags is None:
            return []
        tags = fetch_tags()
        return tags

    def should_run_filter(self):
        """Determines whether we should run filter and display form."""
        # random returns a number between 0 and 1 (inclusive).
        probability = getattr(settings, "SHOW_SKILL_VERIFICATION_PROBABILITY", DEFAULT_PROBABILITY)
        return random.random() < probability


class AddVerticalBlockSkillVerificationSection(VerificationPipelineBase):
    """
    Adds extra HTML to the fragment.

    Example Usage:

    .. code-block::

        "OPENEDX_FILTERS_CONFIG": {
            "org.openedx.learning.vertical_block.render.completed.v1": {
                "fail_sliently": false,
                "pipeline": [
                    "skill_tagging.pipeline.AddVerticalBlockSkillVerificationSection"
                ]
            }
        }
    """
    def run_filter(self, block, fragment, context, view):  # pylint: disable=arguments-differ
        """Pipeline Step implementing the Filter"""

        skills = self.fetch_related_skills(block)
        if not skills or not self.should_run_filter():
            return {"block": block, "fragment": fragment, "context": context, "view": view}
        verify_tags_url = block.runtime.handler_url(block, "verify_tags")
        html = resource_string("static/tagging.html")
        form = Template(resource_string("static/tags_form.html"))
        css = resource_string("static/tagging.css")
        js = resource_string("static/tagging.js")
        image = resource_string("static/brainstorming.svg")
        usage_id = block.scope_ids.usage_id
        data = {
            "block_type": usage_id.block_type,
            "block_id": usage_id.block_id,
            "skills": skills,
            "verify_tags_url": verify_tags_url,
            "image": image,
            "form": form,
            "thank_you_section": Template(resource_string("static/tags_thankyou.html")),
            "error_section": Template(resource_string("static/tags_error.html")),
        }
        template_str = f'<style type="text/css">{css}</style>{html}<script>{js}</script>'
        template = Template(template_str)
        context = Context(data)
        tags_div = template.render(context)
        fragment.content = f"{fragment.content}{tags_div}"
        return {"block": block, "fragment": fragment, "context": context, "view": view}


class AddVideoBlockSkillVerificationComponent(VerificationPipelineBase):
    """
    Adds verification component to video blocks.

    Example Usage:

    .. code-block::

        "OPENEDX_FILTERS_CONFIG": {
            "org.openedx.learning.vertical_block_child.render.started.v1": {
                "fail_sliently": false,
                "pipeline": [
                    "skill_tagging.pipeline.AddVideoBlockSkillVerificationComponent"
                ]
            }
        }
    """
    def run_filter(self, block, context):  # pylint: disable=arguments-differ
        """Pipeline Step implementing the Filter"""
        skills = self.fetch_related_skills(block)
        usage_id = block.scope_ids.usage_id
        if not skills or not self.should_run_filter() or usage_id.block_type != "video":
            return {"block": block, "context": context}
        verify_tags_url = block.runtime.handler_url(block, "verify_tags")
        data = {
            "block_type": usage_id.block_type,
            "block_id": usage_id.block_id,
            "skills": skills,
            "verify_tags_url": verify_tags_url,
            "tag_verification_template": Template(resource_string("static/tagging.html")),
            "form": Template(resource_string("static/tags_form.html")),
            "thank_you_section": Template(resource_string("static/tags_thankyou.html")),
            "error_section": Template(resource_string("static/tags_error.html")),
        }
        def wrapper(fn):
            def wrapped(_context):
                fragment = fn(_context)
                js = resource_string("static/tagging.js")
                css = resource_string("static/tagging.css")
                template = Template(resource_string("static/video_tagging.js"))
                context = Context(data)
                fragment.add_javascript(template.render(context))
                fragment.add_javascript(js)
                fragment.add_css(css)
                return fragment
            return wrapped
        block.student_view = wrapper(block.student_view)
        return {"block": block, "context": context}
