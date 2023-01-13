import pandas as pd

from prioritization_discovery.rules import discover_prioritization_rules


def test_discover_prioritization_rules():
    # Given a set of prioritizations
    prioritizations = pd.DataFrame(
        data=[
            ['B', 0], ['B', 0], ['B', 0],
            ['B', 0], ['B', 0], ['B', 0],
            ['C', 1], ['C', 1], ['C', 1],
            ['C', 1], ['C', 1], ['C', 1]
        ],
        index=[0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5],
        columns=['Activity', 'outcome']
    )
    # Discover their rules
    prioritization_rules = discover_prioritization_rules(prioritizations, 'outcome')
    # Assert the rules
    assert prioritization_rules == [
        {
            'priority_level': 1,
            'rules': [
                [
                    {
                        'attribute': 'Activity',
                        'condition': '=',
                        'value': 'C'
                    }
                ]
            ]
        }
    ]


def test_discover_prioritization_rules_with_extra_attribute():
    # Given a set of prioritizations
    prioritizations = pd.DataFrame(
        data=[
            ['A', 500, 0],
            ['A', 500, 0],
            ['A', 500, 1],
            ['B', 100, 0],
            ['B', 100, 0],
            ['B', 100, 0],
            ['B', 100, 0],
            ['B', 100, 0],
            ['B', 500, 1],
            ['B', 1000, 1],
            ['B', 1000, 1],
            ['C', 100, 0],
            ['C', 500, 1],
            ['C', 500, 1],
            ['C', 1000, 1],
            ['C', 1000, 1]
        ],
        index=[0, 1, 2, 2, 3, 4, 5, 6, 4, 0, 3, 7, 6, 7, 1, 5],
        columns=['Activity', 'loan_amount', 'outcome']
    )
    # Discover their rules
    prioritization_rules = discover_prioritization_rules(prioritizations, 'outcome')
    # Assert the rules
    assert prioritization_rules == prioritization_rules == [
        {
            'priority_level': 2,
            'rules': [
                [
                    {
                        'attribute': 'loan_amount',
                        'condition': '=',
                        'value': '1000'
                    }
                ]
            ]
        },
        {
            'priority_level': 1,
            'rules': [
                [
                    {
                        'attribute': 'loan_amount',
                        'condition': '=',
                        'value': '500'
                    }
                ]
            ]
        }
    ]


def test_discover_prioritization_rules_with_double_and_condition():
    # Given a set of prioritizations
    data = [
        [400, "high", 0], [1100, "high", 1],
        [1000, "low", 0], [1000, "high", 1],
        [1100, "low", 0], [1010, "high", 1],
        [500, "high", 0], [1300, "high", 1],
        [1300, "low", 0], [1100, "high", 1],
        [800, "high", 0], [1800, "high", 1],
        [510, "high", 0], [2000, "high", 1],
        [520, "low", 0], [900, "low", 1],
        [400, "high", 0], [700, "low", 1],
        [600, "low", 0], [800, "low", 1]
    ]
    indices = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
    # Multiply by 10 the observations to have enough population
    resize = 100
    data = data * resize
    num_indices = len(set(indices))
    indices = [index + (num_indices * i) for i in range(resize) for index in indices]
    # Create dataframe with observations
    prioritizations = pd.DataFrame(
        data=data,
        index=indices,
        columns=['loan_amount', 'importance', 'outcome']
    )
    # Discover their rules
    prioritization_rules = discover_prioritization_rules(prioritizations, 'outcome')
    # Assert the rules
    assert prioritization_rules == [
        {
            'priority_level': 2,
            'rules': [
                [
                    {
                        'attribute': 'importance',
                        'condition': '=',
                        'value': 'High'
                    },
                    {
                        'attribute': 'loan_amount',
                        'condition': '>=',
                        'value': '1000'
                    }
                ]
            ]
        },
        {
            'priority_level': 1,
            'rules': [
                [
                    {
                        'attribute': 'loan_amount',
                        'condition': '>=',
                        'value': '700'
                    }
                ]
            ]
        }
    ]
