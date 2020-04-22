# -*- coding: utf-8 -*-
from fimfic.items import FimficStory
import os
import json


class FimficPipeline(object):
    archive_path = None
    indices = {}

    def open_spider(self, spider):
        self.archive_path = spider.archive_path

    def process_item(self, item, spider):
        if not isinstance(item, FimficStory):
            return item
        story_path_dir = os.path.join(
            self.archive_path,
            item['shelf_user_id'],
            item['shelf_id'],
        )
        story_path = os.path.join(
            story_path_dir,
            item['filename']
        )
        os.makedirs(story_path_dir, exist_ok=True)
        with open(story_path, 'w', encoding='utf-8') as f:
            f.write(item['body'])
        index_path = os.path.join(
            self.archive_path,
            item['shelf_user_id'],
            'index.jsonl'
        )
        if index_path not in self.indices:
            self.indices[index_path] = []
        self.indices[index_path].append(
            json.dumps({
                'story_name': item['name'],
                'story_link': item['link'],
                'story_dl': item['dl_link'],
                'rel_path': os.path.join(item['shelf_id'], item['filename'])
            }, ensure_ascii=False)
        )

    def close_spider(self, spider):
        for path in self.indices:
            with open(path, 'w', encoding='utf-8') as f:
                for record in sorted(self.indices[path]):
                    f.write(record+'\n')
