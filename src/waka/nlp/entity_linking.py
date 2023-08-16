import abc
from typing import List

import requests

from waka.nlp.kg import Entity
from waka.nlp.text_processor import TextProcessor


class EntityLinker(TextProcessor[List[Entity], List[Entity]], metaclass=abc.ABCMeta):
    pass


class ElasticEntityLinker(EntityLinker):
    def __init__(self):
        self.search_endpoint = "https://metareal-kb.web.webis.de/api/v1/kb/entity/search"

    def process(self, in_data: List[Entity]) -> List[Entity]:
        cache = {}
        linked_entities = []

        headers = {"accept": "application/json"}

        for entity in in_data:
            retrieved_entities = []

            if entity.text in cache:
                retrieved_entities.extend(cache[entity.text])
            else:
                request_params = {"q": entity.text}

                response = requests.get(self.search_endpoint, params=request_params, headers=headers)
                body = response.json()

                if body["status"] == "success":
                    for e in body["data"]:
                        retrieved_entities.append(e)

                    cache[entity.text] = retrieved_entities

                for e in retrieved_entities:
                    linked_entities.append(Entity(
                        url=e["id"],
                        start_idx=entity.start_idx,
                        end_idx=entity.end_idx,
                        text=entity.text,
                        label=e["label"],
                        score=e["score"],
                        e_type=entity.type))

        return linked_entities
