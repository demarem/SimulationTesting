import modelfile

import argparse
import os
import re

PRIOR_FILE_TEMPLATE = 'prior_{numModels}_{repetition}.txt'
POSTERIOR_FILE_TEMPLATE = 'posterior_{numModels}_{repetition}.txt'
MS_REJECT_TEMPLATE = './msReject {pod} {prior} 0.00005 18 ' + \
    '26 34 42 50 19 27 35 43 51 20 28 36 42 52 > {posterior}'

POD_FILE_NAME = 'pod.txt'

MODEL_REGEX = r'_(\d+)'


def main(masterModelFile, repetitions, numModels, isVerbose=False):
    masterModelFile = modelfile.ModelFile(args.masterModelFile)
    modelRegex = re.compile(MODEL_REGEX)
    for num in numModels:
        for rep in range(repetitions):
            rep += 1
            priorFileName = PRIOR_FILE_TEMPLATE.format(
                numModels=num, repetition=rep)
            priorFile = modelfile.generateFileWithNModels(
                masterModelFile, priorFileName, num)
            if isVerbose:
                print(priorFile.models, priorFile.numInstances)

            pod = priorFile.removeRandomInstance()
            match = modelRegex.search(pod)
            podModel = match.group(1)
            podFile = open(POD_FILE_NAME, 'w')
            podFile.write(pod)

            posteriorFileName = POSTERIOR_FILE_TEMPLATE.format(
                numModels=num, repetition=rep)
            msRejectCommand = MS_REJECT_TEMPLATE.format(
                pod=POD_FILE_NAME, prior=priorFileName,
                posterior=posteriorFileName)
            os.system(msRejectCommand)

            if isVerbose:
                print(msRejectCommand)
                print(priorFile.models, priorFile.numInstances)

            posteriorFile = modelfile.ModelFile(posteriorFileName)
            posteriorFile.calculatePosteriorProbability(podModel)
            

        #TODO: posterior probability: occurrences of pod / total lines (from posterior)


def check_increment_nonzero(argument):
    value = int(argument)
    if value == 0:
        raise argparse.ArgumentTypeError("Increment value must be nonzero")
    return value

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='masterModelFile')
    parser.add_argument('-l', '--lower', required=True, type=int,
                        help='fewest number of models')
    parser.add_argument('-u', '--upper', required=True, type=int,
                        help='maximum number of models')
    parser.add_argument('-i', '--increment', type=check_increment_nonzero,
                        help='number of models to increment each test')
    parser.add_argument('-r', '--repetitions', required=True, type=int,
                        help='number of times each simulation is run')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display a lot of extra info')
    parser.add_argument('-d', '--dryrun', action='store_true',
                        help="don't run the simulation")
    args = parser.parse_args()

    increment = 1
    if args.increment:
        increment = args.increment

    numModels = [x for x in range(args.lower, args.upper+1, increment)]

    if args.verbose:
        print(args)
        print (numModels)
    if not args.dryrun:
        main(args.masterModelFile, args.repetitions, numModels, args.verbose)
