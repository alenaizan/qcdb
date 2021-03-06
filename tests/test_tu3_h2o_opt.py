from utils import *
from addons import *

import qcdb

nucenergy =   9.3007948234239  #TEST
refenergy = -76.0270535127645  #TEST

def test_1a():
    h2o = qcdb.set_molecule("""
      O
      H 1 0.96
      H 1 0.96 2 104.5
    """)

    qcdb.optking('scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST

def test_1b():
    h2o = qcdb.set_molecule("""
      O
      H 1 0.96
      H 1 0.96 2 104.5
    """)

    qcdb.optking('c4-scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST

@using_geometric
def test_2a():
    h2o = qcdb.set_molecule("""
      O
      H 1 0.96
      H 1 0.96 2 104.5
    """)

    qcdb.geometric('scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST

@using_geometric
def test_2b():
    h2o = qcdb.set_molecule("""
      O
      H 1 0.96
      H 1 0.96 2 104.5
    """)

    qcdb.geometric('c4-scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST


@using_geometric
def test_2c():
    h2o = qcdb.set_molecule("""
O 0.          0.         -0.12
H 0.         -1.52  1.04
H 0.          1.52  1.04
units au
    """)

    qcdb.geometric('scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST

@using_geometric
def test_2d():
    h2o = qcdb.set_molecule("""
O 0.          0.         -0.12
H 0.         -1.52  1.04
H 0.          1.52  1.04
units au
    """)

    qcdb.geometric('c4-scf/cc-pvdz')

    assert compare_values(nucenergy, h2o.nuclear_repulsion_energy(), 3, "Nuclear repulsion energy")    #TEST
    assert compare_values(refenergy, qcdb.get_variable("CURRENT ENERGY"), 4, "Reference energy") #TEST


