# -*- coding: utf-8 -*-

import os
from circleci_helpers.matrix.matrix import Matrix


def main():
    matrix = Matrix()
    total_nodes = int(os.environ.get('CIRCLE_NODE_TOTAL', 1))
    node_num = int(os.environ.get('CIRCLE_NODE_INDEX', 0))

    # Stick execution to devision remainder (round-robin node choice)
    for i in range(0, len(matrix.config['env'])):
        rrnum = i % total_nodes
        if rrnum == node_num:
            matrix.execute(step=i)
