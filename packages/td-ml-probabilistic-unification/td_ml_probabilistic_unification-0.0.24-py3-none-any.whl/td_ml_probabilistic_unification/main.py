
import os
import sys

packages = [
    "numpy==1.26.4",
    "fancyimpute==0.7.0",
    "strsim==0.0.3", 
    "networkx==2.5",
    "scipy==1.13.1",
    "fuzzywuzzy==0.18.0",
    "python-Levenshtein==0.21.1"
   
]

os.system(f"{sys.executable} -m pip install {' '.join(packages)}")

import json
import pandas as pd
import numpy as np
import datetime
from .data_loader import TDConnector
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

####----Defining Variables-------#####
TD_SINK_DATABASE=os.environ.get('TD_SINK_DATABASE')
TD_API_KEY=os.environ.get('TD_API_KEY')
TD_API_SERVER=os.environ.get('TD_API_SERVER')

id_col=os.environ.get('id_col')
cluster_col_name=os.environ.get('cluster_col_name')
convergence_threshold = float(os.environ.get('convergence_threshold', 0.01))
cluster_threshold = float(os.environ.get('cluster_threshold', 0.65))
string_type = os.environ.get('string_type', 'jarowinkler')
fill_missing = os.environ.get('fill_missing', 'True').lower() == 'true'

feature_dict=json.loads(os.environ.get('feature_dict'))
blocking_table=os.environ.get('blocking_table')
output_table=os.environ.get('output_table')

record_limit=int(os.environ.get('record_limit'))
lower_limit=int(os.environ.get('lower_limit'))
upper_limit=int(os.environ.get('upper_limit'))
range_index=os.environ.get('range_index')
paralelism = os.environ.get('paralelism')

# New parameters for improved clustering
clustering_method = os.environ.get('clustering_method', 'connected_components')  # 'strict_hierarchical', 'connected_components', 'hierarchical'
min_coverage = float(os.environ.get('min_coverage', '0.5'))  # Minimum feature coverage required
min_cluster_size = int(os.environ.get('min_cluster_size', '2'))  # Minimum cluster size to output

input_table=blocking_table

feature_cols="block_key, " + id_col
for feature in feature_dict:
    name=feature['name']
    feature_cols=feature_cols +  ","  + name

query= f"Select { feature_cols }  from {input_table} WHERE rnk > {lower_limit} and rnk <= {upper_limit}"
print(query)

from td_ml_probabilistic_unification.get_similarity import *
from td_ml_probabilistic_unification.get_cluster import *


def validate_feature_weights(feature_dict):
    """
    Validate and normalize feature weights to ensure they sum to 1.0.
    
    Args:
        feature_dict: List of feature dictionaries
    
    Returns:
        Validated feature dictionary with normalized weights
    """
    total_weight = sum(float(feature['weight']) for feature in feature_dict)
    
    if abs(total_weight - 1.0) > 0.01:  # Allow small tolerance
        print(f"Warning: Feature weights sum to {total_weight}, normalizing to 1.0")
        
        # Normalize weights
        for feature in feature_dict:
            feature['weight'] = float(feature['weight']) / total_weight
    
    return feature_dict


def apply_quality_filters(df_clusters, sim_data, id_col, cluster_col_name, 
                         min_cluster_size=2, min_avg_similarity=None):
    """
    Apply quality filters to remove low-quality clusters.
    
    Args:
        df_clusters: DataFrame with cluster assignments
        sim_data: Original similarity data
        id_col: ID column name
        cluster_col_name: Cluster column name
        min_cluster_size: Minimum number of records in cluster
        min_avg_similarity: Minimum average similarity in cluster
    
    Returns:
        Filtered DataFrame
    """
    if min_avg_similarity is None:
        min_avg_similarity = cluster_threshold
    
    # Count cluster sizes
    cluster_sizes = df_clusters[cluster_col_name].value_counts()
    valid_clusters = cluster_sizes[cluster_sizes >= min_cluster_size].index
    
    # Filter by cluster size
    df_filtered = df_clusters[df_clusters[cluster_col_name].isin(valid_clusters)].copy()
    
    # Filter by average similarity if specified
    if min_avg_similarity > 0:
        df_filtered = df_filtered[
            df_filtered['avg_cluster_similarity'] >= min_avg_similarity
        ].copy()
    
    # Add quality metrics
    df_filtered['cluster_size'] = df_filtered[cluster_col_name].map(cluster_sizes)
    
    return df_filtered


def execute_main():
    # Validate and normalize feature weights
    normalized_feature_dict = validate_feature_weights(feature_dict)
    
    dup_data = TDConnector.read(query,TD_SINK_DATABASE,input_table,TD_API_KEY,TD_API_SERVER)

    #--- Generating all the combinations of pairs within each block
    #--- and then dropping pair of same id e.g. when id=A , self pair would be id_1=A and id_2=A so its like A-A(which we dont need to calculate #    similarities )
    sim_data=pd.merge(dup_data,dup_data,on='block_key',suffixes=('_1','_2')).drop_duplicates()

    #--- Dropping one of duplicate pairs e.g id_1=A and id_2= B ==> there will be two combinations A-B and B-A but we only need any one of them. so dropping one of them here
    sim_data=sim_data[sim_data[id_col+'_1']>sim_data[id_col+'_2']]

    # Calculate similarities with improved missing value handling
    sim_data, sim_feat_list, col_names, weights = get_similarities(
        sim_data, 
        normalized_feature_dict, 
        string_type, 
        min_coverage=min_coverage
    )

    logger.info(f"Generated {len(sim_data)} record pairs")
    logger.info(f"Pairs above threshold ({cluster_threshold}): {len(sim_data[sim_data['score'] >= cluster_threshold])}")
    logger.info(f"Average feature coverage: {sim_data['feature_coverage'].mean():.2f}")

        # Filter pairs that don't meet minimum requirements
    valid_pairs = sim_data[
        (sim_data['score'] >= cluster_threshold) & 
        (sim_data['feature_coverage'] >= min_coverage)
    ]

    logger.info(f"Valid pairs after filtering: {len(valid_pairs)}")

    if len(valid_pairs) == 0:
        logger.info("No valid pairs found. Adjusting parameters...")
        # Relax coverage requirement
        relaxed_coverage = min_coverage * 0.7
        valid_pairs = sim_data[
            (sim_data['score'] >= cluster_threshold * 0.9) & 
            (sim_data['feature_coverage'] >= relaxed_coverage)
        ]
        logger.info(f"Valid pairs with relaxed criteria: {len(valid_pairs)}")

    # Perform clustering with improved method
    df_clusters = clusters(
        sim_data, 
        id_col, 
        cluster_col_name, 
        cluster_threshold, 
        convergence_threshold, 
        col_names, 
        fill_missing, 
        clustering_method=clustering_method,
        min_coverage=min_coverage
    )

    logger.info(f"Generated {df_clusters[cluster_col_name].nunique()} clusters")
    logger.info(f"Records in clusters: {len(df_clusters)}")

    # Apply quality filters
    df_filtered = apply_quality_filters(
        df_clusters, 
        sim_data, 
        id_col, 
        cluster_col_name, 
        min_cluster_size=min_cluster_size,
        min_avg_similarity=cluster_threshold
    )

    logger.info(f"Clusters after quality filtering: {df_filtered[cluster_col_name].nunique()}")
    logger.info(f"Records after quality filtering: {len(df_filtered)}")

    # Only keep clusters with multiple records (remove singletons)
    cluster_counts = df_filtered[cluster_col_name].value_counts()
    multi_record_clusters = cluster_counts[cluster_counts >= min_cluster_size].index
    final_df = df_filtered[df_filtered[cluster_col_name].isin(multi_record_clusters)].copy()

    if len(final_df) == 0:
        logger.info("No clusters found after filtering. Creating empty result.")
        # Create empty DataFrame with correct structure
        final_df = pd.DataFrame(columns=[id_col, cluster_col_name, 'avg_cluster_similarity', 'cluster_size'])
        for col in col_names:
            final_df[col] = []
    else:
        # Replace cluster ids with UUIDs
        unique_cluster_ids = final_df[cluster_col_name].unique()
        cluster_uuid_mapping = {cluster_id: str(uuid.uuid4()) for cluster_id in unique_cluster_ids}
        final_df[cluster_col_name] = final_df[cluster_col_name].map(cluster_uuid_mapping)

        # Merge with original data
        final_df = final_df.merge(dup_data, how='left', on=[id_col]).drop('block_key', axis=1).drop_duplicates()

        # Add range index prefix to cluster IDs
        final_df[cluster_col_name] = str(range_index) + '_' + final_df[cluster_col_name].astype('str')

        # Add quality metrics to output
        logger.info(f"Final output statistics:")
        logger.info(f"- Number of clusters: {final_df[cluster_col_name].nunique()}")
        logger.info(f"- Number of records: {len(final_df)}")
        logger.info(f"- Average cluster size: {final_df['cluster_size'].mean():.1f}")
        logger.info(f"- Average cluster similarity: {final_df['avg_cluster_similarity'].mean():.3f}")
        logger.info(f"- Minimum cluster similarity: {final_df['avg_cluster_similarity'].min():.3f}")

    # Write results
    if paralelism == 'no' and len(final_df) > 0:
        TDConnector.write(final_df, TD_SINK_DATABASE, output_table, TD_API_KEY, TD_API_SERVER)
    elif len(final_df) > 0:
        TDConnector.insert_df(final_df, TD_SINK_DATABASE, output_table, TD_API_KEY, TD_API_SERVER)

    logger.info(f"Processing completed for range index: {range_index}")