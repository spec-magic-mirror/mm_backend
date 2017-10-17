import torch
import torch.nn as nn
import torch.utils.model_zoo as model_zoo
import math
import os
import cv2
import json
import numpy as np
from pprint import pprint
from torch.autograd import Variable
from torch.utils.data import DataLoader
import torch.nn.functional as F

class VGG(nn.Module):

    def __init__(self, features, num_classes=2):
        super(VGG, self).__init__()
        self.features = features
        self.classifier = nn.Sequential(
            nn.Linear(512*2*2, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, num_classes),
        )
        self._initialize_weights()

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        #print(x.size())
        x = self.classifier(x)
        return F.softmax(x)

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                m.weight.data.normal_(0, 0.01)
                m.bias.data.zero_()

class MoleModel():
    def __init__(self, pretrained_path):
        # make vgg16_bn    
        layers = []
        in_channels = 1
        cfg = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M']
        for v in cfg:
            if v == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
                in_channels = v
        nn_layers = nn.Sequential(*layers)

        self.vgg = VGG(nn_layers)
        self.vgg.load_state_dict(torch.load(pretrained_path))
    
    def filter_moles(self, thresh, test_data):
        dataloader = DataLoader(test_data, batch_size=1, shuffle=False, num_workers=2)
        results = []
        for i, data in enumerate(dataloader):
            # get the inputs
            inputs, labels, coords = data['predicted'], data['ground_truth'], data['coords']
        
            # wrap them in Variable
            inputs, target = Variable(inputs.float()).view(-1,1,64,64), \
                Variable(labels.float()).view(-1, 2)

            # forward + backward + optimize
            test_outputs = self.vgg(inputs)

            if test_outputs.data.numpy()[0][1] >= thresh:
                results.append([test_data[i]['coords'], test_outputs.data.numpy()[0][1]])
        return results

#for testing
#mm = MoleModel("mole_vgg.pth")
