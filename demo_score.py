import torch
from modules.network import get_network
from modules.CONTRIQUE_model import CONTRIQUE_model
from torchvision import transforms
import numpy as np

import os
import argparse
import pickle

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from modules.CONTRIQUE_model import CONTRIQUE_model
from modules.network import get_network

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

def main(args):
    # load image
    image = Image.open(args.im_path)
    
    # downscale image by 2
    sz = image.size
    image_2 = image.resize((sz[0] // 2, sz[1] // 2))
    
    # transform to tensor #不太懂fanld
    image = transforms.ToTensor()(image).unsqueeze(0).cuda()
    image_2 = transforms.ToTensor()(image_2).unsqueeze(0).cuda()
    
    # load CONTRIQUE Model
    encoder = get_network('resnet50', pretrained=False)
    model = CONTRIQUE_model(args, encoder, 2048)
    model.load_state_dict(torch.load(args.model_path, map_location=args.device.type))
    model = model.to(args.device)
    
    # extract features
    model.eval()
    with torch.no_grad():
        _,_, _, _, model_feat, model_feat_2, _, _ = model(image, image_2)
    feat = np.hstack((model_feat.detach().cpu().numpy(),\
                                model_feat_2.detach().cpu().numpy()))
    
    # load regressor model
    regressor = pickle.load(open(args.linear_regressor_path, 'rb'))
    score = regressor.predict(feat)[0]
    print(score)

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--im_path', type=str, \
                        default='sample_images/33.bmp', \
                        help='Path to image', metavar='')
    parser.add_argument('--model_path', type=str, \
                        default='models/CONTRIQUE_checkpoint25.tar', \
                        help='Path to trained CONTRIQUE model', metavar='')
    parser.add_argument('--linear_regressor_path', type=str, \
                        default='models/CLIVE.save', \
                        help='Path to trained linear regressor', metavar='')
    args = parser.parse_args()
    args.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)
