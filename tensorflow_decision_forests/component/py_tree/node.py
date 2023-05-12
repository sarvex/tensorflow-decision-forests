# Copyright 2021 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Nodes (leaf and non-leafs) in a tree."""

import abc
from typing import Optional

import six

from tensorflow_decision_forests.component.py_tree import condition as condition_lib
from tensorflow_decision_forests.component.py_tree import value as value_lib
from yggdrasil_decision_forests.dataset import data_spec_pb2
from yggdrasil_decision_forests.model.decision_tree import decision_tree_pb2

AbstractCondition = condition_lib.AbstractCondition
AbstractValue = value_lib.AbstractValue


@six.add_metaclass(abc.ABCMeta)
class AbstractNode(object):
  """A decision tree node."""


class LeafNode(AbstractNode):
  """A leaf node i.e. the node containing a prediction/value/output."""

  def __init__(self, value: AbstractValue):
    self._value = value

  def __repr__(self):
    return f"LeafNode(value={self._value})"

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._value = value


class NonLeafNode(AbstractNode):
  """A non-leaf node i.e.

  a node containing a split/condition.

  Attrs:
    condition: The binary condition of the node.
    pos_child: The child to visit when the condition is true.
    neg_child: The child to visit when the condition is false.
    value: The value/prediction/output of the node if it was a leaf. Not used
      during prediction.
  """

  def __init__(self,
               condition: AbstractCondition,
               pos_child: Optional[AbstractNode] = None,
               neg_child: Optional[AbstractNode] = None,
               value: Optional[AbstractValue] = None):

    self._condition = condition
    self._pos_child = pos_child
    self._neg_child = neg_child
    self._value = value

  @property
  def condition(self):
    return self._condition

  @condition.setter
  def condition(self, value):
    self._condition = value

  @property
  def pos_child(self):
    return self._pos_child

  @pos_child.setter
  def pos_child(self, value):
    self._pos_child = value

  @property
  def neg_child(self):
    return self._neg_child

  @neg_child.setter
  def neg_child(self, value):
    self._neg_child = value

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._value = value

  def __repr__(self):
    text = f"NonLeafNode(condition={str(self._condition)}"
    if self._pos_child is not None:
      text += f", pos_child={self._pos_child}"
    else:
      text += ", pos_child=None"
    if self._neg_child is not None:
      text += f", neg_child={self._neg_child}"
    else:
      text += ", neg_child=None"
    if self._value is not None:
      text += f", value={self._value}"
    text += ")"
    return text


def core_node_to_node(
    core_node: decision_tree_pb2.Node,
    dataspec: data_spec_pb2.DataSpecification) -> AbstractNode:
  """Converts a core node (proto format) into a python node."""

  if core_node.HasField("condition"):
    # Non leaf
    return NonLeafNode(
        condition=condition_lib.core_condition_to_condition(
            core_node.condition, dataspec),
        value=value_lib.core_value_to_value(core_node))

  # Leaf
  value = value_lib.core_value_to_value(core_node)
  if value is None:
    raise ValueError("Leaf node should have a value")
  return LeafNode(value)


def node_to_core_node(
    node: AbstractNode,
    dataspec: data_spec_pb2.DataSpecification) -> decision_tree_pb2.Node:
  """Converts a python node into a core node (proto format)."""

  core_node = decision_tree_pb2.Node()
  if isinstance(node, NonLeafNode):
    condition_lib.set_core_node(node.condition, dataspec, core_node)
    if node.value is not None:
      value_lib.set_core_node(node.value, core_node)

  elif isinstance(node, LeafNode):
    value_lib.set_core_node(node.value, core_node)

  else:
    raise NotImplementedError()

  return core_node
