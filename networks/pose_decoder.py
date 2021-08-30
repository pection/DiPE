# Based on the code of Monodepth2
# https://github.com/nianticlabs/monodepth2/blob/master/networks/pose_decoder.py

# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import torch
import torch.nn as nn
from collections import OrderedDict

torch.manual_seed(10)
torch.cuda.manual_seed(10)


class PoseDecoder(nn.Module):
    def __init__(self, num_ch_enc, num_poses_to_predict_for=1, stride=1):
        super(PoseDecoder, self).__init__()

        self.num_ch_enc = num_ch_enc

        self.num_poses_to_predict_for = num_poses_to_predict_for

        self.convs = OrderedDict()
        self.convs[("squeeze")] = nn.Conv2d(self.num_ch_enc[-1], 256, 1)
        self.convs[("pose", 0)] = nn.Conv2d(256, 256, 3, stride, 1)
        self.convs[("pose", 1)] = nn.Conv2d(256, 256, 3, stride, 1)
        self.convs[("pose", 2)] = nn.Conv2d(256, 6 * num_poses_to_predict_for, 1)

        self.relu = nn.ReLU()

        self.net = nn.ModuleList(list(self.convs.values()))

    def forward(self, input_features):
        last_features = input_features[-1]

        out = self.relu(self.convs["squeeze"](last_features))
        for i in range(3):
            out = self.convs[("pose", i)](out)
            if i != 2:
                out = self.relu(out)

        out = out.mean(3).mean(2)

        out = 0.01 * out.view(-1, self.num_poses_to_predict_for, 1, 6)

        axisangle = out[..., :3]
        translation = out[..., 3:]

        return axisangle, translation
