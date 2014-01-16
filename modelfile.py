import re
import random
import os

MODEL_NUMBER = r'_([0-9]+)'

# create ModelFile instance of master
# generate sample files based on masters models


class ModelFile():
    def __init__(self, fileName):
        self.modelFile = open(fileName, 'r')
        self._models = None  # list of model string
        self._numInstances = None  # number of models (lines in file)

    def __del__(self):
        self.modelFile.close()

    @property
    def models(self):
        if not self._models:
            self._models, self._numInstances = getModelsAndCountInstances(self)
        return self._models

    @models.setter
    def models(self, value):
        self._models = list(value)

    @property
    def numInstances(self):
        if not self._numInstances:
            self._models, self._numInstances = getModelsAndCountInstances(self)
        return self._numInstances

    def write(self, str):
        self.modelFile.write(str)
        if self._numInstances:
            self._numInstances += 1
        else:
            self._numInstances = 1

    def close(self):
        self.modelFile.close()

    def __iter__(self):
        self.modelFile.seek(0)
        for line in self.modelFile:
            yield line

    def removeRandomInstance(self):
        ''' Alters modelFile to have one less random instance (line).

        Arguments:
            modelFile: An open file (for reading) that will be modified to
                contain one less line. File closed after.
            numInstances: The number of instances (lines) in modelFile.

        Returns:
            The removed instance (line).
        '''
        instanceToRemove = random.randrange(self.numInstances)
        removedInstance = None
        modelFileName = self.modelFile.name
        tempModelFileName = modelFileName + '.temp'

        self.modelFile.seek(0)
        tempModelFile = open(tempModelFileName, 'w')

        for i, line in enumerate(self.modelFile):
            if i == instanceToRemove:
                removedInstance = line
            else:
                tempModelFile.write(line)

        tempModelFile.close()
        self.modelFile.close()
        os.rename(tempModelFileName, modelFileName)

        self.modelFile = open(modelFileName, 'r')
        self._numInstances -= 1

        return removedInstance


def getModelsAndCountInstances(modelFile):
    ''' Generates list of all models in a file and counts number of instances.

    Reads through the modelFile and produces a list of the models that
    occur in the file. If duplicates exist in the file, each model will
    exist in the list once.

    Note:
        modelFile has each line formatted as:
            '_[0-9]+.+\n'
    '''

    models = set()
    for i, line in enumerate(modelFile):
        modelMatch = re.match(MODEL_NUMBER, line)
        if modelMatch:
            models.add(modelMatch.group(1))

    return list(models), i + 1


def sampleNModels(models, n):
    ''' Returns a random subset of self.modelList. '''

    if n <= len(models):
        return random.sample(models, n)


def generateFileWithModels(generatedFileName, sourceModelFile, modelList):
    ''' Generates a ModelFile of all instances of models in modelList.

    Arguments:
        generatedFileName: File to which contents will be written and ModelFile
            instance will be created.
        sourceModelFile: the ModelFile instance from which model instances in
            model list will be read.
        modelList: List of strings of desired models.

    Returns:
        ModelFile containing all instances of models in modelList.
    '''
    generatedModelFile = open(generatedFileName, 'w')

    for line in sourceModelFile:
        modelMatch = re.match(MODEL_NUMBER, line)
        if modelMatch:
            if modelMatch.group(1) in modelList:
                generatedModelFile.write(line)

    generatedModelFile.close()

    generatedModelFile = ModelFile(generatedFileName)
    generatedModelFile.models = modelList

    return generatedModelFile


def generateFileWithNModels(sourceModelFile, generatedFileName, n):
    ''' Generates a file with n random models from sourceModelFile.

    Arguments:
        sourceModelFile: the source of the models and instances to be added to
            generatedFile
        generatedFileName: the name of the file that will be generated
        n: (integer) number of models to include
    '''
    modelList = sampleNModels(sourceModelFile.models, n)
    generatedModelFile = generateFileWithModels(generatedFileName,
                                                sourceModelFile, modelList)

    return generatedModelFile

if __name__ == '__main__':
    masterModelFile = ModelFile('test.txt')
    genFile = generateFileWithNModels(masterModelFile, 'genFile3.txt', 3)
    print(genFile.models, genFile.numInstances)

    # count lines in file before
    print('numLines before: ')
    os.system('wc -l {}'.format(genFile.modelFile.name))

    # count lines in file after
    pod = genFile.removeRandomInstance()
    print('numLines after:')
    os.system('wc -l {}'.format(genFile.modelFile.name))

    print(pod)
