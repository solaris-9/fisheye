# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import unicodecsv as csv
import time

class FisheyePipeline(object):
    def __init__(self):
        self.file = open('log/CPLANE_Code_Review_%s.txt' % time.strftime('%Y%m%d-%H%M%S', time.localtime()), 'wb')
        fields = (
            'ReviewID',
            'ReviewLink',
            'Title',
            'FID',
            'State',
            'CreateDate',
            'Author',
            'AuthorName',
            'Participant',
            'ParticipantName',
            'Role',
            'Comments',
            'TimeSpent',
            'ReviewerState',
            'Leader',
        )
        self.writer = csv.DictWriter(self.file, fieldnames=fields, dialect='excel-tab')
        self.writer.writeheader()
        
    def process_item(self, item, spider):
        try:
            self.writer.writerow(item)
        except Exception as e:
            self.logger.error(u'####UPI: %s dumping csv error!' % item['ReviewID'])
            self.logger.error(e)
        
        return item
