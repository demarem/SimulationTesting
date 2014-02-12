import argparse
from collections import Counter
import glob
from os import path
import re

OUTPUT_HEADER = '"File Name", "POD Model", "p(POD)", "p(~POD)"\n'
OUTPUT_TEMPLATE = '"{F}", "{MODEL}", "{P_POD}", "{P_NOT_POD}"\n'
FILE_NAME_PARTS = r'posterior_(?P<NUM_MODELS>\d+)_(?P<REP>\d+).txt'
FILE_NAME_REGEX = re.compile(FILE_NAME_PARTS)

isVerbose = False


def main(inDir, outFile, simDataFile):
    outFile.write(OUTPUT_HEADER)
    next(simDataFile)
    PODS = {}
    for line in simDataFile:
        parts = line.split(',')
        (numModels, repetition) = parts[0].strip(), parts[1].strip()
        podModel = parts[2].strip()
        PODS[(numModels, repetition)] = podModel

    if isVerbose:
        print PODS

    for f in glob.glob(inDir + '/*.txt'):
        modelsCounter = Counter()
        with open(f, 'r') as inFile:
            for line in inFile:
                parts = line.split()
                model = parts[0][1:]
                modelsCounter[model] += 1

        # determine POD model
        fileName = path.basename(f)
        filePartsMatch = FILE_NAME_REGEX.match(fileName)
        numModels = filePartsMatch.group('NUM_MODELS')
        repetition = filePartsMatch.group('REP')
        pod = PODS[(numModels, repetition)]

        # determine POD probability
        total = sum(modelsCounter.values())
        p_pod = float(modelsCounter[pod]) / total

        # determine highest not pod, then its probability
        mostCommon = modelsCounter.most_common(2)
        not_pod = mostCommon[0][0]
        if mostCommon[0][0] == pod:
            not_pod = mostCommon[1][0]
        p_not_pod = float(modelsCounter[not_pod]) / total

        if isVerbose:
            print '\nPOD: ', pod
            print 'Not POD: ', not_pod
            print 'Total: ', total
            print modelsCounter
            print 'Two most common: ', mostCommon

        # output results
        output = OUTPUT_TEMPLATE.format(F=fileName, MODEL=pod, P_POD=p_pod,
                                        P_NOT_POD=p_not_pod)
        outFile.write(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='posteriorFolder', help='directory containing ' +
                        'only posterior files')
    parser.add_argument(dest='outputFile', type=argparse.FileType('w'))
    parser.add_argument(dest='simulationDataFile', type=argparse.FileType('r'),
                        help='file containing the output from running ' +
                        'simulation test. each line in file has ' +
                        '[NUM_MODELS], [REPETITION], [POD_MODEL], ...')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display a lot of extra info')
    args = parser.parse_args()

    if args.verbose:
        print(args)
        isVerbose = True

    main(args.posteriorFolder, args.outputFile, args.simulationDataFile)
