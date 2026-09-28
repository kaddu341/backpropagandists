"""Unit tests for _ext/resources.py: loading/validating the YAML and grouping."""

import pytest
import yaml
from sphinx.errors import ExtensionError

from resources import group, load

TOPICS = {"diffusion", "rl"}


def rec(**overrides):
    """A valid external record; keyword args override or (with None) delete fields."""
    r = {
        "id": "ho-2020-ddpm",
        "title": "Denoising Diffusion Probabilistic Models",
        "url": "https://arxiv.org/abs/2006.11239",
        "kind": "paper",
        "topics": ["diffusion"],
        "level": "foundational",
        "year": 2020,
    }
    r.update(overrides)
    return {k: v for k, v in r.items() if v is not None}


def write(tmp_path, records):
    path = tmp_path / "resources.yaml"
    path.write_text(yaml.safe_dump(records))
    return path


def test_load_returns_valid_records(tmp_path):
    records = [rec(), rec(id="ours", url=None, title=None, doc="notebooks/x", kind="notebook")]
    assert load(write(tmp_path, records), TOPICS) == records


@pytest.mark.parametrize(
    "bad",
    [
        rec(topics=["difusion"]),  # unknown topic
        rec(level="beginner"),  # unknown level
        rec(kind="podcast"),  # unknown kind
        rec(level=None),  # missing required field
        rec(levl="foundational"),  # unknown field (typo)
        rec(year="2020"),  # wrong type
        rec(doc="notebooks/x"),  # both url and doc
        rec(url=None),  # neither url nor doc
        rec(title=None),  # url record without a title
        rec(topics=[]),  # empty topics
    ],
)
def test_load_rejects_bad_record(tmp_path, bad):
    with pytest.raises(ExtensionError, match="ho-2020-ddpm"):
        load(write(tmp_path, [bad]), TOPICS)


def test_load_rejects_duplicate_id(tmp_path):
    with pytest.raises(ExtensionError, match="ho-2020-ddpm"):
        load(write(tmp_path, [rec(), rec()]), TOPICS)


def test_group_orders_ours_first_then_kinds_keeping_yaml_order():
    blog = rec(id="b", kind="blog")
    paper1, paper2 = rec(id="p1"), rec(id="p2")
    ours = rec(id="o", url=None, doc="notebooks/x", kind="notebook")
    assert group([blog, paper1, ours, paper2]) == [
        ("Our material", [ours]),
        ("Papers", [paper1, paper2]),
        ("Blog posts", [blog]),
    ]


def test_group_omits_empty_groups_and_filters_by_topic():
    diffusion, rl = rec(id="d"), rec(id="r", kind="video", topics=["rl"])
    assert group([diffusion, rl], topics=["rl"]) == [("Videos", [rl])]
