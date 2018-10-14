import time
import json
import scrapy
import re
import itertools
import requests
from scrapy.utils.response import open_in_browser


from scrap_foot import settings

XPATH_SCRIPT = '//script[@type="text/javascript"]'
XPATH_STAGE_ID = '//link[@rel="canonical"]/@href'


class ScrapFoot(scrapy.Spider):
    urls = ['https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League',
            'https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1']
    name = "scrap_foot"
    results = {}
    host = 'www.whoscored.com'
    user_agents = ['Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
                   'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2',
                   'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
                   'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
                   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
                   ]
    cookie = 'visid_incap_774904=Hj74+iUvS5KwVToeERimNOo7ulsAAAAAQkIPAAAAAAD7GMKVfavmCX7XX3IXmg09; incap_ses_187_774904=1y4DKTc2Lg+AtfzvYVyYAgxaulsAAAAAoY7oL8AapfKgAqYv7WRqKw==; ct=FR; _ga=GA1.2.20340520.1538939406; _gid=GA1.2.1954726013.1538939406; _gat=1; _gat_subdomainTracker=1'
    players_url = 'https://www.whoscored.com/stageplayerstatfeed/?field=2&isAscending=false&orderBy=Rating&playerId=-1&stageId={}&teamId={}'
    stage_id = 0
    teams_id = {}

    def start_requests(self):
        print('in')
        current_url = ''
        for url in self.urls:
            current_url = url
            yield scrapy.Request(url, callback=self.render)

    def render(self, response):
        # time.sleep(1)
        # open_in_browser(response)
        # time.sleep(30)
        f = open('test3.html', 'w', encoding='utf8')
        f.write(response.xpath('//*').extract_first())
        f.close()
        scripts = response.xpath(XPATH_SCRIPT).extract()
        script = None
        model_last_mode = None
        l = 0
        i = 0
        for sc in scripts:
            if 'DataStore.prime(' in sc:
                # print(i, len(sc))
                i += 1
                if l < len(sc):
                    # print(l)
                    script = sc
                    l = len(sc)
            # if "$.ajaxSetup(" in sc:
            #     model_last_mode = sc.replace('<script type="text/javascript">', '').replace('</script>', '')

        # mlm_cleaned = model_last_mode.split('{')[-1].split('}')[0].split(':')[-1].strip(' ')
        # referer = response.url
        # print(mlm_cleaned)
        data_str = script.split('DataStore.prime(')[1].split(');')[0]
        data_list_str = data_str.split('[', 1)
        data_str = '[' + re.sub(r'"', r'\"', ''.join(data_list_str[1:])).replace("\'", '\"')
        self.stage_id = response.xpath(XPATH_STAGE_ID).extract_first().split('/')[-3]
        print(self.stage_id)
        f = open('test2.json', 'w')
        f.write(data_str)
        f.close()
        data = json.loads(data_str)
        # print(len(data))
        self.teams_id[self.stage_id] = []
        # iter = (i for i in range(100))
        for team in data:
            team_id, team_name = team[1:3]
            # print(team_id, team_name)
            if team_id not in self.results:
                self.results[team_id] = {team_name: {}}
            # time.sleep(1)
            self.teams_id[self.stage_id].append(team_id)

        if response.request.url == self.urls[-1]:
            j = 0
            for i in range(4):
                for stage_id in self.teams_id:
                    for alternate in range(2):
                        if alternate:
                            yield scrapy.Request(self.players_url.format(stage_id, self.teams_id[stage_id][i]),
                                                 headers={'cookie': self.cookie},
                                                 callback=self.test,
                                                 errback=self.test)
                        else:
                            yield scrapy.Request(url=self.urls[0])
                    print(j)
                    j += 1

    def get_player(self):
        print("a")
        print(self.teams_id)
        alternate = 0
        for i in range(4):
            for stage_id in self.teams_id:
                if alternate:
                    yield scrapy.Request(self.players_url.format(stage_id, self.teams_id[stage_id][i]),
                                         headers={'cookie': self.cookie,
                                                  'User-Agent': next(itertools.cycle(self.user_agents))},
                                         callback=self.test,
                                         errback=self.test)
                else:
                    yield scrapy.Request(url=self.urls[0])

    def get_json_players(self, team_id):
        print('a')
        print(self.players_url.format(self.stage_id, team_id))
        yield scrapy.Request(self.players_url.format(self.stage_id, team_id),
                             headers={'cookie': self.cookie},
                             callback=self.test,
                             errback=self.test)

    def test(self, response):
        print('azrzefrz')
        open_in_browser(response)
        # print('b:', response)
