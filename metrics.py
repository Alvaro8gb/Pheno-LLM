def calculate_metrics(y_true:set, y_pred:set):
    tp = 0
    fp = 0
    fn = 0

    for elem in y_true:
        if elem in y_pred:
            tp+=1
        else:
            fn+=1

    fp = len(y_pred - y_true)

    return tp, fn, fp  

def precision(tp, fp):
    if tp + fp == 0:
        return 1
    else:
        return tp/(tp+fp)


def recall(tp, fn):
    if tp + fn == 0:
        return 1
    else:
        return tp/(tp+fn)


def fscore(precision, recall):
    return (2*precision*recall) / (precision+recall)


def metrics(tp, tn, fp, fn):
    """
    In NER True negative is not used, so on accuracy also not
    """

    p = precision(tp, fp)
    r = recall(tp, fn)

    if p == 0 and r == 0:
        f = 0
    else:
        f = fscore(p, r)

    return p, r, f

def show_eval(tp, fn, fp):
    p, r, f = metrics(tp, 0, fp, fn)
    print("Precision: {:.2f}".format(p))
    print("Recall: {:.2f}".format(r))
    print("F1 Score: {:.2f}".format(f))
    print("-"*20)

    return p, r, f

def eval_results(results, log=True):
    
    bad = []
    total_tp, total_fn, total_fp = 0, 0, 0 
    for y_true, y_pred in results:
        tp, fn, fp  = calculate_metrics(y_true, y_pred)
        total_tp+=tp
        total_fn+=fn
        total_fp+=fp

        if log:
            if fn > 0 or fp > 0:
                bad.append([sorted(list(y_true)), sorted(list(y_pred))])

    show_eval(total_tp, total_fn, total_fp)

    return bad