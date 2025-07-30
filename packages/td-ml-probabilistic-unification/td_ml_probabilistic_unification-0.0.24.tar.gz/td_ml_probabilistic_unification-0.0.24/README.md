# td-ml-probabilistic-unification

## Introduction

The `td-ml-probabilistic-unification` is a Python package designed for Scalable Probabilistic Unification within the Treasure Data environment. It provides functionality to unify and cluster records probabilistically based on various attributes, making it useful for a wide range of data integration and analysis tasks.

In order to perform probabilistic unification using this package, you should have an input table containing the data you want to unify. The package will use the specified configuration parameters to perform probabilistic unification and generate an output table with clustered records.

## Configuration
Before using this package, you need to set the following environment variables:

```python
# Configuration variables
TD_SINK_DATABASE = os.environ.get('TD_SINK_DATABASE')
TD_API_KEY = os.environ.get('TD_API_KEY')
TD_API_SERVER = os.environ.get('TD_API_SERVER')

## Profiles id column name
id_col = os.environ.get('id_col')
## cluster id column name by default : cluster_id
cluster_col_name = os.environ.get('cluster_col_name')

## convergence threshold for SoftImpute in case of missing values

convergence_threshold = float(os.environ.get('convergence_threshold'))

## The cluster threshold is a parameter that determines the similarity level required for two entities to be considered part of the same cluster. When performing hierarchical clustering, entities are merged into clusters based on their similarity. The cluster threshold sets a limit on how similar two entities must be to belong to the same cluster.

## Example: If set to 0.9, entities with a similarity level of 0.9 or higher will be grouped into the same cluster.
cluster_threshold = float(os.environ.get('cluster_threshold'))

## Type of string matching technique used.
string_type = os.environ.get('string_type')

## Binary variables to fill missing values or not in adjacency matrix
fill_missing = os.environ.get('fill_missing')

## it is fetched column dictionary with weightage which are being used in Unification
feature_dict = json.loads(os.environ.get('feature_dict'))

## blocking and output table name
blocking_table = os.environ.get('blocking_table')
output_table = os.environ.get('output_table')

## number of records to be used for a single docker image , below parms are being used for wf optimisation
record_limit = int(os.environ.get('record_limit'))
lower_limit = int(os.environ.get('lower_limit'))
upper_limit = int(os.environ.get('upper_limit'))
range_index = os.environ.get('range_index')
paralelism = os.environ.get('paralelism')
input_table = blocking_table

'''python




Thank you for choosing td-ml-probabilistic-unification for your probabilistic unification needs! 📊🚀

`Copyright © 2022 Treasure Data, Inc. (or its affiliates). All rights reserved`
