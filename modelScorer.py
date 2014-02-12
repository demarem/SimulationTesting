import argparse
import itertools
import math

# column names
NUM_MODELS = 0
REPETITION = 1
POD_MODEL = 2
POSTERIOR_PROBABILITY = 3
PRIOR_MODELS = 4
POD = 5

NUMBER_TO_COMPARE = 2

isVerbose = False

SCORES_0 = {('0', '1'): 2}
SCORES_1 = {('0', '1'): 1.0, ('0', '2'): 1.0, ('0', '3'): 1.0, ('0', '4'): 1.5,
            ('1', '2'): 0.5, ('1', '3'): 0.5, ('1', '4'): 1.0,
            ('2', '3'): 0.5, ('2', '4'): 1.0,
            ('3', '4'): 1.0}
SCORES_2 = {('0', '1'): 1.0, ('0', '2'): 1.0, ('0', '3'): 2.0,
            ('1', '2'): 0.5, ('1', '3'): 0.5,
            ('2', '3'): 0.5}
SCORES_3 = {('0', '1'): 0.5, ('0', '2'): 0.5, ('0', '3'): 1.0,
            ('1', '2'): 0.5, ('1', '3'): 0.5,
            ('2', '3'): 0.5}

SCORES = [SCORES_0, SCORES_1, SCORES_2, SCORES_3]


def score_models(m1, m2):
    # each column in t1 <= each column in t2
    t1, t2 = "", ""
    for col1, col2 in zip(m1, m2):
        col1_val, col2_val = int(col1), int(col2)
        if col1_val <= col2_val:
            t1 += col1
            t2 += col2
        else:
            t1 += col2
            t2 += col1

    score = 0
    for col1, col2, scoreMap in zip(t1, t2, SCORES):
        if (col1, col2) in scoreMap:
            score += scoreMap[(col1, col2)]

    return score


def main(inFile, outFile):
    for i, line in enumerate(inFile):
        if i > 0:
            parts = line.split(',')
            models = parts[PRIOR_MODELS].split()
            modelPairs = itertools.combinations(models, NUMBER_TO_COMPARE)

            scores = []
            scoresMap = {}
            for m1, m2 in modelPairs:
                score = score_models(m1, m2)
                scores.append(score)
                scoresMap[(m1, m2)] = score

            avg = float(sum(scores)) / len(scores)
            d = [(i-avg) ** 2 for i in scores]
            stdDev = math.sqrt(sum(d) / len(d))

            resultsString = ', " {scores} ", {avg}, {stdDev}\n'.format(
                scores=scoresMap, avg=avg, stdDev=stdDev)
            line = line.strip() + resultsString
        else:
            line = line.strip() + ', Scores, Avg, StdDev\n'
        outFile.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='inputFile', type=argparse.FileType('r'))
    parser.add_argument(dest='outputFile', type=argparse.FileType('w'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display a lot of extra info')
    args = parser.parse_args()

    if args.verbose:
        print(args)
        isVerbose = True

    main(args.inputFile, args.outputFile)
