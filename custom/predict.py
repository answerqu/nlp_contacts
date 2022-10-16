import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np

class ModelBoosting:
    """
    Класс-обертка бустингового классификатора для запуска в контейнере.
    """
    def __init__(self, clf_params = {}, tfidf_params = {}, add_clf_params = None, add_clf_features = None,
                 add_clf_cat_features = None):
        self.clf = LGBMClassifier(**clf_params)
        self.tfidf = TfidfVectorizer(**tfidf_params)

        if add_clf_params is not None and add_clf_features is not None:
            self.add_clf_features = add_clf_features
            self.add_clf_cat_features = add_clf_cat_features
            self.add_clf = LGBMClassifier(**add_clf_params)
            self.lr_stacking = LogisticRegression(random_state=42)
            self.mappers = {}
        else:
            self.add_clf = None
            self.mappers = None

    def label_encoding(self, df, df_val = None):
        if df_val is not None: #fit function
            for c in self.add_clf_cat_features:
                if df[c].dtype == 'O' and df_val[c].dtype == 'O':
                    le = LabelEncoder()
                    df[c] = le.fit_transform(df[c])
                    mapper = dict(zip(le.classes_, range(len(le.classes_))))
                    df_val[c] = df_val[c].map(lambda x: mapper.get(x,-1))
                    self.mappers[c] = mapper
            return df, df_val
        else: #predict_proba function or no early_stopping_rounds
            if self.mappers is None:
                for c in self.add_clf_cat_features:
                    if df[c].dtype == 'O':
                        le = LabelEncoder()
                        df[c] = le.fit_transform(df[c])
                        mapper = dict(zip(le.classes_, range(len(le.classes_))))
                        self.mappers[c] = mapper
            else:
                for c, mapper in self.mappers.items():
                    df[c] = df[c].map(lambda x: mapper.get(x,-1))
            return df

    def fit(self, df_train, df_val = None) -> None:
        print('Fitting tf-idf model...')
        train_tfidf = self.tfidf.fit_transform(df_train['normalized_text'])
        if df_val is not None:
            print('\n\nFitting model on tf-idf features...')
            val_tfidf = self.tfidf.transform(df_val['normalized_text'])
            self.clf.fit(train_tfidf, df_train.is_bad, eval_set=[(val_tfidf, df_val.is_bad)],
                                early_stopping_rounds=50, eval_metric='auc', verbose=250)

            if self.add_clf is not None:
                print('\n\nFitting model on meta features...')
                df_train, df_val = self.label_encoding(df_train.copy(), df_val.copy())

                self.add_clf.fit(df_train[self.add_clf_features], df_train.is_bad, 
                                 categorical_feature = self.add_clf_cat_features,
                                 eval_set = [(df_val[self.add_clf_features], df_val.is_bad)],
                                 early_stopping_rounds=50, verbose=250, eval_metric='auc')
                
                sample = pd.concat([df_train, df_val])
                sample['pred_1'] = self.add_clf.predict_proba(sample[self.add_clf_features]).T[1]
                sample['pred_2'] = self.clf.predict_proba(self.tfidf.transform(sample['normalized_text'])).T[1]

                print('\n\nFitting logreg stacking model...')
                self.lr_stacking.fit(sample[['pred_1','pred_2']], sample.is_bad)
                
        else:
            print('\n\nFitting model on tf-idf features... No early_stopping_rounds.')
            self.clf.fit(train_tfidf, df_train.is_bad, verbose=250)
            if self.add_clf is not None:
                print('\n\nFitting model on meta features... No early_stopping_rounds.')
                df_train = self.label_encoding(df_train.copy())

                self.add_clf.fit(df_train[self.add_clf_features], df_train.is_bad, verbose=250, 
                                 categorical_feature = self.add_clf_cat_features)

                sample = df_train.copy()
                sample['pred_1'] = self.clf.predict_proba(self.tfidf.transform(sample['normalized_text'])).T[1]
                sample['pred_2'] = self.add_clf.predict_proba(sample[self.add_clf_features]).T[1]

                print('\n\nFitting logreg stacking model...')
                self.lr_stacking.fit(sample[['pred_1','pred_2']], sample.is_bad)

    def predict_proba(self, df):
        """
        Объединение инференса объекта TfidfVectorizer и LGBMClassifier.
        """
        df_tfidf = self.tfidf.transform(df['normalized_text'])
        pred_2 = self.clf.predict_proba(df_tfidf).T[1]
        if self.add_clf is not None:
            df = self.label_encoding(df.copy())
            pred_1 = self.add_clf.predict_proba(df[self.add_clf_features]).T[1]
            sample = np.concatenate([pred_1.reshape(-1,1), pred_2.reshape(-1,1)],axis=1)

            return self.lr_stacking.predict_proba(sample)
        else:
            return pred_2

    def save_model(self, name):
        joblib.dump(self, os.path.join('models', name))

