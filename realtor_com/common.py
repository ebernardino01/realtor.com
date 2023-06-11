from multiprocessing import Process, Queue
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


# Execute spider using reactor and crawler runner
def run_spider_crawler(q, spider):
    try:
        runner = CrawlerRunner(settings=get_project_settings())
        deferred = runner.crawl(spider)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(None)
    except Exception as e:
        q.put(e)


# Wrapper to fork a separate process
def run_spider(spider):
    q = Queue()
    p = Process(target=run_spider_crawler, args=(q, spider))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
