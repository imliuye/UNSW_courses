import torch
from collections import defaultdict
from config import config
import torch.nn.functional as F
from torch.nn._functions.thnn import rnnFusedPointwise as fusedBackend
_config = config()

test = False


def last_index(mylist, myvalue):
    return len(mylist) - mylist[::-1].index(myvalue) - 1


def evaluate(golden_list, predict_list):
    '''
    This method computes the F1 score of the given predicted tags and golden tags.
    :param golden_list:
    :param predict_list:
    :return:
    '''

    tp = 0
    fp_fn = 0

    for i in range(len(golden_list)):

        golden = golden_list[i]
        predict = predict_list[i]
        # golden_bit = [1 if golden[j] != 'O' else 0 for j in range(len(golden))]
        # predict_bit = [1 if predict[j] != 'O' else 0 for j in range(len(predict))]

        golden_tar_start = golden.index('B-TAR')
        try:
            golden_tar_end = last_index(golden, 'I-TAR')
        except ValueError:
            golden_tar_end = golden_tar_start

        golden_hyp_start = golden.index('B-HYP')
        try:
            golden_hyp_end = golden.index('I-HYP')
        except ValueError:
            golden_hyp_end = golden_hyp_start

        tar_len = golden_tar_end + 1 - golden_tar_start
        hyp_len = golden_hyp_end + 1 - golden_hyp_end

        if golden[golden_tar_start:golden_tar_end + 1] == predict[golden_tar_start:golden_tar_end+1] \
                and (golden_tar_end + 1 == len(golden) or predict[golden_tar_end+1] != 'I-TAR'):
            tp += tar_len
        else:
            fp_fn += tar_len

        if golden[golden_hyp_start:golden_hyp_end + 1] == predict[golden_hyp_start:golden_hyp_end+1]\
                and(golden_hyp_end + 1 == len(golden) or predict[golden_hyp_end+1] != 'I-HYP'):
            tp += hyp_len
        else:
            fp_fn += hyp_len

        # o_false = [1 for j in range(len(golden)) if predict_bit[j] == 1 and golden_bit[j] == 0]
        o_false = [1 for j in range(len(golden)) if predict[j] != 'O' and golden[j] == 'O']
        fp_fn += len([1 for j in range(len(golden)) if predict[j] != 'O' and golden[j] == 'O'])

        if test:
            print('---------------')
            print('golden: ', golden)
            print('predict: ', predict)
            print('golden_tar_start, golden_tar_end, tar_len')
            print(golden_tar_start, golden_tar_end, tar_len)
            print('golden_hyp_start,golden_hyp_end,hyp_len')
            print(golden_hyp_start,golden_hyp_end,hyp_len)
            print('o_false and len ', o_false, ' o_false_len:', len(o_false))
            print('tp:', tp)
            print('fp+fn', fp_fn)
            print('---------------')

    f1_score = 2*tp/(2*tp+fp_fn)
    if test:
        print(f1_score)
    return f1_score


def new_LSTMCell(input_, hidden, w_ih, w_hh, b_ih=None, b_hh=None):
    if input_.is_cuda:
        igates = F.linear(input_, w_ih)
        hgates = F.linear(hidden[0], w_hh)
        state = fusedBackend.LSTMFused.apply
        return state(igates, hgates, hidden[1]) if b_ih is None else state(igates, hgates, hidden[1], b_ih, b_hh)

    hx, cx = hidden
    gates = F.linear(input_, w_ih, b_ih) + F.linear(hx, w_hh, b_hh)

    ingate, forgetgate, cellgate, outgate = gates.chunk(4, 1)
    ingate = torch.sigmoid(ingate)
    forgetgate = torch.sigmoid(forgetgate)
    cellgate = torch.tanh(cellgate)
    outgate = torch.sigmoid(outgate)

    cy = (forgetgate * cx) + ((1-forgetgate) * cellgate)
    hy = outgate * torch.tanh(cy)

    return hy, cy


def get_char_sequence(model, batch_char_index_matrices, batch_word_len_lists):
    pass;


if __name__ == '__main__':
    golden_list = [['B-TAR', 'I-TAR', 'O', 'B-HYP'], ['B-TAR', 'O', 'O', 'B-HYP']]
    predict_list = [['B-TAR', 'O', 'O', 'O'], ['B-TAR', 'O', 'B-HYP', 'I-HYP']]
    f1 = evaluate(golden_list, predict_list)
    print(f1)

'''

golden_list = [['B-TAR', 'I-TAR', 'O', 'B-HYP'], ['B-TAR', 'O', 'O', 'B-HYP']]
predict_list = [['B-TAR', 'O', 'O', 'O'], ['B-TAR', 'O', 'B-HYP', 'I-HYP']]
f1 = evaluate(golden_list, predict_list)
print(f1)
#0.2857142857142857
    
golden_list = [['B-TAR', 'O', 'O', 'B-HYP']]
predict_list = [['B-TAR', 'O', 'B-HYP', 'I-HYP']]
f1 = evaluate(golden_list, predict_list)
print(f1)
    
    
golden_list = [['B-TAR', 'I-TAR', 'I-TAR', 'B-HYP']]
predict_list = [['B-TAR', 'O', 'B-HYP', 'O']]
f1 = evaluate(golden_list, predict_list)
print(f1)

golden_list = [['B-TAR', 'I-TAR', 'I-TAR', 'B-HYP']]
predict_list = [['B-TAR', 'O', 'B-HYP', 'I-HYP']]
f1 = evaluate(golden_list, predict_list)
print(f1)
    
golden_list = [['B-TAR', 'I-TAR', 'O', 'B-HYP']]
predict_list = [['B-TAR', 'I-TAR','I-TAR', 'B-HYP']]
f1 = evaluate(golden_list, predict_list)
print(f1)   


golden_list = [['B-TAR', 'I-TAR', 'O', 'B-HYP']]
predict_list = [['B-TAR', 'I-TAR','', 'B-HYP']]
f1 = evaluate(golden_list, predict_list)
print(f1)   
'''