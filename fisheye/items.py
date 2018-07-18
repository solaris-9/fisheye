# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FisheyeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ReviewID = scrapy.Field()
    ReviewLink = scrapy.Field()
    Title = scrapy.Field() #(/detailedReviewData/name) 
    FID = scrapy.Field()
    State = scrapy.Field()
    CreateDate = scrapy.Field() #(/detailedReviewData/createDate) 
    Author = scrapy.Field() #(//author/userName) 
    AuthorName = scrapy.Field() # Full Name
    Participant = scrapy.Field()
    ParticipantName = scrapy.Field() # Full Name
    Role = scrapy.Field()
    Comments = scrapy.Field() #(//comments/published) 
    TimeSpent = scrapy.Field() #(//reviewer/timeSpent) 
    ReviewerState = scrapy.Field() #(//reviewer/completed)
    Leader = scrapy.Field()
    pass
