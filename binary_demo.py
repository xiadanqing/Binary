import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


class Processing():
    #极度简单的黑名单
    def _get_blacklist(self,train):
        cheat = train[train['label']==1] 
        noCheat = train[train['label']==0] 
        blacklist_dic = {}
        for f in ['ip','adidmd5','imeimd5']:
            w_s = []
            s = set(cheat[f])
            blacklist_dic[f] = s
        return blacklist_dic

class TrainModels():  
    #极度简单的黑名单的作弊判断
    def _judge_black(self,blacklist_dic,test):
        judge_cheat_sid = set()
        judge_features = list(blacklist_dic.keys())
        judge_df = test[judge_features+['sid']]
        judge_df['label'] = [0]*len(judge_df)
        for f in judge_features:
            s = blacklist_dic[f]
            judge_df['label'] = judge_df.apply(lambda x: 1 if (x[f] in s or x['label'] == 1) else 0,axis=1)
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

