import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pyarmour.attacks.fgsm import FGSM
from pyarmour.attacks.pgd import PGD
from pyarmour.attacks.deepfool import DeepFool
from pyarmour.utils import SimpleCNN

def test_fgsm_attack():
    model = SimpleCNN()
    x = np.random.random((1, 1, 28, 28)).astype(np.float32)
    y = np.array([0])
    
    attack = FGSM(model, epsilon=0.01)
    adv_x, _, _ = attack.generate(x, y)
    
    assert adv_x.shape == x.shape
    assert np.all(adv_x >= 0) and np.all(adv_x <= 1)
    assert np.linalg.norm(adv_x - x) > 0

def test_pgd_attack():
    model = SimpleCNN()
    x = np.random.random((1, 1, 28, 28)).astype(np.float32)
    y = np.array([0])
    
    attack = PGD(model, epsilon=0.01, alpha=0.01, steps=10)
    adv_x, _, _ = attack.generate(x, y)
    
    assert adv_x.shape == x.shape
    assert np.all(adv_x >= 0) and np.all(adv_x <= 1)
    assert np.linalg.norm(adv_x - x) > 0

def test_deepfool_attack():
    model = SimpleCNN()
    x = np.random.random((1, 1, 28, 28)).astype(np.float32)
    y = np.array([0])
    
    attack = DeepFool(model, max_iter=50)
    adv_x, _, _ = attack.generate(x, y)
    
    assert adv_x.shape == x.shape
    assert np.all(adv_x >= 0) and np.all(adv_x <= 1)
    assert np.linalg.norm(adv_x - x) > 0


