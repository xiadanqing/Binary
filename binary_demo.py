import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier

class Processing():
    #黑名单获取
    def _get_blacklist(self,train):
        cheat = train[train['label']==1] 
        noCheat = train[train['label']==0] 
        blacklist_dic = {}
        for f in ['adidmd5','imeimd5']:
            w_s = []
            s = set(cheat[f])
            blacklist_dic[f] = s
        return blacklist_dic
    #特征工程 
    def _feature_eng(self,train,test):
        features = ['pkgname', 'ver', 'adunitshowid', 'mediashowid', 'apptype', 'adidmd5', 'imeimd5', 'ip','macmd5', 'openudidmd5',
            'reqrealip', 'city', 'province', 'idfamd5', 'dvctype', 'model', 'make', 'ntt',
            'carrier', 'os', 'osv', 'orientation', 'lan', 'h', 'w', 'ppi','hour']
        train_test = pd.concat([train, test], ignore_index=True,sort=True)
        train_test['label'] = train_test['label'].fillna(-1).astype(int)
        train_test['time'] = pd.to_datetime(train_test['nginxtime'] , unit='ms')
        train_test['hour'] = train_test['time'].dt.hour.astype('str')
        features.append('hour')
        new_test = train_test[train_test['label'] == -1]
        new_train = train_test[train_test['label'] != -1]
        return new_train,new_test,features
    

    
    

class TrainModels():  
    #黑名单作弊判断
    def _judge_black(self,blacklist_dic,test):
        judge_cheat_sid = set()
        judge_features = list(blacklist_dic.keys())
        judge_df = test[judge_features+['sid']]
        judge_df['label_blacklist'] = [0]*len(judge_df)
        for f in judge_features:
            s = blacklist_dic[f]
            judge_df['label'] = judge_df.apply(lambda x: 1 if (x[f] in s or x['label'] == 1) else 0,axis=1)
        return judge_df[['sid','label']]
    
    #利用catboost做二分类
    def _judge_catboost(self,train,test,features):    
        model = CatBoostClassifier(iterations=946, depth=8,cat_features=features,learning_rate=0.05, custom_metric='F1',eval_metric='F1',random_seed=2019,
                            l2_leaf_reg=5.0,logging_level='Silent')
        model.fit(train[features],train['label'])
        y_pred = model.predict(test[features]).tolist()
        
        judge_df = pd.DataFrame()
        judge_df['sid'] = test['sid'].tolist()
        judge_df['label'] = y_pred
        judge_df['label'] = judge_df['label'].apply(lambda x: 1 if x>=0.5 else 0)
        return judge_df[['sid','label']]
    

  if __name__ == "__main__":
    train = pd.read_table('round1_iflyad_anticheat_traindata.txt')
    test = pd.read_table('round1_iflyad_anticheat_testdata_feature.txt')    
    proce_module = Processing()
    model_module = TrainModels()
    #黑名单
    blacklist_dic = proce_module._get_blacklist(train)
    judge_by_blackList = model_module._judge_black(blacklist_dic,test)
    judge_by_blackList.to_csv('judge_by_blackList.csv',index=False,encoding='utf-8')
    #二分类---使用catboost
    new_train,new_test,features= proce_module._feature_eng(train,test)
    judge_by_catboost = model_module._judge_catboost(new_train,new_test,features)   
    judge_by_catboost.to_csv('judge_by_catboost.csv',index=False,encoding='utf-8')

