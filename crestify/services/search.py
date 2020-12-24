# -*- coding: utf-8 -*-
from crestify import elastic_search_engine
from elasticsearch_dsl import Search


def create_index(index, model):
    if not elastic_search_engine:
        return
    elastic_search_engine.indices.create(index=index.lower(), ignore=400)


def add_to_index(index, model):
    if not elastic_search_engine:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    elastic_search_engine.index(index=index.lower(), id=model.id, body=payload)


def remove_from_index(index, model):
    if not elastic_search_engine:
        return
    elastic_search_engine.delete(index=index.lower(), id=model.id)


def query_index(index, query, page, per_page, filters=None, fields=None):
    if not elastic_search_engine:
        return [], 0
    search = (
        Search(using=elastic_search_engine, index=index.lower())
        .query(
            "query_string",
            default_operator="AND",
            query=query,
            lenient=True,
            fields=fields or ["*"],
        )
        .highlight_options(order="score")
        .highlight("title")
        .highlight("description")
        .highlight("full_text")[((page - 1) * per_page) : per_page]
    )
    if filters:
        for __filter in filters:
            search = search.filter("term", **{__filter["key"]: __filter["value"]})
    search = search.execute()
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]
