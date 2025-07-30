

# Probabilistic ID Unification Clustering - Production Version

import networkx as nx
from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import pandas as pd
import numpy as np
import logging
from collections import defaultdict
from fancyimpute import SoftImpute

logger = logging.getLogger(__name__)

def fill_missing_links(matrix, convergence_threshold=0.01):
    """Fill missing values in adjacency matrix using SoftImpute"""
    matrix_ = matrix.copy()
    
    # Set diagonal to 1 for similarity matrix
    np.fill_diagonal(matrix_, 1)
    
    # Mark missing values (zeros become NaN for imputation)
    mask = (matrix_ == 0) & (~np.eye(len(matrix_), dtype=bool))
    matrix_[mask] = np.nan
    
    # Only proceed with imputation if there are missing values
    if not np.isnan(matrix_).any():
        return matrix_
    
    try:
        imputer = SoftImpute(
            min_value=0, max_value=1, verbose=False, 
            convergence_threshold=convergence_threshold,
            init_fill_method='mean'
        )
        matrix_ = imputer.fit_transform(matrix_)
        
        # Ensure symmetry and diagonal
        matrix_ = (matrix_ + matrix_.T) / 2
        np.fill_diagonal(matrix_, 1.0)
        matrix_ = np.tril(matrix_) + np.triu(matrix_.T, 1)
        
    except Exception as e:
        logger.warning(f"SoftImpute failed, using fallback: {e}")
        # Fallback: use mean imputation
        matrix_[np.isnan(matrix_)] = np.nanmean(matrix_[~np.eye(len(matrix_), dtype=bool)])
        np.fill_diagonal(matrix_, 1.0)
    
    return matrix_

def safe_hierarchical_clustering(data, ROW_ID, threshold):
    """
    Safe clustering method using connected components approach
    """
    # Create graph with only edges above threshold
    graph = nx.Graph()
    
    # Add all nodes first
    all_nodes = set()
    for _, row in data.iterrows():
        all_nodes.add(row[f'{ROW_ID}_1'])
        all_nodes.add(row[f'{ROW_ID}_2'])
    
    graph.add_nodes_from(all_nodes)
    
    # Add edges only for pairs above threshold
    for _, row in data.iterrows():
        if row['score'] >= threshold:
            graph.add_edge(row[f'{ROW_ID}_1'], row[f'{ROW_ID}_2'], score=row['score'])
    
    # Find connected components
    clustering = {}
    cluster_id = 1
    
    for component in nx.connected_components(graph):
        # Split very large components
        if len(component) > 10000:
            component_list = list(component)
            for i in range(0, len(component_list), 5000):
                sub_component = component_list[i:i + 5000]
                for node in sub_component:
                    clustering[node] = cluster_id
                cluster_id += 1
        else:
            for node in component:
                clustering[node] = cluster_id
            cluster_id += 1
    
    return clustering

def hierarchical_clustering_strict(data, ROW_ID, threshold, convergence_threshold, fill_missing):
    """
    Perform hierarchical clustering with strict threshold enforcement
    """
    # Create graph
    graph = nx.Graph()
    
    # Add nodes and edges
    for _, row in data.iterrows():
        graph.add_node(row[f'{ROW_ID}_1'])
        graph.add_node(row[f'{ROW_ID}_2'])
        graph.add_edge(row[f'{ROW_ID}_1'], row[f'{ROW_ID}_2'], score=row['score'])

    # Process connected components
    clustering = {}
    cluster_counter = 0

    for component in nx.connected_components(graph):
        subgraph = graph.subgraph(component)

        if len(subgraph.nodes) > 1:
            # Handle large components with fallback
            if len(subgraph.nodes) > 5000:
                logger.warning(f"Large component ({len(subgraph.nodes)} nodes), using safe method")
                for node in subgraph.nodes():
                    clustering[node] = cluster_counter
                    cluster_counter += 1
                continue
            
            try:
                # Get adjacency matrix
                node_list = list(subgraph.nodes())
                adjacency = nx.to_numpy_array(subgraph, nodelist=node_list, weight='score')
                np.fill_diagonal(adjacency, 1.0)

                # Fill missing values if specified
                if fill_missing:
                    adjacency = fill_missing_links(adjacency, convergence_threshold)
                    np.fill_diagonal(adjacency, 1.0)

                # Apply threshold filtering
                mask = ~np.eye(len(adjacency), dtype=bool)
                adjacency[mask & (adjacency < threshold)] = 0.01

                # Calculate distances
                distances = 1.0 - adjacency
                np.fill_diagonal(distances, 0.0)
                
                # Hierarchical clustering
                condensed_distance = ssd.squareform(distances)
                linkage = hierarchy.linkage(condensed_distance, method='complete')
                distance_threshold = 1 - threshold
                clusters = hierarchy.fcluster(linkage, t=distance_threshold, criterion='distance')
                
            except Exception as e:
                logger.warning(f"Hierarchical clustering failed for component: {e}")
                # Fallback: each node gets its own cluster
                clusters = np.arange(1, len(node_list) + 1)
        else:
            node_list = list(subgraph.nodes())
            clusters = np.array([1])

        # Update clustering dictionary
        clustering.update(dict(zip(node_list, clusters + cluster_counter)))
        cluster_counter += len(set(clusters))

    return clustering

def post_process_clusters(clustering, original_data, ROW_ID, threshold):
    """Post-process clusters for quality assurance"""
    if not clustering:
        return {}, {}
    
    # Create reverse mapping
    cluster_to_records = defaultdict(list)
    for record_id, cluster_id in clustering.items():
        cluster_to_records[cluster_id].append(record_id)
    
    cluster_stats = {}
    valid_clustering = {}
    
    for cluster_id, record_ids in cluster_to_records.items():
        if len(record_ids) == 1:
            valid_clustering[record_ids[0]] = cluster_id
            cluster_stats[cluster_id] = {
                'size': 1, 'avg_similarity': 1.0, 'min_similarity': 1.0
            }
            continue
        
        # Calculate cluster similarities
        similarities = []
        for i, id1 in enumerate(record_ids):
            for id2 in record_ids[i+1:]:
                try:
                    match1 = original_data[
                        (original_data[f'{ROW_ID}_1'] == id1) & 
                        (original_data[f'{ROW_ID}_2'] == id2)
                    ]
                    match2 = original_data[
                        (original_data[f'{ROW_ID}_1'] == id2) & 
                        (original_data[f'{ROW_ID}_2'] == id1)
                    ]
                    
                    if not match1.empty:
                        similarities.append(match1['score'].iloc[0])
                    elif not match2.empty:
                        similarities.append(match2['score'].iloc[0])
                except:
                    continue
        
        if similarities:
            avg_sim = np.mean(similarities)
            min_sim = np.min(similarities)
            
            cluster_stats[cluster_id] = {
                'size': len(record_ids),
                'avg_similarity': avg_sim,
                'min_similarity': min_sim
            }
            
            # Quality check: keep cluster if meets criteria
            if avg_sim >= threshold and min_sim >= threshold * 0.8:
                for record_id in record_ids:
                    valid_clustering[record_id] = cluster_id
            else:
                # Split cluster
                max_cluster = max(cluster_to_records.keys()) if cluster_to_records else 0
                for i, record_id in enumerate(record_ids):
                    valid_clustering[record_id] = max_cluster + i + 1
        else:
            # No similarity data, split cluster
            max_cluster = max(cluster_to_records.keys()) if cluster_to_records else 0
            for i, record_id in enumerate(record_ids):
                valid_clustering[record_id] = max_cluster + i + 1
    
    return valid_clustering, cluster_stats

def clusters(data, ROW_ID, DEDUPLICATION_ID_NAME, cluster_threshold, convergence_threshold, 
             col_names, fill_missing, clustering_method='safe', min_coverage=0.5):
    """
    Main clustering function with fallback mechanisms
    """
    logger.info(f"Starting clustering with method '{clustering_method}', threshold {cluster_threshold}")
    
    try:
        # Filter valid data
        valid_data = data[
            (data['score'] >= cluster_threshold) & 
            (data.get('feature_coverage', 1.0) >= min_coverage)
        ].copy()
        
        if valid_data.empty:
            logger.warning("No valid pairs found, creating singleton clusters")
            # Create singleton clusters
            all_records = set()
            for col in [f'{ROW_ID}_1', f'{ROW_ID}_2']:
                if col in data.columns:
                    all_records.update(data[col].unique())
            
            clustering = {record: i for i, record in enumerate(all_records, 1)}
        else:
            # Try clustering with fallback
            clustering_methods = [clustering_method, 'safe', 'connected_components']
            clustering = None
            
            for method in clustering_methods:
                try:
                    if method in ['connected_components', 'safe']:
                        clustering = safe_hierarchical_clustering(valid_data, ROW_ID, cluster_threshold)
                    elif method == 'strict_hierarchical':
                        clustering = hierarchical_clustering_strict(
                            valid_data, ROW_ID, cluster_threshold, convergence_threshold, fill_missing
                        )
                    
                    if clustering:
                        logger.info(f"Clustering successful with method: {method}")
                        break
                        
                except Exception as e:
                    logger.warning(f"Clustering method '{method}' failed: {e}")
                    continue
            
            if not clustering:
                raise Exception("All clustering methods failed")
        
        # Post-process clusters
        try:
            final_clustering, cluster_stats = post_process_clusters(
                clustering, data, ROW_ID, cluster_threshold
            )
        except Exception as e:
            logger.warning(f"Post-processing failed: {e}")
            final_clustering = clustering
        
        # Create result DataFrame
        if not final_clustering:
            return pd.DataFrame(columns=[ROW_ID, DEDUPLICATION_ID_NAME, 'avg_cluster_similarity'])
        
        df_clusters = pd.DataFrame.from_dict(
            final_clustering, orient='index', columns=[DEDUPLICATION_ID_NAME]
        )
        df_clusters.sort_values(DEDUPLICATION_ID_NAME, inplace=True)
        df_clusters[ROW_ID] = df_clusters.index
        df_clusters = df_clusters.reset_index(drop=True)
        
        # Calculate cluster similarities
        cluster_similarities = {}
        for cluster_id in df_clusters[DEDUPLICATION_ID_NAME].unique():
            cluster_records = df_clusters[
                df_clusters[DEDUPLICATION_ID_NAME] == cluster_id
            ][ROW_ID].tolist()
            
            if len(cluster_records) == 1:
                cluster_similarities[cluster_id] = 1.0
            else:
                similarities = []
                for i, id1 in enumerate(cluster_records):
                    for id2 in cluster_records[i+1:]:
                        try:
                            match1 = data[
                                (data[f'{ROW_ID}_1'] == id1) & (data[f'{ROW_ID}_2'] == id2)
                            ]
                            match2 = data[
                                (data[f'{ROW_ID}_1'] == id2) & (data[f'{ROW_ID}_2'] == id1)
                            ]
                            
                            if not match1.empty:
                                similarities.append(match1['score'].iloc[0])
                            elif not match2.empty:
                                similarities.append(match2['score'].iloc[0])
                        except:
                            continue
                
                cluster_similarities[cluster_id] = np.mean(similarities) if similarities else cluster_threshold
        
        df_clusters['avg_cluster_similarity'] = df_clusters[DEDUPLICATION_ID_NAME].map(cluster_similarities)
        
        logger.info(f"Clustering completed: {df_clusters[DEDUPLICATION_ID_NAME].nunique()} clusters, {len(df_clusters)} records")
        return df_clusters
        
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        return pd.DataFrame(columns=[ROW_ID, DEDUPLICATION_ID_NAME, 'avg_cluster_similarity'])

