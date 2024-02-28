import pandas as pd

class cleandf:
    def __init__(self):
         return None
     
    def liste_en_texte(self, lst):
        if isinstance(lst, list):
            return ' '.join(lst)
        else:
            return lst

    def cleanText(self, df):
        df.fillna('missing', inplace=True)
        df = df.str.replace(',', ' ')
        return df

    def BooleanToText(self, df):
        return df.apply(lambda x: 'True' if x == 1 else 'False')

    def DateToCategory(self, df):
        df.fillna(df.mean(), inplace=True)
        bins = list(range(1800, 2056, 5))
        labels = [f"between{start}and{start+4}" for start in range(1800, 2051, 5)]
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def RuntimeToCategory(self, df):
        df = df.astype(int)
        df.fillna(df.mean(), inplace=True)
        bins = list(range(0, 615, 15))
        labels = [f"runtime_Between{start}and{start+15}" for start in range(0, 600, 15)]
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def RatingToCategory(self, df):
        df.fillna(df.mean(), inplace=True)
        bins = list(range(0, 12, 2))
        labels = ['*', '**', '***', '****', '*****']
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def listTostr(self, df):
        return df.apply(lambda x: ' '.join(map(str, x)))

    def crewmod(self, x, type):
        return ' '.join([type + '_' + name for name in x.split()])

    def getindex(self, filmm):
        index_list = self.df.loc[self.df['primaryTitle'] == filmm].index
        return index_list[0] if not index_list.empty else None

    def index_list(self, similarity_measure, Nbfilm):
        sorted_indexes = sorted(enumerate(similarity_measure), key=lambda x: x[1], reverse=True)
        top_indexes = [index for index, _ in sorted_indexes[:Nbfilm]]
        return top_indexes

    def clean(self, df):
        columns_to_clean = ['titleType', 'genres', 'directors', 'writers', 
                            'actor', 'producer', 'cinematographer', 'composer', 'editor', 
                            'production_designer', 'self', 'archive_footage', 'archive_sound']

        for column in columns_to_clean:
            df[column] = self.cleanText(df[column])
            
        df['feature'] = df['primaryTitle'] + ' '

        df['feature'] += 'titleType_'+df['titleType'] + ' '

        df['feature'] += 'Rating_'+self.RatingToCategory(df['averageRating']).astype(str) + ' '

        df['feature'] += 'startYear_'+self.DateToCategory(df['startYear']).astype(str) + ' '

        df['feature'] += self.RuntimeToCategory(df['runtimeMinutes']).astype(str)+ ' '

        df['feature'] += df['genres'] + ' '

        df['feature'] += 'ADULT_'+self.BooleanToText(df['isAdult']).astype(str)+' '

        df['feature'] += df['directors'].apply(self.crewmod, type='directors').astype(str)+' '
        df['feature'] += df['writers'].apply(self.crewmod, type='writers').astype(str)+' '
        df['feature'] += df['actor'].apply(self.crewmod, type='actor').astype(str)+' '
        df['feature'] += df['producer'].apply(self.crewmod, type='producer').astype(str)+' '
        return df     