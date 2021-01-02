import pandas as pd
from tqdm import tqdm
from os import listdir
from pymongo import MongoClient
from datetime import datetime, timedelta

from source.crypto_scraper_csv import interval_to_scrape
from source.utils import data_scraper


class Database(object):
    """
    Access to different databases where daily collections are stored containing tick data from the orderbook
    and for a specified cryptocurrency.

    # Execute in your terminal: brew services restart mongodb-community

    """

    COLLECTION = None

    def __init__(self):
        """
        Connection to your localhost database and first function execution.
        """
        self._client = MongoClient('localhost', 27017)
        self.databaseName = self.select_database()

    def select_database(self):
        """
        Shows a list of your existing databases and allows you to create a new one in case you need it.

        Arguments:
        ----------
        ()

        Returns:
        --------
            Access to the written database.

        """

        print(f'Available databases: {sorted(self._client.list_database_names())}.')
        print('Please, write the one you are interested in:')

        self.db_name = str(input())
        if self.db_name in self._client.list_database_names():
            print(f'Connecting to {self.db_name}...')
            return self._client[self.db_name]

        else:
            print(f'Sorry, we do not have any database named: {self.db_name}. '
                  f'Write "yes" if you would like to create a new one named {self.db_name}. '
                  f'Otherwise, restart the DB and try again.')

            new_db = str(input()).lower()
            if new_db == 'yes':
                print(f'Creating and connecting to {self.db_name}...')
                return self._client[self.db_name]

    def select_collection(self):
        """
        Shows a list of your existing databases and allows you to create a new one in case you need it.

        Arguments:
        ----------
        ()

        Returns:
        --------
            Access to the written database.

        """
        available_data = self.show_available_collections()
        if available_data:
            print(f'These are current available collections inside your "{self.db_name}" database:', available_data)
            print('Select the one you are willing to connect: ')
            self.collection_name = str(input()).upper()
            print(f"You've been connected into your {self.db_name} database and logged into {self.collection_name} data")
            return self.databaseName[self.collection_name]

        else:
            # Finding out the available cryptocurrencies
            interval = (str(datetime.today() - timedelta(days=1))).split(' ')[0].replace('-', '')
            cryptos = pd.read_csv(f'https://s3-eu-west-1.amazonaws.com/public-testnet.bitmex.com/data/trade/'
                                  f'{interval}.csv.gz')

            print('You do not have any collection in this database yet. \nChoose from the list below:\n',
                  cryptos['symbol'].unique())

            # Selecting the name of the collection we are going to generate inside our new db
            self.collection_name = str(input()).upper()
            self.databaseName.create_collection(str(self.collection_name))
            print(f"You've been connected into your {self.db_name} database and logged into {self.collection_name} data")
            return self.databaseName[self.collection_name]

    def remove_collection(self, collection=''):
        """
        Shows the available collections and asks to delete any collections we are no longer interested in storing
        into our database.

        Arguments:
        ----------
        ()

        Returns:
        --------
        ()

        """
        if collection:
            self.databaseName[collection].drop()
            print(f'The database {collection} has been deleted successfully!')

        else:
            print(f'Available collections for this database: {self.show_available_collections()}')
            print('Please, select the one you are willing to drop: or write "all" if you want to drop them all')
            collections = str(input())

            if collections == 'all':
                print('We are preparing all available collections: ', collections)
                for collection in tqdm(self.show_available_collections()):
                    self.databaseName[collection].drop()

            elif len(collections) > 1:
                collections_date = collections.replace(',', '').replace("'", '').split(' ')
                print("We are deleting the collections you've selected: ", collections_date)
                for collection in tqdm(sorted(collections_date)):
                    self.databaseName[collection].drop()

            else:
                print("We are deleting the collection you've selected: ", collections)
                self.databaseName[collections].drop()

    def show_available_collections(self):
        available_data = sorted(self.databaseName.list_collection_names())
        return available_data


    def populate_collection(self, selected_collection):
        """
        Shows a list of available collections we can find inside the selected database and asks if we are interested
        in updating our database with new data.

        Arguments:
        ----------
        ()
        Returns:
        --------
            Collections we are willing to include into our database.

        """
        # print('---~', self._client[self.db_name].selected_collection.find({}))
        # data = self._client[self.db_name].selected_collection.find({})
        # Database.COLLECTION = self._client[self.databaseName]
        # available_data = sorted(Database.selected_collection.list_collection_names())



        print("\nIf you'd like to collect all the available data, write: 'ORIGIN'.")
        # print("If you'd like to update your database, write: 'UPDATE'.")
        # print("If you'd like to update since the last available record in the database, write 'LAST'.")
        # print("To update from a specific period, write the date in this format: 'YYYYMMDD'.")
        # print("To update ONLY a CONCRETE period, write: CONCRETE.")


        last_available_day = (str(datetime.today() - timedelta(days=1))).split(' ')[0].replace('-', '')
        interval = str(input()).lower()
        if interval == 'origin':
            print(f'You have chosen ORIGIN, so we are going to collect data since the very beginning: 20141122.')

            # Generating a list containing the dates we are going to scrape & getting the data
            interval_to_update = sorted(interval_to_scrape(day1='20200101', max_date=''))
            for date in tqdm(interval_to_update[:-1]):
                print(f'{date} is being processed...')
                data = data_scraper(date, self.collection_name)
                self.update_database(date, data, selected_collection)
            # Inserting the data into our collection






    # interval = str(input()).lower()
        # if interval == 'last':
        #     try:
        #         last_val = data[-1]
        #         print('You have chosen LAST, so we will update your general csv file since:', last_val)
        #         to_update = [x for x in available_data if x >= last_val]
        #         return sorted(to_update), ''
        #     except:
        #         print('You do not have any record yet. We are going to update since the very beginning...')
        #         to_update = [x for x in available_data if x >= '20141121']
        #         return sorted(to_update), ''
        #
        # elif interval == 'origin':
        #     print(f'You have chosen ORIGIN, so we are going to collect data since the very beginning.')
        #     to_update = [x for x in available_data if x >= '20141121']
        #     return sorted(to_update), ''
        #
        # elif interval == 'concrete':
        #     print('Write the period you want to collect in the following format: "YYYYMMDD" ')
        #     interval = str(input())
        #     if interval in available_data:
        #         print(f'The interval: {interval} is available')
        #         return [interval], ''
        #     else:
        #         print('Sorry but we do not have this collection in our database.')
        #
        # elif interval in available_data:
        #     print(f'The interval: {interval} is available')
        #     to_update = [x for x in available_data if x >= interval]
        #     return sorted(to_update), ''
        #
        # elif interval == 'update':
        #     file = listdir('data.nosync/')
        #     datatypes = []
        #     for f in file:
        #         if f not in datatypes and f.endswith(".csv"):
        #             datatypes.append(f.split('_')[0].replace('.', '').replace('readmetxt', '').replace('DS', ''))
        #     print('These are your existing timeframes/datatype files: ', set(datatypes))
        #     print("Which is the timeframe/datatype you'd like to update [XMin, XH, D, W, M, RAW...]")
        #
        #     frequency = str(input()).replace(' ', '')
        #     if frequency != 'RAW':
        #         try:
        #             all_data = pd.read_csv(f'data.nosync/{frequency}_general.csv').timestamp.iloc[-1].split(' ')[0]\
        #                         .replace('-', '')
        #             print('You have chosen UPDATE, so we will update since:', all_data)
        #             to_update = [x for x in available_data if x >= all_data]
        #             return sorted(to_update), frequency
        #
        #         except:
        #             all_data = pd.read_csv(f'data.nosync/{frequency}_general.csv').Timestamp.iloc[-1].split(' ')[0]\
        #                         .replace('-', '')
        #             print('You have chosen UPDATE, so we will update since:', all_data)
        #             to_update = [x for x in available_data if x >= all_data]
        #             return sorted(to_update), frequency
        #     else:
        #         raws = [f.replace('RAW_', '').replace('.csv', '') for f in file if f.startswith('RAW_')]
        #         print('You have chosen UPDATE, so we will update since:', sorted(raws)[-1])
        #         to_update = [x for x in available_data if x >= sorted(raws)[-1]]
        #         return sorted(to_update), frequency
        #
        # else:
        #     print('There is no data for this date')

    @staticmethod
    def update_database(date, available_data, db_collection):
        """
        Updates our database with new scraped data.

        Arguments:
        ----------
        date {[str]} -- Date to include in our database.
        available_data -- Scraped data we will convert into a dict to store into our mongo database.

        Returns:
        --------
            {[Collection]}
                A new collection into our database for the specified date and currency.

        """
        available_data = available_data.to_dict(orient='records')
        # print('aaahhhssss', available_data)
        try:
            db_collection.insert_many(available_data)
            print(f'Your new collection {date}, has been created successfully')

        except:
            print(f'There is no available data for the date: ', date)

    def dates_double_check(self, scraped_interval):
        """
        Checks for empty collections.

        Arguments:
        ----------
        scraped_interval {[list]} -- Dates we are going to check.

        Returns:
        --------
            {[list]}
                With collection names we should double check.

        """
        print('We are collecting empty datasets, wait a moment....')
        Database.COLLECTION = self._client[self.databaseName]
        double_check = [date for date in scraped_interval if date not in Database.COLLECTION.list_collection_names()]
        print('\nSince there is no stored data, you should double check these collections: \n\n', double_check)
        print(f'\nThere are {len(double_check)} collections you should check.')
        return double_check


class DatabaseUpdator(Database):
    """
    Class inherits Database class to properly work when updating a new collection of data.

    """

    # def __init__(self):
    #     pass

    def update_db(self):
        """
        Shows a list of available collections we can find inside the selected database and asks if we are interested
        in updating our database with new data.

        Arguments:
        ----------
        ()
        Returns:
        --------
            Collections we are willing to include into our database.

        """

        Database.COLLECTION = self._client[self.databaseName]
        available_data = sorted(Database.COLLECTION.list_collection_names())
        print('Available data: ', available_data)

        print(f'\nThere are {len(available_data)} available collections in your database.')

        print("\nIf you'd like to collect all the available data, write: 'ORIGIN'.")
        print("If you'd like to update your general csv file, write: 'UPDATE'.")
        print("If you'd like to update since the last available record in the database, write 'LAST'.")
        print("To update from a specific period, write the date in this format: 'YYYYMMDD'.")
        print("To update ONLY a CONCRETE period, write: CONCRETE.")

        interval = str(input()).lower()
        if interval == 'last':
            last_val = available_data[-1]
            print('You have chosen LAST, so we will update your general csv file since:', last_val)
            to_update = [x for x in available_data if x >= last_val]
            return sorted(to_update), ''

        elif interval == 'origin':
            print(f'You have chosen ORIGIN, so we are going to collect data since the very beginning.')
            to_update = [x for x in available_data if x >= '20141121']
            return sorted(to_update), ''

        elif interval == 'concrete':
            print('Write the period you want to collect in the following format: "YYYYMMDD" ')
            interval = str(input())
            if interval in available_data:
                print(f'The interval: {interval} is available')
                return [interval], ''
            else:
                print('Sorry but we do not have this collection in our database.')

        elif interval in available_data:
            print(f'The interval: {interval} is available')
            to_update = [x for x in available_data if x >= interval]
            return sorted(to_update), ''

        elif interval == 'update':
            return available_data[-1], ''

        else:
            print('There is no data for this database')
