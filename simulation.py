import modelfile

import argparse
import os

PRIOR_FILE_TEMPLATE = 'prior_{numModels}_{repetition}.txt'
POSTERIOR_FILE_TEMPLATE = 'posterior_{numModels}_{repetitions}.txt'
MS_REJECT_TEMPLATE = './msReject {pod} {prior} 0.00005 18 ' + \
    '26 34 42 50 19 27 35 43 51 20 28 36 42 52 > {posterior}'
POD_FILE_NAME = 'pod.txt'


def main(masterModelFile, repetitions, numModels):
    masterModelFile = modelfile.ModelFile(args.masterModelFile)
    for num in numModels:
        for rep in range(repetitions):
            rep += 1
            priorFileName = PRIOR_FILE_TEMPLATE.format(
                numModels=num, repetitions=rep)
            priorFile = modelfile.generateFileWithNModels(
                masterModelFile, priorFileName, num)
            #print(genFile.models, genFile.numInstances)

            pod = priorFile.removeRandomInstance()
            podFile = open(POD_FILE_NAME, 'w')
            podFile.write(pod)

            posteriorFileName = POSTERIOR_FILE_TEMPLATE.format(
                numModels=num, repetition=rep)
            msRejectCommand = MS_REJECT_TEMPLATE.format(
                pod=POD_FILE_NAME, prior=priorFileName,
                posterior=posteriorFileName)
            os.system(msRejectCommand)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='masterModelFile')
    parser.add_argument('-l', '--lower', required=True, type=int,
                        help='fewest number of models')
    parser.add_argument('-u', '--upper', required=True, type=int,
                        help='maximum number of models')
    parser.add_argument('-i', '--increment', required=True, type=int,
                        help='number of models to increment each test')
    parser.add_argument('-r', '--repetitions', required=True, type=int,
                        help='number of times each simulation is run')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display a lot of extra info')
    parser.add_argument('-d', '--dryrun', action='store_true',
                        help="don't run the simulation")
    args = parser.parse_args()
    numModels = [x for x in range(args.lower, args.upper+1, args.increment)]

    if args.verbose:
        print(args)
        print (numModels)
    if not args.dryrun:
        main(args.masterModelFile, args.repetitions, numModels)
