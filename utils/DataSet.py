# -*- coding: utf-8 -*-
#/usr/bin/python2


from tensorflow.python.platform import tf_logging as logging
import pdb
import numpy as np
import tensorflow as tf
import os
import xlrd
import csv

# Visual Features
# params: 
#     
class DataSet(object):
    def __init__(self, params):

        print("Loading data...")

        self.params = params 
        self.featureDir = os.path.join("data", params['feature_dir'], "features") 
        self.annotationDir = os.path.join("data", params['annotation_dir'], "annotations") 

        featureFile = os.path.join(params['uploaded_dir'], 'features.npy')
        annotationFile = os.path.join(params['uploaded_dir'], 'annotations.npy')
        if os.path.exists(featureFile) and os.path.exists(annotationFile) :
            print("---- npy files founded!!    (If you want to reset dataset, please delete those files first.)")
            self.featureData = np.load(featureFile)
            self.annotationData = np.load(annotationFile)
            return 

        movieList = params['movies']
        if movieList == None:
            dirList = os.listdir(self.featureDir) # all directorys 
            movieList = [] 
            for movie in dirList:
                if os.path.isdir(os.path.join(self.featureDir, movie)):
                    movieList.append(movie)

        movieFeatures = {}
        movieAnnotations = {}
        for movie in movieList:
            movieFeatures[movie], movieAnnotations[movie] = self.__loadVideoData(movie, self.params['visual_features'])
        self.featureData = np.concatenate(list(movieFeatures.values()), axis=0)
        self.annotationData = np.concatenate(list(movieAnnotations.values()), axis=0)

        if not os.path.exists(params['uploaded_dir']):
            os.mkdir(params['uploaded_dir'])
        np.save(featureFile,self.featureData)
        np.save(annotationFile,self.annotationData)

    def __loadVideoData(self, videoName, featureParams):

        print("---- Loading data from video: ''" + videoName +"''")
        features = {} 
        for featureName in featureParams:
            if(featureParams[featureName] == True):
                features[featureName] = self.__loadFeature(videoName, featureName) 
        annotations = self.__loadAnnotation(videoName)
        features = np.concatenate(list(features.values()), axis=1)[0:annotations.shape[0]*5+5,:].transpose(1, 0)
        features = features.reshape(features.shape[0], features.shape[1]//5, 5).sum(2).transpose(1, 0)
        features = features[1:features.shape[0],:]+features[0:features.shape[0]-1,:] 

        return features, annotations

    def __loadFeature(self, videoName, featureName):

        print("---- ---- Loading feature: " + featureName)

        featurePath = os.path.join(self.featureDir, videoName, featureName) 
        if not os.path.exists(featurePath):
            return 
        num = 1 ;
        feature = [] ;
        while True:
            fileName = videoName+"-"+str(num).zfill(5)+"_"+featureName+".txt" 
            filePath = os.path.join(featurePath, fileName) 
            if not os.path.exists(filePath):
                break 
            feature.append(np.array(open(filePath, 'r').read().split(','))) 
            num = num + 1
        return np.array(feature, dtype=np.float32)

    def __loadAnnotation(self, videoName):
        print("---- ---- Loading annotation")

        annotationPath = os.path.join(self.annotationDir, videoName+"-MEDIAEVAL2017-valence_arousal.txt") 
        if not os.path.exists(annotationPath):
            return 

        annotation = []

        with open(annotationPath, newline='') as csvFile:
            csvReader = csv.reader(csvFile, delimiter='\t', quotechar='|')
            flag = 0
            for row in csvReader:
                if flag == 0:
                    flag = 1
                    continue
                annotation.append([float(row[2]), float(row[3])])

        return np.array(annotation, dtype=np.float32)

'''
def load_data(dir_):
    # Target indices
    indices = load_target(dir_ + Params.target_dir)

    # Load question data
    print("Loading question data...")
    q_word_ids, _ = load_word(dir_ + Params.q_word_dir)
    q_char_ids, q_char_len, q_word_len = load_char(dir_ + Params.q_chars_dir)

    # Load passage data
    print("Loading passage data...")
    p_word_ids, _ = load_word(dir_ + Params.p_word_dir)
    p_char_ids, p_char_len, p_word_len = load_char(dir_ + Params.p_chars_dir)

    # Get max length to pad
    p_max_word = Params.max_p_len#np.max(p_word_len)
    p_max_char = Params.max_char_len#,max_value(p_char_len))
    q_max_word = Params.max_q_len#,np.max(q_word_len)
    q_max_char = Params.max_char_len#,max_value(q_char_len))

    # pad_data
    print("Preparing data...")
    p_word_ids = pad_data(p_word_ids,p_max_word)
    q_word_ids = pad_data(q_word_ids,q_max_word)
    p_char_ids = pad_char_data(p_char_ids,p_max_char,p_max_word)
    q_char_ids = pad_char_data(q_char_ids,q_max_char,q_max_word)

    # to numpy
    indices = np.reshape(np.asarray(indices,np.int32),(-1,2))
    p_word_len = np.reshape(np.asarray(p_word_len,np.int32),(-1,1))
    q_word_len = np.reshape(np.asarray(q_word_len,np.int32),(-1,1))
    # p_char_len = pad_data(p_char_len,p_max_word)
    # q_char_len = pad_data(q_char_len,q_max_word)
    p_char_len = pad_char_len(p_char_len, p_max_word, p_max_char)
    q_char_len = pad_char_len(q_char_len, q_max_word, q_max_char)

    for i in range(p_word_len.shape[0]):
        if p_word_len[i,0] > p_max_word:
            p_word_len[i,0] = p_max_word
    for i in range(q_word_len.shape[0]):
        if q_word_len[i,0] > q_max_word:
            q_word_len[i,0] = q_max_word

    # shapes of each data
    shapes=[(p_max_word,),(q_max_word,),
            (p_max_word,p_max_char,),(q_max_word,q_max_char,),
            (1,),(1,),
            (p_max_word,),(q_max_word,),
            (2,)]

    return ([p_word_ids, q_word_ids,
            p_char_ids, q_char_ids,
            p_word_len, q_word_len,
            p_char_len, q_char_len,
            indices], shapes)

def get_dev():
    devset, shapes = load_data(Params.dev_dir)
    indices = devset[-1]
    # devset = [np.reshape(input_, shapes[i]) for i,input_ in enumerate(devset)]

    dev_ind = np.arange(indices.shape[0],dtype = np.int32)
    np.random.shuffle(dev_ind)
    return devset, dev_ind

def get_batch(is_training = True):
    """Loads training data and put them in queues"""
    with tf.device('/cpu:0'):
        # Load dataset
        input_list, shapes = load_data(Params.train_dir if is_training else Params.dev_dir)
        indices = input_list[-1]

        train_ind = np.arange(indices.shape[0],dtype = np.int32)
        np.random.shuffle(train_ind)

        size = Params.data_size
        if Params.data_size > indices.shape[0] or Params.data_size == -1:
            size = indices.shape[0]
        ind_list = tf.convert_to_tensor(train_ind[:size])

        # Create Queues
        ind_list = tf.train.slice_input_producer([ind_list], shuffle=True)

        @producer_func
        def get_data(ind):
            return [np.reshape(input_[ind], shapes[i]) for i,input_ in enumerate(input_list)]

        data = get_data(inputs=ind_list,
                        dtypes=[np.int32]*9,
                        capacity=Params.batch_size*32,
                        num_threads=6)

        # create batch queues
        batch = tf.train.batch(data,
                                shapes=shapes,
                                num_threads=2,
                                batch_size=Params.batch_size,
                                capacity=Params.batch_size*32,
                                dynamic_pad=True)

    return batch, size // Params.batch_size
'''