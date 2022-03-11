import math
from doc_utils import *

N_up = 612  # 613-1
N_down = 126  # 127-1
N_ttl = 738  # 613+127-1-1


class Phrase:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.tf_all = self.tf_up + self.tf_down
        self.df_all = self.df_up + self.df_down
        for elm in ['up', 'down']:
            self.calc_MI(elm)
            self.calc_tfidf(elm)
            self.calc_assocs(elm)
            self.calc_chisq(elm)

    def __gt__(self, other):
        if self.conf_up > other.conf_up:
            return True
        elif self.conf_up == other.conf_up:
            if self.supp_up > other.supp_up:
                return True
            else:
                return False
        else:
            return False

    def __str__(self):
        frqstr = 'Phrase:{}\nUP: tf={}, df={} / {}\nDN: tf={}, df={} / {}\nALL: tf={}, df={} / {}\n' \
            .format(self.name, self.tf_up, self.df_up, N_up, self.tf_down, self.df_down, N_down, self.tf_all, self.df_all, N_ttl)
        ascstr = 'UP: MI={:.3f}, tfidf={:.3f}, support={:.3f}, confidence={:.3f}, lift={:.3f}, CHISQ={:.3f}\nDN: MI={:.3f}, tfidf={:.3f}, support={:.3f}, confidence={:.3f}, lift={:.3f}, CHISQ={:.3f}' \
            .format(self.MI_up, self.tfidf_up, self.supp_up, self.conf_up, self.lift_up, self.chisq_up,
                    self.MI_down, self.tfidf_down, self.supp_down, self.conf_down, self.lift_down, self.chisq_down)

        return frqstr + ascstr + '\n -------------------------------------------------------------------------------------------'

    def calc_MI(self, lmttyp):
        # MI = log(N(XY) / (N(X)N(Y)), belongs to df
        if lmttyp == 'up':
            self.MI_up = math.log((self.df_up + 1e-4) / (N_up * self.df_all))
        elif lmttyp == 'down':
            self.MI_down = math.log((self.df_down + 1e-4) / (N_down * self.df_all))

    def calc_tfidf(self, lmttyp):
        # tf-idf = (1+log(tf)) * log(N_ttl/df) ???
        N_tmp = N_up if lmttyp == 'up' else N_down
        if lmttyp == 'up':
            self.tfidf_up = (1 + math.log(self.tf_up + 1e-4)) * math.log(N_ttl / self.df_all)
        elif lmttyp == 'down':
            self.tfidf_down = (1 + math.log(self.tf_down + 1e-4)) * math.log(N_ttl / self.df_all)

    def calc_assocs(self, lmttyp):
        # Support P(XY) = N(XY)/N_ttl
        # Confidence(X->Y) P(Y|X) = P(XY)/P(X) = N(XY)/N(X)
        # Lift P(XY)/(P(X)P(Y)) = N_ttl*N(XY)/(N(X)N(Y))
        # Feature (X) -> up or down (Y)
        if lmttyp == 'up':
            self.supp_up = self.df_up / N_ttl
            self.conf_up = self.df_up / self.df_all
            self.lift_up = (N_ttl * self.df_up) / (self.df_all * N_up)
        elif lmttyp == 'down':
            self.supp_down = self.df_down / N_ttl
            self.conf_down = self.df_down / self.df_all
            self.lift_down = (N_ttl * self.df_down) / (self.df_all * N_down)

    def calc_chisq(self, lmttyp):
        if lmttyp == 'up':
            expected = self.df_all * N_up / N_ttl
            self.chisq_up = (1 if self.df_up > expected else -1)*(self.df_up - expected)**2 / expected
        elif lmttyp == 'down':
            expected = self.df_all * N_down / N_ttl
            self.chisq_down = (1 if self.df_down > expected else -1) * (self.df_down - expected)**2 / expected


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def generatePhraseList(save=True):
    tf_up = JSON2COUNTER('up', 'tf')
    df_up = JSON2COUNTER('up', 'df')
    tf_down = JSON2COUNTER('down', 'tf')
    df_down = JSON2COUNTER('down', 'df')
    tf_all = JSON2COUNTER('all', 'tf')
    df_all = JSON2COUNTER('all', 'df')

    ret_lst = []
    for key, val in df_all.most_common():
        phrase = Phrase(name=key,
                        tf_up=tf_up[key] if key in tf_up else 0,
                        df_up=df_up[key] if key in df_up else 0,
                        tf_down=tf_down[key] if key in tf_down else 0,
                        df_down=df_down[key] if key in df_down else 0
                        )
        ret_lst.append(phrase)
    if save: PhraseList2JSON(ret_lst)
    return ret_lst

def showPhraseList(lst, num, show_detail=True):
    namelist = []

    for idx, elm in enumerate(lst[0:num]):
        if show_detail: print('{} {}'.format(idx, elm))
        namelist.append(elm.name)

    showNameList(namelist)
    return namelist


def showNameList(namelist):
    num = len(namelist)
    cnt = 0
    for elm in namelist[0:num]:
        print('{}'.format(elm), end=' ')
        if cnt == 9:
            cnt = 0
            print('')
        else:
            cnt += 1
    print('\nNum: {}'.format(num))

if __name__ == '__main__':
    generate = True
    if(generate): phraselist = generatePhraseList()
    else: phraselist = JSON2PhraseList()
    showPhraseList(phraselist, 10)
