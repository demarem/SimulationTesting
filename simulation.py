import modelfile

import argparse
import os
import re
from collections import defaultdict, Counter
import random

PRIOR_FILE_TEMPLATE = 'priors/prior_{numModels}_{repetition}.txt'
POSTERIOR_FILE_TEMPLATE = 'posteriors/posterior_{numModels}_{repetition}.txt'
MS_REJECT_TEMPLATE = './msReject {pod} {prior} {tolerance} 18 ' + \
    '26 34 42 50 19 27 35 43 51 20 28 36 44 52 > {posterior}'
OUTPUT_TEMPLATE = '{numModels}, {repetition}, {model}, {posteriorProb}, ' + \
                  '{priorModels}, {pod}\n'
OUTPUT_HEADER = 'NumModels, Repetition, POD Model, Posterior Probability, ' + \
                'Prior Models, POD\n'

RAND_POST_OUTPUT_TEMPLATE = '{numModels}, {avgHighestPP}, {highestPP}\n'
RAND_POST_OUTPUT_HEADER = 'NumModels, Avg Highest Prob, Highest Prob\n'

POD_FILE_NAME = 'pod.txt'

MODEL_REGEX = re.compile(r'_(\d+)')

isVerbose = False


def posteriorGeneration(priorFile, numModels, repetition, tolerance):
    pod = priorFile.removeRandomInstance()
    match = MODEL_REGEX.search(pod)
    podModel = match.group(1)
    with open(POD_FILE_NAME, 'w') as podFile:
        podFile.write(pod)

    posteriorFileName = POSTERIOR_FILE_TEMPLATE.format(
        numModels=numModels, repetition=repetition)
    msRejectCommand = MS_REJECT_TEMPLATE.format(
        pod=POD_FILE_NAME, prior=priorFile.name, tolerance=tolerance,
        posterior=posteriorFileName)

    if isVerbose:
        print(msRejectCommand)

    # execute msReject program to generate posterior file
    os.system(msRejectCommand)

    posteriorFile = modelfile.ModelFile(posteriorFileName)

    return posteriorFile, podModel, pod


def randPosteriorGeneration(priorFile, repetitions, tolerance, numModels,
                            posteriorProbabilityData):
    numSamples = int(priorFile.numInstances * tolerance)
    for rep in range(repetitions):
        posteriorLines = random.sample(xrange(priorFile.numInstances),
                                       numSamples)
        posteriorModels = modelfile.getModels(priorFile, posteriorLines)
        posteriorModelsCounter = Counter(posteriorModels)
        countOfMostCommon = posteriorModelsCounter.most_common(1)[0][1]
        proportion = countOfMostCommon / float(len(posteriorModels))
        posteriorProbabilityData[numModels].append(proportion)


def main(masterModelFile, repetitions, numModelsList, outputFile, tolerance,
         deletePriors, randPostRepetitions, randPosteriorOutputFile):
    randPostRepetitionsPerPrior = randPostRepetitions / repetitions

    masterModelFile = modelfile.ModelFile(args.masterModelFile)
    posteriorProbabilityData = defaultdict(list)

    outputFile.write(OUTPUT_HEADER)
    randPosteriorOutputFile.write(RAND_POST_OUTPUT_HEADER)
    for numModels in numModelsList:
        for rep in range(repetitions):
            rep += 1

            # generate prior file with desired number of models
            priorFileName = PRIOR_FILE_TEMPLATE.format(
                numModels=numModels, repetition=rep)
            priorFile = modelfile.generateFileWithNModels(
                masterModelFile, priorFileName, numModels)

            # generate posterior based on prior and pod
            posteriorFile, podModel, pod = posteriorGeneration(
                priorFile, numModels, rep, tolerance)
            posteriorProbability = posteriorFile.calculatePosteriorProbability(
                podModel)

            # output posterior data
            priorModels = ' '.join(priorFile.models)
            output = OUTPUT_TEMPLATE.format(numModels=numModels,
                                            repetition=rep,
                                            model=podModel, pod=pod.strip(),
                                            posteriorProb=posteriorProbability,
                                            priorModels=priorModels)
            outputFile.write(output)

            randPosteriorGeneration(priorFile, randPostRepetitionsPerPrior,
                                    tolerance, numModels,
                                    posteriorProbabilityData)

            if deletePriors:
                priorFile.delete()

    for numModels, avgs in sorted(posteriorProbabilityData.items()):
        highestPP = max(avgs)
        avgHighestPP = sum(avgs) / float(len(avgs))
        randPostOutput = RAND_POST_OUTPUT_TEMPLATE.format(
            numModels=numModels, avgHighestPP=avgHighestPP,
            highestPP=highestPP)
        randPosteriorOutputFile.write(randPostOutput)


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
    parser.add_argument('-rp', '--randpostreps', required=True, type=int,
                        help='number of times each randomly generated ' +
                        'posterior is generated')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        required=True, help='File to write results.')
    parser.add_argument('-op', '--randpostout', type=argparse.FileType('w'),
                        required=True, help='File to write randomly ' +
                        'generated posterior data')
    parser.add_argument('-t', '--tolerance', required=True, type=float,
                        help='Proportion of simulation replicates that will' +
                        'be accepted')
    parser.add_argument('-d', '--deletepriors', action='store_true',
                        help='delete each prior after it has been generated')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display a lot of extra info')
    args = parser.parse_args()

    increment = 1
    if args.increment:
        increment = args.increment

    numModels = [x for x in range(args.lower, args.upper+1, increment)]

    if args.verbose:
        print(args)
        print (numModels)
        isVerbose = True

    main(args.masterModelFile, args.repetitions, numModels, args.output,
         args.tolerance, args.deletepriors, args.randpostreps,
         args.randpostout)
