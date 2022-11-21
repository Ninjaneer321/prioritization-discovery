import pandas as pd
import pandasql as ps

from .config import DELAYED_PREFIX, PRIORITIZED_PREFIX


def discover_prioritized_instances(
        event_log: pd.DataFrame,
        attributes: list[str]
) -> pd.DataFrame:
    """
    Discover activity instances that are prioritized over others. This means they are not being executed following a FIFO order, i.e., in
    the order they are enabled.

    :param event_log:   event log to analyze.
    :param attributes:  list of column names for the attributes to use as features for the prioritization.

    :return: a pd.DataFrame with each of the observations (positive and negative) of prioritization found in the event log.
    """
    # Dictionaries with the attribute name and delayed/prioritized renamed values
    delayed_attributes = {attribute: add_prefix(DELAYED_PREFIX, attribute) for attribute in attributes}
    prioritized_attributes = {attribute: add_prefix(PRIORITIZED_PREFIX, attribute) for attribute in attributes}
    # Define columns for the SQL query
    columns = [
                  "delayed.{} as {}".format(attribute, delayed_attributes[attribute]) for attribute in delayed_attributes
              ] + [
                  "prioritized.{} as {}".format(attribute, prioritized_attributes[attribute]) for attribute in prioritized_attributes
              ]
    # Query the prioritized and delayed events
    prioritizations = ps.sqldf("""
        SELECT {}
        FROM event_log as delayed, event_log as prioritized
        WHERE (delayed.enabled_time < prioritized.enabled_time and 
                delayed.start_time > prioritized.start_time and 
                delayed.Resource = prioritized.Resource)
    """.format(", ".join(columns)), locals())
    # Split the log so each activity instance is an observation
    prioritized_instances = _split_to_individual_observations(
        prioritizations,
        list(delayed_attributes.values()),
        list(prioritized_attributes.values()),
        'outcome'
    )
    # Return extended observations
    return prioritized_instances


def _split_to_individual_observations(
        event_log: pd.DataFrame,
        delayed_attributes: list[str],
        prioritized_attributes: list[str],
        outcome: str
) -> pd.DataFrame:
    """
    Split the received pd.DataFrame with the prioritized instances (delayed and prioritized) into positive (prioritized) and negative
    (delayed) ones.

    :param event_log:               event log to split into delayed and prioritized instances.
    :param delayed_attributes:      list of column names of attributes for delayed observations.
    :param prioritized_attributes:  list of column names of attributes for prioritized observations.
    :param outcome                  ID of the column with the variable to predict (1 positive, 0 negative).

    :return:
    """
    # Get the columns of the delayed instances
    delayed_instances = event_log[delayed_attributes].rename(
        {
            column_name: remove_prefix(DELAYED_PREFIX, column_name)
            for column_name in delayed_attributes
        },
        axis=1
    )
    delayed_instances[outcome] = 0
    # Get the columns of the prioritized instances
    prioritized_instances = event_log[prioritized_attributes].rename(
        {
            column_name: remove_prefix(PRIORITIZED_PREFIX, column_name)
            for column_name in prioritized_attributes
        },
        axis=1
    )
    prioritized_instances[outcome] = 1
    # Return both individual delayed and prioritized instances (don't reset index
    return pd.concat([delayed_instances, prioritized_instances])


def add_prefix(prefix: str, name: str) -> str:
    return "{}_{}".format(prefix, name)


def remove_prefix(prefix: str, name: str) -> str:
    if name.startswith(prefix):
        return name[len(prefix) + 1:]
    else:
        return name
