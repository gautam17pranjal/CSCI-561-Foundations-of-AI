from operator import itemgetter
import collections
import copy

def convertCNF(n, kb):
    cnf = []
    for i in range(n):
        if('=>' in kb[i]):      
            temp = kb[i].split('=>')
            left, right = temp[0], temp[1]
            leftOld = left.split('&')
            negLeft = []
            for val in leftOld:
                val = val.strip()
                if(val[0] == "~"):
                    negLeft.append(val[1:])
                else:
                    negLeft.append("~"+val)
            newLeft = "|".join(negLeft)
            cnf.append(newLeft+"|"+right.strip())  
        else: 
            cnf.append(kb[i])
    return cnf

def standardizeVariables(kb):
    i = 0
    res = []
    var_dict = dict()
    for sentence in kb:
        preds = sentence.split('|')
        var_sen_dict = dict()
        for j, p in enumerate(preds):
            t1 = p.split('(')   
            t2 = t1[1].split(')')   
            varb = t2[0].split(",")
            for k, val in enumerate(varb):
                if(val[0].islower()):   
                    if(val in var_sen_dict):
                        varb[k] = var_sen_dict[val]
                    else:
                        varb[k] = 'a'+str(i)
                        var_sen_dict[val] = 'a'+str(i)
                        var_dict[val] = var_sen_dict[val]
                        i += 1
            variables = ",".join(varb)
            preds[j] = t1[0]+"("+variables+")"
        newSentence = "|".join(preds)
        res.append(newSentence)
    return res

def divideKB(kb):
    negKB, posKB, posConst, negConst = dict(), dict(), dict(), dict()
    for val in kb:
        if('|' not in val):     
            if(val[0] == '~'):
                pred = val[1:].split('(')[0]
                if(pred in negConst):
                    negConst[pred].append(val)
                else:
                    negConst[pred] = [val]
            else:
                pred = val.split('(')[0]
                if(pred in posConst):
                    posConst[pred].append(val)
                else:
                    posConst[pred] = [val]
        else:
            predicates = val.split('|')
            for p in predicates:
                if(len(p) != 0):
                    if(p[0] == '~'):
                        p = p[1:].split('(')[0]
                        if p in negKB:
                            negKB[p].append(val)
                        else:
                            negKB[p] = [val]
                    else:
                        p = p.split('(')[0]
                        if p in posKB:
                            posKB[p].append(val)
                        else:
                            posKB[p] = [val]
    return negKB, posKB, posConst, negConst

def cleanSubQuery(q):
    if(len(q) == 0):
        return q
    q = q.replace(" ", "")
    q = q.replace("||", "|")
    if(q[0] == "|"):
        q = q[1:]
    if(q[-1] == "|"):
        q = q[:-1]
    temp = list(set(q.split('|')))
    q = "|".join(temp) 
    temp = q.split('|')
    n = len(temp)
    for i in range(0, n-1):
        f = True
        p1, const1 = getPredVariables(temp[i])
        for j in range(i+1, n):
            if((temp[i][0]== '~' and temp[j][0]!='~') or (temp[i][0]!='~' and temp[j][0] == '~')):
                p2, const2 = getPredVariables(temp[j])
                if(len(const1) != len(const2)):
                    continue
                elif(len(const1) == len(const2)):
                    if(p1 == p2):
                        for k in range(len(const1)):
                            if(const1[k][0].isupper() and const2[k][0].isupper()):
                                if(const1[k] != const2[k]):
                                    f = False
                                    break
                            elif(const1[k][0].islower() and const2[k][0].islower()):
                                continue
                            else:
                                f = False
                                break
                        if(f): 
                            temp[i] = ""
                            temp[j] = ""
    q = "|".join(temp)
    q = q.replace(" ", "")
    q = q.replace("||", "|")
    if(q[0] == "|"):
        q = q[1:]
    if(q and q[-1] == "|"):
        q = q[:-1]
    q = q.split('|')
    temp = []
    for val in q:
        constLen = len(val.split(','))
        temp.append([constLen, val])
    temp = sorted(temp, key = itemgetter(0))
    res = ""
    for val in temp:
        res += val[1]+"|"
    return res[:-1]

def getPred(q):
    res = []
    clauses = q.split('|')
    for c in clauses:
        res.append(c.split('(')[0])
    return len(res), res

def checkPredCounters(pred_q, pred_c):
    q, c = collections.Counter(pred_q), collections.Counter(pred_c)
    for key_q in q:
        if(key_q in c):
            if(q[key_q] != c[key_q]):
                return False
    return True

def checkMatch(query, clause):
    flag = False
    query, clause = cleanSubQuery(query), cleanSubQuery(clause)
    if(len(query) != len(clause)):
        return False
    if(len(query) == 0):
        return True
    qy = copy.deepcopy(query)
    cl = copy.deepcopy(clause)
    replaceFinal = {}
    predInQuery = qy.split('|')
    predInClause = cl.split('|')
    if(len(predInClause) != len(predInQuery)):
        return False
    for j, val in enumerate(predInQuery):
        queryPred, queryVar = getPredVariables(val)
        for i, c in enumerate(predInClause):
            cPred, cVar = getPredVariables(c)
            if(queryPred == cPred):
                if(len(queryVar) != len(cVar)):
                    continue
                qval, pval, replace, f = compareVariables(queryVar, cVar)
                if(f == False): 
                    None
                else: 
                    replaceFinal.update(replace)
                    predInClause[i] = ""
                    predInQuery[j] = ""
                    flag = True
                    break
        if(flag):
            break
        else:
            return False
    if(flag):   
        for k, d in enumerate(predInClause):
            if(len(d) != 0):
                pred, const = getPredVariables(d)
                for g, p in enumerate(const):
                    if(p in replaceFinal):
                        const[g] = replaceFinal[p]
                predInClause[k] = pred + "(" + ",".join(const) + ")"
        for k, d in enumerate(predInQuery):
            if(len(d)!= 0):
                pred, const = getPredVariables(d)
                for g, p in enumerate(const):
                    if(p in replaceFinal):
                        const[g] = replaceFinal[p]
                predInQuery[k] = pred + "(" + ",".join(const) + ")"
        q = copy.deepcopy("|".join(predInClause))
        c = copy.deepcopy("|".join(predInQuery))
        res = checkMatch(q, c)
        if(res == True):
            return True
    return False

def checkQueryHistory(q, history):
    n_q, pred_q = getPred(q)
    for seen in history:
        n_seen, pred_seen = getPred(seen)
        if(n_q != n_seen):
            continue
        if(n_q == n_seen):
            if(checkPredCounters(pred_q, pred_seen)):
                if(q == seen):
                    return True
                else:
                    query = copy.deepcopy(q)
                    clause = copy.deepcopy(seen)
                    if(checkMatch(query, clause)):
                        return True
                    else:
                        continue
            else:
                continue
    return False

def unify(q, negKB, posKB, posConst, negConst, history):
    q = cleanSubQuery(q)
    if(q == ""):
        return True
    for seen in history:
        if(checkQueryHistory(copy.deepcopy(q), history)):
            return False
    h = copy.deepcopy(history)
    h.append(q)
    sentences = []
    if(q[0] == '~'):
        pred = q.split('(')[0]    
        if(pred[1:] not in posKB and pred[1:] not in posConst):
            return False
        if(pred[1:] in posConst):
            sentences += posConst[pred[1:]]
        if(pred[1:] in posKB):
            sentences += posKB[pred[1:]]
        temp = q[1:].split(')')[0]+')'
        for sentence in sentences:
            res, val = subsitution(temp, q, sentence)
            res = cleanSubQuery(res)
            if(val == False):   
                continue
            if(res == ""):  
                return True
            else:      
                if(unify(res, negKB, posKB, posConst, negConst, h)):
                    return True
                else:
                    continue
        return False
    else:
        pred = q.split('(')[0]
        if(pred not in negKB and pred not in negConst):
            return False
        if(pred in negConst):
            sentences += negConst[pred[0:]]
        if(pred in negKB):
            sentences += negKB[pred[0:]]
        temp = '~'+q[0:].split(')')[0]+')'
        for sentence in sentences:
            res, val = subsitution(temp, q, sentence)
            if(val == False):   
                continue
            if(res == ""):
                return True
            else:
                res = cleanSubQuery(res)
                if(unify(res, negKB, posKB, posConst, negConst, h)):
                    return True
                else:
                    continue
    return False

def getPredVariables(query):
    temp = query.split('(')
    t = temp[1][:-1]
    t = t.replace(')', "")
    pred, variables = temp[0], t.split(',')
    return pred, variables

def subsitution(query, entireq, sentence):       
    flag = False
    replaceFinal = {}
    predInSentence = sentence.split('|')
    queryPred, queryVariables = getPredVariables(query)
    try:
        for i, val in enumerate(predInSentence):
            pred, predVariables = getPredVariables(val)
            if(pred == queryPred):  
                try:
                    qval, pval, replace, f = compareVariables(queryVariables, predVariables)
                except:
                    f = False
                if(f == False):     
                    None
                else:   
                    replaceFinal.update(replace)
                    predInSentence[i] = ""
                    flag = True
                    break
        if(flag):   
            queryTemp = entireq.split('|')
            predInSentence += queryTemp[1:]
            try:
                for j, val in enumerate(predInSentence):
                    if(len(val) != 0):
                        pred, const = getPredVariables(val)
                        for k, c in enumerate(const):
                            if(c in replaceFinal):
                                const[k] = replaceFinal[c]
                        predInSentence[j] = pred + "(" + ",".join(const) + ")"
                q = "|".join(predInSentence)
                q = cleanSubQuery(q)
                return q, flag
            except:
                return "queryFailed", False
    except:
        return "queryFailed", False
    return "queryFailed", flag

def compareVariables(qVar, pVar):      
    ip = 0
    flag = True
    replacement = dict()
    if(len(qVar) != len(pVar)):
        return qVar, pVar, replacement, False
    for iq in range(len(qVar)):
        if(qVar[iq][0].islower() and pVar[ip][0].islower()):      # both are variables
            replacement[qVar[iq]] = pVar[ip]
            qVar = [pVar[ip] if x == qVar[iq] else x for x in qVar]
            ip += 1
        elif(qVar[iq][0].islower() and pVar[ip][0].isupper()):      # q-> variable , sentence-> const
            replacement[qVar[iq]] = pVar[ip]
            qVar = [pVar[ip] if x == qVar[iq] else x for x in qVar]
            ip += 1
        elif(qVar[iq][0].isupper() and pVar[ip][0].islower()):   # q-> constant , sentence-> variable
            replacement[pVar[ip]] = qVar[iq]
            pVar = [qVar[iq] if x == pVar[ip] else x for x in pVar]
            ip += 1
        elif(qVar[iq][0].isupper() and pVar[ip][0].isupper()):
            if(qVar[iq] == pVar[ip]):
                ip += 1
            else:
                flag = False
                break
    return qVar, pVar, replacement, flag


def generateOutput(ans):        
    f = open("output.txt", "w")
    for val in ans:
        f.write(val)
        f.write('\n')
    f.close()

f = open("input.txt", "r")
numQueries = int(f.readline().strip().split("\n")[0])
queries, kb = [], []
for i in range(numQueries):
    line = f.readline().strip().split("\n")[0]
    line = line.replace(" ", "")
    queries.append(line)
numKB = int(f.readline().strip().split("\n")[0])
for i in range(numKB):
    sentence = f.readline().strip().split("\n")[0]
    sentence = sentence.replace(" ", "")
    kb.append(sentence)
f.close()
kb = convertCNF(numKB, kb)
kb = standardizeVariables(kb)
negKB, posKB, posConst, negConst = divideKB(kb)
ans = []
for q in queries:
    history = []
    if(q[0] == "~"):
        newQuery = q[1:]
        posConstTemp = copy.deepcopy(posConst)
        pred = q[1:].split('(')[0]
        if(pred in posConstTemp):
            posConstTemp[pred].append(newQuery)
        else:
            posConstTemp[pred] = [newQuery]
        if(unify(newQuery, negKB, posKB, posConstTemp, negConst, history)):
            ans.append("TRUE")
        else:
            ans.append("FALSE")  
    else:
        newQuery = "~"+q[0:]
        pred = q[0:].split('(')[0]
        negConstTemp = copy.deepcopy(negConst)
        if(pred in negConstTemp):
            negConstTemp[pred].append(newQuery)
        else:
            negConstTemp[pred] = [newQuery]
        if(unify(newQuery, negKB, posKB, posConst, negConstTemp, history)):
            ans.append("TRUE")
        else:
            ans.append("FALSE")
generateOutput(ans)
