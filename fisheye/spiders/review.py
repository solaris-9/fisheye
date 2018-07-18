# -*- coding: utf-8 -*-
import scrapy
from fisheye.items import FisheyeItem
from fisheye.credential import credentials
from fisheye.settings import ID_MAX, ID_MIN
from fisheye.fid import fids
from fisheye.names import csl2leader
from lxml import etree
import re
import math

class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["fisheye4.int.net.nokia.com"]
    start_urls = ['https://fisheye4.int.net.nokia.com/rest-service/auth-v1/login?userName=%s&password=%s' % (credentials[0], credentials[1])]
    review_urls = [
        'https://fisheye4.int.net.nokia.com/rest-service/reviews-v1/CPLANE-LTE-TRUNK-%d/details' % 
                i for i in range(ID_MIN, ID_MAX)
    ]

    def parse(self, response):
        if b'error' in response.body:
            self.logger.error('!!! Login Failed !!!')
            return
        else:
            self.logger.info('!!! Login Pass !!!')
        if self.settings.getbool('DEBUG_MODE'):
            self.logger.info(self.review_urls)
        for u in self.review_urls:
            if self.settings.getbool('DEBUG_MODE'):
                self.logger.info('Crawling: %s' % u)
            yield scrapy.Request(u, self.parse_review)

    def parse_review(self, response):
        l_state = ''.join(response.xpath('/detailedReviewData/state/text()').extract())
        ### return for not valid state
        if l_state in ['Dead', 'Draft']:
            return
            
        ### return for not valid FID in the title
        l_title = ''.join(response.xpath('/detailedReviewData/name/text()').extract())
        if re.search(r'SANDBOX|OBSOLETE|DOJO', l_title.upper()):
            return

        ### general info: ID/URL/Title/FID/State/createDate/Author
        p_url = response.url.split('/') ### temp var for url
        l_id = p_url[-2]
        if self.settings.getbool('DEBUG_MODE'):
            self.logger.info('ID: %s' % l_id)
        ###l_title = ''.join(response.xpath('/detailedReviewData/name/text()').extract())
        ### TODO: to determine if a good FID is included in the review
        l_fid = ''
        res = re.search(r'LTE\d+|LBT\d+|CRL\d+|PR\d+|CAS-\d+-\w+', 
                            l_title.upper()
                         )
        if res:
            l_fid = res.group()
            self.logger.info('1======== Searched FID: %s' % l_fid)
            
        ### replace the FID with offline lists collected for escaped titles
        if l_id in fids.keys():
            l_fid = fids[l_id]
            self.logger.info('2======== Escaped FID: %s' % l_fid)

        if l_fid.upper() in ['SANDBOX', 'OBSOLETE']:
            return
        
        self.logger.info('3======== Final FID: %s' % l_fid)
        l_url = '%s//%s/cru/%s' % (p_url[0], p_url[2], p_url[-2])
            
        l_createDate = ''.join(response.xpath('/detailedReviewData/createDate/text()').extract())
        l_author = ''.join(response.xpath('//author/userName/text()').extract())
        l_authorName = ''.join(response.xpath('//author/displayName/text()').extract())
            
        ### put the leader of the author
        l_leader = ''
        if l_author in csl2leader.keys():
            l_leader = csl2leader[l_author]
            
        if l_leader in ['WRO', 'HZ', 'HE Bin C']:
            return

        ### number of comments for every participants, including author itself.
        d = {
                response.xpath('//comments/user/text()').extract()[i] : 
                response.xpath('//comments/published/text()').extract()[i] 
                for i in range(len(response.xpath('//stats/comments')))
        }
            
        p_author_comment_number = '0'
        if l_author in d.keys():
            p_author_comment_number = d[l_author]
        
        yield FisheyeItem( ReviewID = l_id, 
                           ReviewLink = l_url, 
                           Title = l_title, 
                           FID = l_fid, 
                           State = l_state, 
                           CreateDate = l_createDate, 
                           Author = l_author, 
                           AuthorName = l_authorName,
                           Participant = l_author, 
                           ParticipantName = l_authorName,
                           Role =  'Author', 
                           Comments = p_author_comment_number, 
                           TimeSpent = '0', 
                           ReviewerState = '',
                           Leader = l_leader,
                        )
        
        ### Crawling reviewer's metrics
        for s in response.xpath('//reviewers/reviewer').extract():
            ll_name = ''.join(etree.fromstring(s).xpath('//userName/text()'))
            ll_full_name = ''.join(etree.fromstring(s).xpath('//displayName/text()'))
            self.logger.info('Reviewer Name : %s' % ll_name)
            ll_reviewer_comment_number = '0'
            if ll_name in d.keys():
                ll_reviewer_comment_number = d[ll_name]
            ll_time = ''.join(etree.fromstring(s).xpath('//timeSpent/text()'))
            if ll_time == '':
                ll_time = '0'
            ll_state = ''.join(etree.fromstring(s).xpath('//completed/text()'))
            yield FisheyeItem( ReviewID = l_id, 
                   ReviewLink = l_url, 
                   Title = l_title, 
                   FID = l_fid, 
                   State = l_state, 
                   CreateDate = l_createDate, 
                   Author = l_author, 
                   AuthorName = l_authorName,
                   Participant = ll_name, 
                   ParticipantName = ll_full_name,
                   Role =  'Reviewer', 
                   Comments = ll_reviewer_comment_number, 
                   TimeSpent = int(ll_time) / 1000 / 60 / 60,   ### time in hours
                   ReviewerState = ll_state,
                   Leader = l_leader,
            )

        return

'''        
        for p in response.xpath('//reviewers/reviewer'):
            fish = FisheyeItem()
            p_url = response.url.split('/')
            fish['ReviewID'] = p_url[-2]
            if self.settings.getbool('DEBUG_MODE'):
                self.logger.info('ID: %s' % fish['ReviewID'])
            fish['ReviewLink'] = '%s//%s/cru/%s' % (p_url[0], p_url[2], p_url[-2])
            if len(response.xpath('/detailedReviewData/name/text()').extract()) > 0:
                fish['Title'] = ''.join(response.xpath('/detailedReviewData/name/text()').extract())
            else:
                fish['Title'] = ''
            fish['State'] = response.xpath('/detailedReviewData/state/text()').extract()[0]
            fish['CreateDate'] = response.xpath('/detailedReviewData/createDate/text()').extract()[0]
            fish['Author'] = response.xpath('//author/userName/text()').extract()[0]
            fish['Reviewer'] = p.xpath('//reviewer/userName/text()').extract()[0]
            if len(response.xpath('//reviewer/timeSpent/text()').extract()) > 0:
                fish['TimeSpent'] = p.xpath('//reviewer/timeSpent/text()').extract()[0]
            else:
                fish['TimeSpent'] = '0'
            fish['ReviewerState'] = p.xpath('//reviewer/completed/text()').extract()[0]
            if fish['Reviewer'] in d.keys():
                fish['Comments'] = d[fish['Reviewer']]
            else:
                fish['Comments'] = '0'
            self.logger.info(fish)
            yield fish
'''        