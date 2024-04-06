from psaw import PushshiftAPI                               #Importing wrapper library for reddit(Pushshift)

api = PushshiftAPI() 

class PushshiftFunc:
    def data_prep_posts(self, subreddit, start_time, end_time, filters, limit):
        if(len(filters) == 0):
            filters = ['id', 'author', 'created_utc',
                    'domain', 'url',
                    'title', 'num_comments']                 #We set by default some columns that will be useful for data analysis

        posts = list(api.search_submissions(
            subreddit=subreddit,                                #We set the subreddit we want to audit
            after=start_time,                                   #Start date
            before=end_time,                                    #End date
            filter=filters,                                     #Column names we want to get from reddit
            limit=limit))                                       #Max number of posts we wanto to recieve

        return posts                                            #Return dataframe 

    def data_prep_comments(self, term, start_time, end_time, filters, limit):
        if (len(filters) == 0):
            filters = ['id', 'author', 'created_utc',
                    'body', 'permalink', 'subreddit']        #We set by default some columns that will be useful for data analysis

        comments = list(api.search_comments(
            q=term,                                             #We set the subreddit we want to audit
            after=start_time,                                   #Start date
            before=end_time,                                    #End date
            filter=filters,                                     #Column names we want to get from reddit
            limit=limit))                                       #Max number of comments we wanto to recieve

        return comments                                         #Return dataframe 