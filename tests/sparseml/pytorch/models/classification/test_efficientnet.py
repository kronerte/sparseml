# Copyright (c) 2021 - present / Neuralmagic, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Callable, Union

import pytest
import torch

from sparseml.pytorch.models import ModelRegistry, efficientnet_b0, efficientnet_b4
from tests.sparseml.pytorch.models.utils import compare_model


@pytest.mark.skipif(
    os.getenv("NM_ML_SKIP_PYTORCH_TESTS", False),
    reason="Skipping pytorch tests",
)
@pytest.mark.skipif(
    os.getenv("NM_ML_SKIP_MODEL_TESTS", False),
    reason="Skipping model tests",
)
@pytest.mark.parametrize(
    "key,pretrained,test_input,match_const,model_args",
    [
        ("efficientnet_b0", False, True, efficientnet_b0, {}),
        ("efficientnet_b0", "base", False, efficientnet_b0, {}),
        ("efficientnet_b0", "arch-moderate", False, efficientnet_b0, {"se_mod": True}),
        ("efficientnet_b4", False, True, efficientnet_b4, {}),
        ("efficientnet_b4", "base", False, efficientnet_b4, {}),
        ("efficientnet_b4", "arch-moderate", False, efficientnet_b4, {"se_mod": True}),
    ],
)
def test_efficientnet(
    key: str,
    pretrained: Union[bool, str],
    test_input: bool,
    match_const: Callable,
    model_args: dict,
):
    model = ModelRegistry.create(key, pretrained, **model_args)
    diff_model = match_const(**model_args)

    if pretrained:
        compare_model(model, diff_model, same=False)
        match_model = ModelRegistry.create(key, pretrained, **model_args)
        compare_model(model, match_model, same=True)

    if test_input:
        input_shape = ModelRegistry.input_shape(key)
        batch = torch.randn(1, *input_shape)
        model = model.eval()
        out = model(batch)
        assert isinstance(out, tuple)
        for tens in out:
            assert tens.shape[0] == 1
            assert tens.shape[1] == 1000
