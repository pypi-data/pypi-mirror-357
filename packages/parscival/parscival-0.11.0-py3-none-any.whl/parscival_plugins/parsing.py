# -*- coding: utf-8 -*-
# module parsing.py
#
# Copyright (c) 2021  CorTexT Platform
# Copyright (c) 2021  Cogniteva SAS
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ---------------------------------------------------------------------------
import pluginlib                                  #
import logging                                    #
# ---------------------------------------------------------------------------
from parscival_plugins.utils.logging_mixin import LoggingMixin
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
@pluginlib.Parent('parsing')
class Parser(LoggingMixin):
  """
  Base class for parsing tasks with logging capabilities.
  """
  _alias_ = 'parsing'
  _version_ = '1.0.0'

  @staticmethod
  @pluginlib.abstractmethod
  def init(parsing_spec, **params):
    pass

  @staticmethod
  @pluginlib.abstractmethod
  def can_parse(parsing_spec, dataset_info, document_info, document_line, **params):
    pass

  @staticmethod
  @pluginlib.abstractmethod
  def buffer_restart(parsing_spec, dataset_info, document_info, document_line, **params):
    pass

  @staticmethod
  @pluginlib.abstractmethod
  def get_next_record(parscival_spec, dataset_info, dataset):
    pass

  @staticmethod
  @pluginlib.abstractmethod
  def process(parsing_spec: dict, dataset_info: dict, document_info: dict, **params)  -> bool:
    pass
